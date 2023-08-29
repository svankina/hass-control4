"""Platform for Control4 Blinds."""
from __future__ import annotations

import logging

from pyControl4.blind import C4Blind

from homeassistant.components.cover import CoverEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import Control4Entity, get_items_of_category
from .const import CONF_DIRECTOR, CONTROL4_ENTITY_TYPE, DOMAIN
from .director_utils import director_get_entry_variables

_LOGGER = logging.getLogger(__name__)

CONTROL4_CATEGORY = "blinds_shades"

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Control4 blinds from a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]

    items_of_category = await get_items_of_category(hass, entry, CONTROL4_CATEGORY)

    entity_list = []

    for item in items_of_category:
        try:
            if item["type"] == CONTROL4_ENTITY_TYPE and item["id"]:
                item_name = str(item["name"])
                item_id = item["id"]
                item_area = item["roomName"]
                item_parent_id = item["parentId"]

                item_manufacturer = None
                item_device_name = None
                item_model = None

                for parent_item in items_of_category:
                    if parent_item["id"] == item_parent_id:
                        item_manufacturer = parent_item["manufacturer"]
                        item_device_name = parent_item["name"]
                        item_model = parent_item["model"]
            else:
                continue
        except KeyError:
            _LOGGER.exception(
                "Unknown device properties received from Control4: %s",
                item,
            )
            continue

        item_attributes = await director_get_entry_variables(hass, entry, item_id)

        entity_list.append(
            Control4Cover(
                entry_data,
                entry,
                item_name,
                item_id,
                item_device_name,
                item_manufacturer,
                item_model,
                item_parent_id,
                item_area,
                item_attributes,
            )

        )
    async_add_entities(entity_list, True)

class Control4Cover(Control4Entity, CoverEntity):
    """Control4 cover entity."""

    def __init__(self,)

    def create_api_object(self):
        """Create a pyControl4 device object.

        This exists so the director token used is always the latest one, without needing to re-init the entire entity.
        """
        return C4Blind(self.entry_data[CONF_DIRECTOR], self._idx)

    @property
    def is_closed(self):
        """Return whether the cover is open or closed."""
        #TODO: Implement this properly.
        return True

    async def async_open_cover(self, **kwargs) -> None:
        """Open the cover"""
        c4_cover = self.create_api_object()
        await c4_cover.open()
        await self.async_update_ha_state()

    async def async_close(self, **kwargs) -> None:
        """Close the cover"""
        c4_cover = self.create_api_object()
        await c4_cover.close()
        await self.async_update_ha_state()
