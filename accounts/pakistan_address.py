"""
Pakistan delivery validation: province, city whitelist, and postal-code prefix alignment.
Coarse but practical for e-commerce — rejects obvious mismatches (e.g. Lahore + KPK).
"""
from __future__ import annotations

# Stored DB / form values (English labels)
PROVINCE_CHOICES: tuple[tuple[str, str], ...] = (
    ("Punjab", "Punjab"),
    ("Sindh", "Sindh"),
    ("KPK", "Khyber Pakhtunkhwa"),
    ("Balochistan", "Balochistan"),
    ("Islamabad", "Islamabad Capital Territory"),
    ("Gilgit-Baltistan", "Gilgit-Baltistan"),
    ("AJK", "Azad Jammu & Kashmir"),
)

# Major cities per province (Title Case as shown to user)
CITIES_BY_PROVINCE: dict[str, tuple[str, ...]] = {
    "Punjab": (
        "Lahore",
        "Rawalpindi",
        "Faisalabad",
        "Multan",
        "Gujranwala",
        "Sialkot",
        "Sargodha",
        "Bahawalpur",
        "Jhang",
        "Sheikhupura",
        "Gujrat",
        "Kasur",
        "Rahim Yar Khan",
        "Sahiwal",
        "Okara",
        "Wah Cantonment",
        "Dera Ghazi Khan",
        "Mianwali",
        "Narowal",
        "Chiniot",
        "Kamoke",
        "Hafizabad",
        "Mandi Bahauddin",
        "Pakpattan",
        "Chishtian",
        "Jhelum",
        "Attock",
    ),
    "Sindh": (
        "Karachi",
        "Hyderabad",
        "Sukkur",
        "Larkana",
        "Nawabshah",
        "Mirpur Khas",
        "Jacobabad",
        "Shikarpur",
        "Khairpur",
        "Dadu",
        "Thatta",
        "Badin",
        "Umerkot",
        "Tando Adam",
        "Tando Allahyar",
    ),
    "KPK": (
        "Peshawar",
        "Mardan",
        "Abbottabad",
        "Swabi",
        "Charsadda",
        "Kohat",
        "Haripur",
        "Mansehra",
        "Swat",
        "Dera Ismail Khan",
        "Bannu",
        "Nowshera",
        "Battagram",
        "Timergara",
        "Mingora",
        "Hangu",
        "Tank",
    ),
    "Balochistan": (
        "Quetta",
        "Turbat",
        "Khuzdar",
        "Chaman",
        "Hub",
        "Sibi",
        "Gwadar",
        "Zhob",
        "Usta Muhammad",
        "Loralai",
        "Dera Murad Jamali",
    ),
    "Islamabad": ("Islamabad",),
    "Gilgit-Baltistan": (
        "Gilgit",
        "Skardu",
        "Hunza",
        "Chilas",
        "Ghizer",
        "Ghanche",
    ),
    "AJK": (
        "Muzaffarabad",
        "Mirpur",
        "Kotli",
        "Rawalakot",
        "Bagh",
        "Bhimber",
        "Hattian Bala",
        "Neelum",
    ),
}

# First two digits of 5-digit Pakistan postal codes commonly associated with each province
# (approximate; sufficient to catch Lahore-style codes under wrong province)
POSTAL_PREFIX_BY_PROVINCE: dict[str, frozenset[str]] = {
    "Punjab": frozenset(
        f"{i:02d}" for i in range(50, 62)
    ),  # 50–61
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
    """Return field_name -> error message (empty dict if valid)."""
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

    if province in CITIES_BY_PROVINCE and city_norm not in CITIES_BY_PROVINCE[province]:
        errors["city"] = (
            f"The city “{city_norm}” is not listed under {province}. "
            "Choose the province where you actually receive deliveries."
        )

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

    blob = f"{city_norm} {street}".lower()
    if "lahore" in blob and province != "Punjab":
        errors["__all__"] = "Lahore is in Punjab — province, city, postal code, and street must all describe the same location."
    if "karachi" in blob and province != "Sindh":
        errors.setdefault(
            "__all__",
            "Karachi is in Sindh — please align province and address.",
        )
    if "peshawar" in blob and province != "KPK":
        errors.setdefault(
            "__all__",
            "Peshawar is in Khyber Pakhtunkhwa — please align province and address.",
        )

    return errors
