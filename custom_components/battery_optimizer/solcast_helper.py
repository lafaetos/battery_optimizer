import logging
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

def get_solcast_data_with_type(hass: HomeAssistant, today_entity_id: str, tomorrow_entity_id: str, threshold: float = 0.6):
    now = datetime.now()
    current_hour = now.hour
    
    solar_evening_end = 19 
    if current_hour >= solar_evening_end:
        active_entity_id = tomorrow_entity_id
        source_type = "tomorrow"
    else:
        active_entity_id = today_entity_id
        source_type = "today"

    if not active_entity_id:
        active_entity_id = today_entity_id or tomorrow_entity_id
        source_type = "today"

    state = hass.states.get(active_entity_id)
    if not state or state.state in ("unknown", "unavailable"):
        fallback_id = today_entity_id if active_entity_id == tomorrow_entity_id else tomorrow_entity_id
        if fallback_id:
            state = hass.states.get(fallback_id)
            source_type = "today" if fallback_id == today_entity_id else "tomorrow"

    if not state or state.state in ("unknown", "unavailable"):
        return 5.0, 8, 18, None, "unknown"

    forecast = 5.0
    try:
        forecast = float(state.state)
    except ValueError:
        pass

    solar_start, solar_end = _parse_detailed_forecast(state, threshold)
    if solar_start is None or solar_end is None:
        return forecast, 8, 18, state, source_type

    return forecast, solar_start, solar_end, state, source_type

def _parse_detailed_forecast(solcast_state, threshold=0.6):
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
        
        if period_start is not None and pv_estimate >= threshold:
            try:
                if isinstance(period_start, datetime):
                    dt_local = dt_util.as_local(period_start)
                else:
                    dt = datetime.fromisoformat(str(period_start))
                    dt_local = dt_util.as_local(dt)
                valid_hours.append(dt_local.hour)
            except Exception:
                continue
                
    if not valid_hours:
        return None, None

    return min(valid_hours), max(valid_hours) + 1
