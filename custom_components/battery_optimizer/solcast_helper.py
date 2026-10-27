import logging
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

def get_solcast_data(hass: HomeAssistant, today_entity_id: str, tomorrow_entity_id: str):
    now = datetime.now()
    
    # Вибираємо сенсор: вночі/вранці беремо завтра, якщо сьогодні ще не заповнене, або навпаки
    active_entity_id = tomorrow_entity_id if now.hour >= 18 or now.hour < 6 else today_entity_id
    
    state = hass.states.get(active_entity_id)
    if not state or state.state in ("unknown", "unavailable"):
        # Фалбек на інший сенсор, якщо основний недоступний
        fallback_id = today_entity_id if active_entity_id == tomorrow_entity_id else tomorrow_entity_id
        state = hass.states.get(fallback_id)
        if not state or state.state in ("unknown", "unavailable"):
            return 5.0, 8, 18, None
        active_entity_id = fallback_id

    forecast = 5.0
    try:
        forecast = float(state.state)
    except ValueError:
        pass

    solar_start, solar_end = _parse_detailed_forecast(state)
    
    if solar_start is None or solar_end is None:
        return forecast, 8, 18, state

    return forecast, solar_start, solar_end, state

def _parse_detailed_forecast(solcast_state):
    if not solcast_state.attributes:
        return None, None

    attrs = solcast_state.attributes
    detailed_data = (
        attrs.get("detailedForecast") or 
        attrs.get("DetailedForecast") or 
        attrs.get("detailedHourly") or 
        attrs.get("DetailedHourly", [])
    )
    
    if not detailed_data:
        return None, None

    valid_hours = []

    for entry in detailed_data:
        period_start = entry.get("period_start")
        pv_estimate = entry.get("pv_estimate", 0.0)
        
        if period_start is not None and pv_estimate >= 0.2:
            try:
                # Якщо Solcast вже передав готовий datetime об'єкт
                if isinstance(period_start, datetime):
                    dt_local = dt_util.as_local(period_start)
                else:
                    # Якщо це все ж таки рядок
                    dt = datetime.fromisoformat(str(period_start))
                    dt_local = dt_util.as_local(dt)
                
                valid_hours.append(dt_local.hour)
            except Exception as e:
                _LOGGER.error(f"Error parsing period_start {period_start}: {e}")
                continue
                
    if not valid_hours:
        return None, None

    start_hour = min(valid_hours)
    end_hour = max(valid_hours) + 1
    
    _LOGGER.info(f"SUCCESS: Calculated solar hours from {solcast_state.entity_id} -> Start: {start_hour}, End: {end_hour}")
    return start_hour, end_hour
