"""Centralized waste category configuration - single source of truth."""
from typing import Dict, Any

WASTE_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "plastic": {
        "id": "plastic", "name": "Plastic",
        "description": "Synthetic polymer-based materials that are lightweight and durable.",
        "examples": ["water bottles", "food containers", "bags", "straws", "packaging"],
        "recommendation": "Clean and rinse plastic items before recycling. Check the recycling symbol (1-7) on the bottom. Types 1 (PET) and 2 (HDPE) are most widely accepted.",
        "disposal_method": "Plastic recycling stream",
        "hardware_command": "SORT_PLASTIC",
        "color": "#3B82F6", "icon": "bottle",
    },
    "metal": {
        "id": "metal", "name": "Metal",
        "description": "Ferrous and non-ferrous metallic materials including cans and foils.",
        "examples": ["aluminium cans", "tin cans", "scrap metal", "foil", "bottle caps"],
        "recommendation": "Rinse metal cans thoroughly. Aluminium and steel are 100% recyclable and can be recycled indefinitely.",
        "disposal_method": "Metal recycling stream",
        "hardware_command": "SORT_METAL",
        "color": "#6B7280", "icon": "can",
    },
    "glass": {
        "id": "glass", "name": "Glass",
        "description": "Silica-based transparent or translucent containers and materials.",
        "examples": ["glass bottles", "jars", "broken glass", "drinking glasses"],
        "recommendation": "Rinse glass containers before recycling. Never mix window glass, mirrors, or Pyrex with container glass.",
        "disposal_method": "Glass recycling bank or kerbside collection",
        "hardware_command": "SORT_GLASS",
        "color": "#10B981", "icon": "glass",
    },
    "paper_cardboard": {
        "id": "paper_cardboard", "name": "Paper & Cardboard",
        "description": "Cellulose-based paper products and cardboard packaging.",
        "examples": ["newspapers", "cardboard boxes", "office paper", "magazines"],
        "recommendation": "Keep paper and cardboard dry. Flatten boxes to save space. Remove plastic tape and bubble wrap.",
        "disposal_method": "Paper & cardboard recycling stream",
        "hardware_command": "SORT_PAPER",
        "color": "#F59E0B", "icon": "newspaper",
    },
    "organic": {
        "id": "organic", "name": "Organic / Food Waste",
        "description": "Biodegradable food scraps and garden waste.",
        "examples": ["fruit peels", "vegetable scraps", "food leftovers", "garden waste"],
        "recommendation": "Compost organic waste at home or use a green bin/food waste collection.",
        "disposal_method": "Compost or organic waste bin",
        "hardware_command": "SORT_ORGANIC",
        "color": "#84CC16", "icon": "leaf",
    },
    "e_waste": {
        "id": "e_waste", "name": "E-Waste / Electronics",
        "description": "Discarded electronic and electrical equipment.",
        "examples": ["batteries", "phones", "cables", "PCBs", "laptops", "light bulbs"],
        "recommendation": "NEVER put e-waste in general waste. Take to a certified e-waste collection point.",
        "disposal_method": "Certified e-waste collection point",
        "hardware_command": "SORT_EWASTE",
        "color": "#EF4444", "icon": "cpu",
    },
    "textile": {
        "id": "textile", "name": "Textile / Clothing",
        "description": "Fabric-based items including clothing, shoes, and linens.",
        "examples": ["clothes", "shoes", "bags", "curtains", "bed linen"],
        "recommendation": "Donate wearable clothes to charity shops. Never put textiles in general recycling.",
        "disposal_method": "Charity shop, clothing bank, or textile recycling",
        "hardware_command": "SORT_TEXTILE",
        "color": "#8B5CF6", "icon": "shirt",
    },
    "other": {
        "id": "other", "name": "General Waste",
        "description": "Items that do not fit other categories and cannot be easily recycled.",
        "examples": ["nappies", "crisp packets", "polystyrene", "contaminated packaging"],
        "recommendation": "General waste goes to landfill or energy-from-waste. Minimise this category by checking if items can be reused or recycled.",
        "disposal_method": "General waste / residual waste bin",
        "hardware_command": "SORT_OTHER",
        "color": "#9CA3AF", "icon": "trash",
    },
}

CATEGORY_IDS = list(WASTE_CATEGORIES.keys())

def get_category(category_id: str) -> Dict[str, Any]:
    return WASTE_CATEGORIES.get(category_id, WASTE_CATEGORIES["other"])

def get_hardware_command(category_id: str) -> str:
    return get_category(category_id)["hardware_command"]

def get_recommendation(category_id: str) -> str:
    return get_category(category_id)["recommendation"]

def get_display_name(category_id: str) -> str:
    return get_category(category_id)["name"]

def list_categories() -> list:
    return list(WASTE_CATEGORIES.values())
