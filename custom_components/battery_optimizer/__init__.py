import logging
from datetime import datetime, timedelta, time
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_CONSUMPTION_SENSOR,
    CONF_SOLCAST_TODAY_SENSOR,
    CONF_SOLCAST_TOMORROW_SENSOR,
    CONF_BATTERY_SOC_SENSOR,
    CONF_BATTERY_CAPACITY,
    CONF_MIN_SOC,
    CONF_SOC_OFFSET,
    CONF_MODE,
    CONF_HISTORY_DAYS,
    CONF_NIGHT_START,
    CONF_NIGHT_END,
    CONF_SOLAR_THRESHOLD_MODE,
    CONF_SOLAR_THRESHOLD_CUSTOM,
    MODE_MAX_CHARGE,
    MODE_THRESHOLD_AUTO,
)
from .solcast_helper import get_solcast_data_with_type

_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("=== BATTERY OPTIMIZER COMPONENT IS STARTING UP ===")

STORAGE_KEY = f"{DOMAIN}_history"
STORAGE_KEY_TMP = f"{DOMAIN}_tmp"
STORAGE_VERSION = 1

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = BatteryOptimizerCoordinator(hass, entry)
    await coordinator.async_load_history()
    
    await coordinator.async_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

class BatteryOptimizerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.store_tmp = Store(hass, STORAGE_VERSION, STORAGE_KEY_TMP)
        
        self.hourly_history_workday = [0.5] * 24
        self.hourly_history_weekend = [0.5] * 24
        
        self._hourly_start_values = {}
        self._last_checked_hour = None
        
        self.target_soc = 20.0
        self.required_kwh = 0.0
        self.day_consumption = 0.0
        self.morning_consumption = 0.0
        
        self.workday_morning_consumption = 0.0
        self.workday_day_consumption = 0.0
        self.weekend_morning_consumption = 0.0
        self.weekend_day_consumption = 0.0
        self.solcast_source_type = "today"
        self.solar_threshold_value = 0.5

        self.night_start = "23:00"
        self.night_end = "05:00"
        self.solar_start = "08:00"
        self.solar_end = "18:00"
        self.forecast_surplus = 0.0
        self.realtime_surplus = 0.0

        self.soc_at_solar_end = 0.0
        self._last_tracked_date = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=4),
        )

    async def async_load_history(self):
        try:
            data = await self.store.async_load()
            if data:
                if "workday" in data and isinstance(data["workday"], list) and len(data["workday"]) == 24:
                    self.hourly_history_workday = data["workday"]
                if "weekend" in data and isinstance(data["weekend"], list) and len(data["weekend"]) == 24:
                    self.hourly_history_weekend = data["weekend"]
                
                # Відновлюємо soc_at_solar_end та дату з основного сховища історії
                self.soc_at_solar_end = data.get("soc_at_solar_end", 0.0)
                saved_date_str = data.get("last_tracked_date")
                if saved_date_str:
                    try:
                        self._last_tracked_date = datetime.fromisoformat(saved_date_str).date()
                    except Exception:
                        pass

                _LOGGER.info(f"Successfully loaded history and soc_at_solar_end ({self.soc_at_solar_end}%) from storage.")
            else:
                await self.async_save_history()

            tmp_data = await self.store_tmp.async_load()
            if tmp_data:
                saved_hour = tmp_data.get("last_checked_hour")
                saved_start_values = tmp_data.get("hourly_start_values", {})
                current_hour = datetime.now().hour

                if saved_hour == current_hour:
                    self._last_checked_hour = saved_hour
                    self._hourly_start_values = {int(k): v for k, v in saved_start_values.items()}
                    _LOGGER.info(f"Restored temporary hourly start values for hour {saved_hour} from _tmp storage.")
        except Exception as e:
            _LOGGER.error(f"Failed to load history or temporary data: {e}")

    async def async_save_history(self):
        try:
            await self.store.async_save({
                "workday": self.hourly_history_workday,
                "weekend": self.hourly_history_weekend,
                "soc_at_solar_end": self.soc_at_solar_end,
                "last_tracked_date": self._last_tracked_date.isoformat() if self._last_tracked_date else None,
            })
        except Exception as e:
            _LOGGER.error(f"Failed to save consumption history: {e}")

    async def async_save_tmp_data(self):
        try:
            await self.store_tmp.async_save({
                "last_checked_hour": self._last_checked_hour,
                "hourly_start_values": self._hourly_start_values,
            })
        except Exception as e:
            _LOGGER.error(f"Failed to save temporary data: {e}")

    def _get_config(self, key, default):
        if self.entry.options and key in self.entry.options:
            return self.entry.options[key]
        return self.entry.data.get(key, default)

    async def _async_update_data(self):
        _LOGGER.info("Coordinator update triggered!")
        await self._update_hourly_consumption()
        self._calculate_optimizer_data()
        return {
            "target_soc": self.target_soc,
            "required_kwh": self.required_kwh,
            "day_consumption": self.day_consumption,
            "morning_consumption": self.morning_consumption,
            "soc_at_solar_end": self.soc_at_solar_end,
        }

    async def _update_hourly_consumption(self):
        now = datetime.now()
        current_hour = now.hour

        sensor_id = self._get_config(CONF_CONSUMPTION_SENSOR, None)
        if not sensor_id:
            return

        state = self.hass.states.get(sensor_id)
        if not state or state.state in ("unknown", "unavailable"):
            return

        try:
            current_val = float(state.state)
        except ValueError:
            return

        if self._last_checked_hour is None:
            self._last_checked_hour = current_hour
            self._hourly_start_values[current_hour] = current_val
            await self.async_save_tmp_data()
            return

        if self._last_checked_hour != current_hour:
            target_hour = self._last_checked_hour
            target_is_weekend = (now - timedelta(hours=1)).weekday() >= 5
            start_val = self._hourly_start_values.get(target_hour)

            if start_val is not None and current_val >= start_val:
                delta_kwh = current_val - start_val
                history_days = self._get_config(CONF_HISTORY_DAYS, 14)
                alpha = max(0.05, 2.0 / (history_days + 1))

                if 0 <= delta_kwh < 50.0:
                    active_history = self.hourly_history_weekend if target_is_weekend else self.hourly_history_workday
                    old_val = active_history[target_hour]
                    new_val = round((1 - alpha) * old_val + alpha * delta_kwh, 3)
                    active_history[target_hour] = new_val
                    await self.async_save_history()

            self._hourly_start_values[current_hour] = current_val
            self._last_checked_hour = current_hour
            await self.async_save_tmp_data()

    def _parse_time(self, time_str, default_hour):
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except (ValueError, TypeError):
            return time(default_hour, 0)

    def _calculate_optimizer_data(self):
        capacity = self._get_config(CONF_BATTERY_CAPACITY, 15.0)
        min_soc = self._get_config(CONF_MIN_SOC, 20)
        soc_offset = self._get_config(CONF_SOC_OFFSET, 0)
        mode = self._get_config(CONF_MODE, MODE_MAX_CHARGE)
        
        self.night_start = self._get_config(CONF_NIGHT_START, "23:00")
        self.night_end = self._get_config(CONF_NIGHT_END, "05:00")
        night_end_time = self._parse_time(self.night_end, 5)
        night_end_hour = night_end_time.hour

        solcast_today_entity = self._get_config(CONF_SOLCAST_TODAY_SENSOR, None)
        solcast_tomorrow_entity = self._get_config(CONF_SOLCAST_TOMORROW_SENSOR, None)
        battery_soc_entity = self._get_config(CONF_BATTERY_SOC_SENSOR, None)

        now = datetime.now()
        is_today_weekend = now.weekday() >= 5
        active_history = self.hourly_history_weekend if is_today_weekend else self.hourly_history_workday

        # Розрахунок сонячного порогу (авто: добова сума / 24, або ручне значення)
        threshold_mode = self._get_config(CONF_SOLAR_THRESHOLD_MODE, MODE_THRESHOLD_AUTO)
        if threshold_mode == MODE_THRESHOLD_AUTO:
            daily_total = sum(active_history)
            self.solar_threshold_value = round(daily_total / 24.0, 2)
            hourly_threshold = self.solar_threshold_value
        else:
            self.solar_threshold_value = self._get_config(CONF_SOLAR_THRESHOLD_CUSTOM, 0.5)
            hourly_threshold = self.solar_threshold_value

        # Отримуємо прогноз з урахуванням ефективного сонячного порогу
        solcast_forecast, solar_start_h, solar_end_h, solcast_state, source_type = get_solcast_data_with_type(
            self.hass, solcast_today_entity, solcast_tomorrow_entity, threshold=hourly_threshold
        )
        self.solcast_source_type = source_type

        self.solar_start = f"{solar_start_h:02d}:00"
        self.solar_end = f"{solar_end_h:02d}:00"

        night_end_h = max(0, min(23, night_end_hour))
        solar_start_h = max(0, min(24, solar_start_h))
        solar_end_h = max(solar_start_h, min(24, solar_end_h))
        morning_start_h = min(night_end_h, solar_start_h)

        self.workday_morning_consumption = round(sum(self.hourly_history_workday[morning_start_h:solar_start_h]), 2)
        self.workday_day_consumption = round(sum(self.hourly_history_workday[solar_start_h:solar_end_h]), 2)
        self.weekend_morning_consumption = round(sum(self.hourly_history_weekend[morning_start_h:solar_start_h]), 2)
        self.weekend_day_consumption = round(sum(self.hourly_history_weekend[solar_start_h:solar_end_h]), 2)

        self.morning_consumption = round(sum(active_history[morning_start_h:solar_start_h]), 2)
        self.day_consumption = round(sum(active_history[solar_start_h:solar_end_h]), 2)

        if mode == MODE_MAX_CHARGE:
            needed_kwh = capacity - (solcast_forecast - self.day_consumption) + self.morning_consumption
            target = (needed_kwh / capacity) * 100.0
        else:
            needed_kwh = self.morning_consumption + (capacity * (min_soc / 100.0))
            target = (needed_kwh / capacity) * 100.0

        target += soc_offset
        self.target_soc = max(min_soc, min(100.0, round(target, 1)))
        self.required_kwh = round((self.target_soc / 100.0) * capacity, 2)

        total_day_consumption = sum(active_history)
        surplus = solcast_forecast - (total_day_consumption + (capacity - (capacity * (min_soc / 100.0))))
        self.forecast_surplus = round(max(0.0, surplus), 2)

        # Фіксація SoC на закінчення сонячного дня
        if mode == MODE_MAX_CHARGE and battery_soc_entity:
            current_date = now.date()
            if now.hour == solar_end_h and self._last_tracked_date != current_date:
                soc_state = self.hass.states.get(battery_soc_entity)
                if soc_state and soc_state.state not in ("unknown", "unavailable"):
                    try:
                        self.soc_at_solar_end = float(soc_state.state)
                        self._last_tracked_date = current_date
                        _LOGGER.info(f"Captured battery SoC at solar end ({solar_end_h}:00): {self.soc_at_solar_end}%")
                        self.hass.async_create_task(self.async_save_history())
                    except ValueError:
                        pass
