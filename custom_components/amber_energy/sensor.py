"""Sensor platform for Amber Energy integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_CENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Amber Energy sensors."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # General usage sensors
    entities.append(AmberCurrentPriceSensor(coordinator, entry, "general"))
    entities.append(AmberNextPriceSensor(coordinator, entry, "general"))
    entities.append(AmberRenewablesSensor(coordinator, entry, "general"))
    entities.append(AmberDescriptorSensor(coordinator, entry, "general"))

    # Feed-in sensors
    entities.append(AmberCurrentPriceSensor(coordinator, entry, "feedin"))
    entities.append(AmberNextPriceSensor(coordinator, entry, "feedin"))
    entities.append(AmberRenewablesSensor(coordinator, entry, "feedin"))
    entities.append(AmberDescriptorSensor(coordinator, entry, "feedin"))

    async_add_entities(entities)


class AmberBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Amber Energy sensors."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        price_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._price_type = price_type
        self._postcode: str = entry.data["postcode"]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and bool(self._get_intervals())

    def _get_intervals(self) -> list[dict[str, Any]] | None:
        """Get the intervals for the price type."""
        if not self.coordinator.data:
            return None

        if self._price_type == "general":
            price_data = self.coordinator.data.get("priceData", [])
        else:
            price_data = self.coordinator.data.get("feedInPriceData", [])

        if price_data and len(price_data) > 0:
            return price_data[0].get("intervals", [])

        return None

    def _get_current_interval(self) -> dict[str, Any] | None:
        """Get the most recent interval."""
        intervals = self._get_intervals()
        if intervals:
            # API usually returns in chronological order; last = most recent
            return intervals[-1]
        return None

    def _get_next_interval(self) -> dict[str, Any] | None:
        """Get the next interval if available."""
        intervals = self._get_intervals()
        if intervals and len(intervals) > 1:
            # Second last is "next" relative to most recent
            return intervals[-2]
        return None


class AmberCurrentPriceSensor(AmberBaseSensor):
    """Sensor for current Amber Energy price."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        price_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, price_type)
        type_label = "Feed-In" if price_type == "feedin" else "General Usage"
        self._attr_name = f"Amber {type_label} Current Price"
        self._attr_unique_id = f"{entry.entry_id}_{price_type}_current_price"
        self._attr_native_unit_of_measurement = f"{CURRENCY_CENT}/kWh"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_icon = "mdi:currency-usd"

    @property
    def native_value(self) -> float | None:
        """Return the current price."""
        interval = self._get_current_interval()
        if interval:
            return round(interval.get("perKwh", 0), 2)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        interval = self._get_current_interval()
        if interval:
            return {
                "nem_time": interval.get("nemTime"),
                "descriptor": interval.get("descriptor"),
                "renewables": interval.get("renewables"),
                "postcode": self._postcode,
            }
        return {}


class AmberNextPriceSensor(AmberBaseSensor):
    """Sensor for next Amber Energy price."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        price_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, price_type)
        type_label = "Feed-In" if price_type == "feedin" else "General Usage"
        self._attr_name = f"Amber {type_label} Next Price"
        self._attr_unique_id = f"{entry.entry_id}_{price_type}_next_price"
        self._attr_native_unit_of_measurement = f"{CURRENCY_CENT}/kWh"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_icon = "mdi:currency-usd-clock"

    @property
    def native_value(self) -> float | None:
        """Return the next price."""
        interval = self._get_next_interval()
        if interval:
            return round(interval.get("perKwh", 0), 2)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        interval = self._get_next_interval()
        if interval:
            return {
                "nem_time": interval.get("nemTime"),
                "descriptor": interval.get("descriptor"),
                "renewables": interval.get("renewables"),
                "postcode": self._postcode,
            }
        return {}


class AmberRenewablesSensor(AmberBaseSensor):
    """Sensor for current renewables percentage."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        price_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, price_type)
        type_label = "Feed-In" if price_type == "feedin" else "General Usage"
        self._attr_name = f"Amber {type_label} Renewables"
        self._attr_unique_id = f"{entry.entry_id}_{price_type}_renewables"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:leaf"

    @property
    def native_value(self) -> float | None:
        """Return the renewables percentage."""
        interval = self._get_current_interval()
        if interval:
            return round(interval.get("renewables", 0), 2)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        interval = self._get_current_interval()
        if interval:
            return {
                "nem_time": interval.get("nemTime"),
                "postcode": self._postcode,
            }
        return {}


class AmberDescriptorSensor(AmberBaseSensor):
    """Sensor for current price descriptor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        price_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, price_type)
        type_label = "Feed-In" if price_type == "feedin" else "General Usage"
        self._attr_name = f"Amber {type_label} Descriptor"
        self._attr_unique_id = f"{entry.entry_id}_{price_type}_descriptor"
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str | None:
        """Return the price descriptor."""
        interval = self._get_current_interval()
        if interval:
            return interval.get("descriptor")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        interval = self._get_current_interval()
        if interval:
            return {
                "nem_time": interval.get("nemTime"),
                "price_per_kwh": interval.get("perKwh"),
                "postcode": self._postcode,
            }
        return {}
