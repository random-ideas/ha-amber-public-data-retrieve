"""Config flow for Amber Energy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_POSTCODE, CONF_PAST_HOURS, DEFAULT_PAST_HOURS
from .api import AmberEnergyAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_POSTCODE): str,
        vol.Optional(CONF_PAST_HOURS, default=DEFAULT_PAST_HOURS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=24)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = AmberEnergyAPI(
        data[CONF_POSTCODE], data.get(CONF_PAST_HOURS, DEFAULT_PAST_HOURS)
    )

    try:
        result = await hass.async_add_executor_job(api.get_prices)
    except Exception as err:
        _LOGGER.error("Error connecting to Amber API: %s", err)
        raise CannotConnect from err

    if not result or "postcode" not in result:
        raise InvalidPostcode

    return {"title": f"Amber Energy - {data[CONF_POSTCODE]}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Amber Energy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidPostcode:
                errors["base"] = "invalid_postcode"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_POSTCODE])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidPostcode(HomeAssistantError):
    """Error to indicate the postcode is invalid."""
