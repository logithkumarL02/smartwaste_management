import logging
from functools import lru_cache
from .base import SortingDevice
from .simulator import SimulationSortingDevice

log = logging.getLogger(__name__)

SUPPORTED_MODES = {
    "simulation": SimulationSortingDevice,
    # Future: "raspberry_pi": RaspberryPiSortingDevice, "esp32": ESP32SortingDevice
}

@lru_cache(maxsize=1)
def get_sorting_device(mode: str = "simulation") -> SortingDevice:
    device_class = SUPPORTED_MODES.get(mode.lower())
    if device_class is None:
        log.warning(f"Unknown HARDWARE_MODE '{mode}'. Falling back to simulation.")
        device_class = SimulationSortingDevice
    device = device_class()
    log.info(f"Hardware mode: {device.get_mode()} ({device_class.__name__})")
    return device
