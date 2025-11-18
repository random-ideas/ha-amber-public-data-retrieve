"""API client for Amber Energy."""
import logging
from typing import Any

import requests

from .const import API_BASE_URL, API_ORIGIN, DEFAULT_PAST_HOURS

_LOGGER = logging.getLogger(__name__)


class AmberEnergyAPI:
    """API client for Amber Energy pricing data."""

    def __init__(self, postcode: str, past_hours: int | None = None) -> None:
        """Initialize the API client."""
        self.postcode = postcode
        self.past_hours = past_hours or DEFAULT_PAST_HOURS

    def get_prices(self) -> dict[str, Any]:
        """Fetch price data from Amber API."""
        url = f"{API_BASE_URL}/postcode/{self.postcode}/prices"
        params = {"past-hours": self.past_hours}
        headers = {"origin": API_ORIGIN}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching Amber Energy data: %s", err)
            raise
