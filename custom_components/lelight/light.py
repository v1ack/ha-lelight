"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA, ATTR_COLOR_TEMP, ATTR_COLOR_MODE,
                                            COLOR_MODES_BRIGHTNESS, COLOR_MODE_COLOR_TEMP,
                                            LightEntity)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .connector import App
from .encoder import Commands

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
})


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]

    add_entities([AwesomeLight(host, App(host))])

    # Setup connection with devices/cloud
    # hub = awesomelights.Hub(host, username, password)
    #
    # # Verify that passed in configuration works
    # if not hub.is_valid_login():
    #     _LOGGER.error("Could not connect to AwesomeLight hub")
    #     return
    #
    # # Add devices
    # add_entities(AwesomeLight(light) for light in hub.lights())


def normalize_value(value: int, max: int, new_max: int) -> int:
    """Normalize value to new range."""
    return int(value * new_max / max)


class AwesomeLight(LightEntity):
    """Representation of an Awesome Light."""
    min_mireds = 3000
    max_mireds = 6400
    supported_color_modes = {COLOR_MODES_BRIGHTNESS, COLOR_MODE_COLOR_TEMP}

    def __init__(self, host: str, light: App) -> None:
        """Initialize an AwesomeLight."""
        self._host = host
        self._light = light
        self._name = f"Light {host}"
        self._state = False
        self._brightness = 255
        self._temp = 4700

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return normalize_value(self._brightness, 1000, 255)

    @property
    def color_temp(self) -> int | None:
        """Return the color temperature."""
        return self._temp

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.send(Commands.turn_on())
        self._brightness = normalize_value(kwargs.get(ATTR_BRIGHTNESS, 255), 255, 1000)
        self._temp = kwargs.get(ATTR_COLOR_TEMP, 4700)
        self._light.send(Commands.bright(self._brightness))
        self._light.send(Commands.temp(self._temp))

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._light.send(Commands.turn_off())

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        pass
