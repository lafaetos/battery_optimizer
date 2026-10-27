from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TargetSoCSensor(coordinator),
        RequiredEnergySensor(coordinator),
        NightStartSensor(coordinator),
        NightEndSensor(coordinator),
        SolarStartSensor(coordinator),
        SolarEndSensor(coordinator),
        ForecastSurplusSensor(coordinator),
        RealtimeSurplusSensor(coordinator),
	DayConsumptionSensor(coordinator),
        MorningConsumptionSensor(coordinator),
	BatterySocAtSolarEndSensor(coordinator),
    ])

class BatterySocAtSolarEndSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Battery SoC at Solar End"
        self._attr_unique_id = "battery_optimizer_soc_at_solar_end"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:battery-arrow-down"

    @property
    def native_value(self):
        return getattr(self.coordinator, "soc_at_solar_end", 0.0)


class TargetSoCSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Target Battery SoC Night"
        self._attr_unique_id = "target_battery_soc_night"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:battery-charging-100"

    @property
    def native_value(self):
        return self.coordinator.target_soc

class RequiredEnergySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Target Battery Energy Night"
        self._attr_unique_id = "target_battery_energy_night"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_icon = "mdi:lightning-bolt"

    @property
    def native_value(self):
        return self.coordinator.required_kwh

class NightStartSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Night Tariff Start Time"
        self._attr_unique_id = "battery_optimizer_night_start"
        self._attr_icon = "mdi:clock-start"

    @property
    def native_value(self):
        return self.coordinator.night_start

class NightEndSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Night Tariff End Time"
        self._attr_unique_id = "battery_optimizer_night_end"
        self._attr_icon = "mdi:clock-end"

    @property
    def native_value(self):
        return self.coordinator.night_end

class SolarStartSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Solar Generation Start"
        self._attr_unique_id = "battery_optimizer_solar_start"
        self._attr_icon = "mdi:weather-sunny"

    @property
    def native_value(self):
        return self.coordinator.solar_start

class SolarEndSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Solar Generation End"
        self._attr_unique_id = "battery_optimizer_solar_end"
        self._attr_icon = "mdi:weather-sunset"

    @property
    def native_value(self):
        return self.coordinator.solar_end

class ForecastSurplusSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Forecasted Energy Surplus"
        self._attr_unique_id = "battery_optimizer_forecast_surplus"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_icon = "mdi:solar-power"

    @property
    def native_value(self):
        return self.coordinator.forecast_surplus

class RealtimeSurplusSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Realtime Energy Surplus"
        self._attr_unique_id = "battery_optimizer_realtime_surplus"
        self._attr_native_unit_of_measurement = "kW"
        self._attr_icon = "mdi:flash-alert"

    @property
    def native_value(self):
        return self.coordinator.realtime_surplus

class DayConsumptionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Day Consumption Forecast"
        self._attr_unique_id = "battery_optimizer_day_consumption"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_icon = "mdi:chart-line"

    @property
    def native_value(self):
        return getattr(self.coordinator, "day_consumption", 0.0)

class MorningConsumptionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Morning Consumption Forecast"
        self._attr_unique_id = "battery_optimizer_morning_consumption"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_icon = "mdi:weather-sunset-up"

    @property
    def native_value(self):
        return getattr(self.coordinator, "morning_consumption", 0.0)
