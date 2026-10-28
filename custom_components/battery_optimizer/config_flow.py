import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

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
    MODE_MAX_SOLAR,
    MODE_THRESHOLD_AUTO,
    MODE_THRESHOLD_CUSTOM,
)

class BatteryOptimizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Battery Optimizer", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_CONSUMPTION_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_SOLCAST_TODAY_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_SOLCAST_TOMORROW_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Optional(CONF_BATTERY_SOC_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_BATTERY_CAPACITY, default=15.0): vol.Coerce(float),
            vol.Required(CONF_MIN_SOC, default=20): vol.Coerce(int),
            vol.Required(CONF_SOC_OFFSET, default=0): vol.Coerce(int),
            vol.Required(CONF_MODE, default=MODE_MAX_CHARGE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[MODE_MAX_CHARGE, MODE_MAX_SOLAR],
                    translation_key="mode"
                )
            ),
            vol.Required(CONF_HISTORY_DAYS, default=14): vol.Coerce(int),
            vol.Required(CONF_NIGHT_START, default="23:00"): str,
            vol.Required(CONF_NIGHT_END, default="05:00"): str,
            vol.Required(CONF_SOLAR_THRESHOLD_MODE, default=MODE_THRESHOLD_AUTO): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[MODE_THRESHOLD_AUTO, MODE_THRESHOLD_CUSTOM],
                    translation_key="threshold_mode"
                )
            ),
            vol.Optional(CONF_SOLAR_THRESHOLD_CUSTOM, default=5.0): vol.Coerce(float),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BatteryOptimizerOptionsFlow()


class BatteryOptimizerOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        data = self.config_entry.data

        get_val = lambda key, default: options.get(key, data.get(key, default))

        schema = vol.Schema({
            vol.Required(
                CONF_CONSUMPTION_SENSOR, 
                default=get_val(CONF_CONSUMPTION_SENSOR, "")
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                CONF_SOLCAST_TODAY_SENSOR, 
                default=get_val(CONF_SOLCAST_TODAY_SENSOR, "")
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                CONF_SOLCAST_TOMORROW_SENSOR, 
                default=get_val(CONF_SOLCAST_TOMORROW_SENSOR, "")
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Optional(
                CONF_BATTERY_SOC_SENSOR, 
                default=get_val(CONF_BATTERY_SOC_SENSOR, "")
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                CONF_BATTERY_CAPACITY, 
                default=get_val(CONF_BATTERY_CAPACITY, 15.0)
            ): vol.Coerce(float),
            vol.Required(
                CONF_MIN_SOC, 
                default=get_val(CONF_MIN_SOC, 20)
            ): vol.Coerce(int),
            vol.Required(
                CONF_SOC_OFFSET, 
                default=get_val(CONF_SOC_OFFSET, 0)
            ): vol.Coerce(int),
            vol.Required(
                CONF_MODE, 
                default=get_val(CONF_MODE, MODE_MAX_CHARGE)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[MODE_MAX_CHARGE, MODE_MAX_SOLAR],
                    translation_key="mode"
                )
            ),
            vol.Required(
                CONF_HISTORY_DAYS, 
                default=get_val(CONF_HISTORY_DAYS, 14)
            ): vol.Coerce(int),
            vol.Required(
                CONF_NIGHT_START, 
                default=get_val(CONF_NIGHT_START, "23:00")
            ): str,
            vol.Required(
                CONF_NIGHT_END, 
                default=get_val(CONF_NIGHT_END, "05:00")
            ): str,
            vol.Required(
                CONF_SOLAR_THRESHOLD_MODE, 
                default=get_val(CONF_SOLAR_THRESHOLD_MODE, MODE_THRESHOLD_AUTO)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[MODE_THRESHOLD_AUTO, MODE_THRESHOLD_CUSTOM],
                    translation_key="threshold_mode"
                )
            ),
            vol.Optional(
                CONF_SOLAR_THRESHOLD_CUSTOM, 
                default=get_val(CONF_SOLAR_THRESHOLD_CUSTOM, 5.0)
            ): vol.Coerce(float),
        })

        return self.async_show_form(step_id="init", data_schema=schema)
