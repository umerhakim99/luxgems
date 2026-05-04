"""
Pakistan delivery validation: province and postal-code prefix alignment.
City is now free text — no whitelist validation.
"""
from __future__ import annotations

PROVINCE_CHOICES: tuple[tuple[str, str], ...] = (
    ("Punjab", "Punjab"),
    ("Sindh", "Sindh"),
    ("KPK", "Khyber Pakhtunkhwa"),
    ("Balochistan", "Balochistan"),
    ("Islamabad", "Islamabad Capital Territory"),
    ("Gilgit-Baltistan", "Gilgit-Baltistan"),
    ("AJK", "Azad Jammu & Kashmir"),
)

CITIES_BY_PROVINCE: dict[str, tuple[str, ...]] = {}

POSTAL_PREFIX_BY_PROVINCE: dict[str, frozenset[str]] = {
    "Punjab": frozenset(f"{i:02d}" for i in range(50, 62)),
    "Sindh": frozenset(f"{i:02d}" for i in range(65, 76)),
    "KPK": frozenset(f"{i:02d}" for i in range(21, 28)),
    "Balochistan": frozenset(f"{i:02d}" for i in range(80, 87)),
    "Islamabad": frozenset(["44"]),
    "Gilgit-Baltistan": frozenset(["15", "16"]),
    "AJK": frozenset(["12", "13", "14"]),
}


def normalize_city(city: str) -> str:
    return " ".join((city or "").strip().title().split())


def validate_pakistan_address(
    *,
    province: str,
    city: str,
    postal_code: str,
    street_address: str = "",
) -> dict[str, str]:
    errors: dict[str, str] = {}
    province = (province or "").strip()
    city_norm = normalize_city(city)
    postal = (postal_code or "").strip().replace(" ", "")
    street = (street_address or "").strip()

    if not street or len(street) < 8:
        errors["street_address"] = "Please enter a complete street address (building, road, area)."

    valid_provinces = {c[0] for c in PROVINCE_CHOICES}
    if province not in valid_provinces:
        errors["province"] = "Select a valid province or territory."

    if not city_norm:
        errors["city"] = "Please enter your city name."

    if len(postal) != 5 or not postal.isdigit():
        errors["postal_code"] = "Pakistan postal codes are exactly 5 digits (e.g. 54000 for Lahore)."
    elif province in POSTAL_PREFIX_BY_PROVINCE:
        prefix = postal[:2]
        allowed = POSTAL_PREFIX_BY_PROVINCE[province]
        if prefix not in allowed:
            errors["postal_code"] = (
                f"The postal code {postal} does not match the selected province ({province}). "
                "Use the postal code for the same area as your address."
            )

    return errors