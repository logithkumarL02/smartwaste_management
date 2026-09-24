import logging
from typing import Tuple
from .base import SortingDevice

log = logging.getLogger(__name__)

COMMAND_VISUALS = {
    "SORT_PLASTIC":  "🔵 [BIN 1 - PLASTIC]   → Opening gate A",
    "SORT_METAL":    "⚫ [BIN 2 - METAL]     → Activating magnet conveyor",
    "SORT_GLASS":    "🟢 [BIN 3 - GLASS]     → Lowering soft-drop chute",
    "SORT_PAPER":    "🟡 [BIN 4 - PAPER]     → Activating paper belt",
    "SORT_ORGANIC":  "🌿 [BIN 5 - ORGANIC]   → Opening compost gate",
    "SORT_EWASTE":   "🔴 [BIN 6 - E-WASTE]   → Isolated e-waste container",
    "SORT_TEXTILE":  "🟣 [BIN 7 - TEXTILE]   → Textile collection arm",
    "SORT_OTHER":    "⬜ [BIN 8 - GENERAL]   → General waste conveyor",
    "MANUAL_REVIEW": "⚠️  [MANUAL REVIEW]     → Flagging for human inspection",
}

class SimulationSortingDevice(SortingDevice):
    def sort(self, command: str) -> Tuple[bool, str]:
        visual = COMMAND_VISUALS.get(command, f"❓ Unknown command: {command}")
        log.info(f"[SIMULATOR] {visual}")
        if command not in COMMAND_VISUALS:
            return False, f"Unknown command: {command}"
        category_name = command.replace("SORT_", "").replace("_", " ").title()
        return True, f"{category_name} sorting action simulated successfully."

    def get_mode(self) -> str:
        return "simulation"

    def is_available(self) -> bool:
        return True
