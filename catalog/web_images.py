"""
Royalty-free image URLs (HTTPS) for the storefront.
Unsplash: https://unsplash.com/license  |  Pexels: https://www.pexels.com/license/
"""

# Home hero (full-bleed + editorial strip)
HERO_MAIN = (
    "https://images.unsplash.com/photo-1758995115437-7547c7e6500d"
    "?auto=format&fit=crop&w=1920&q=82"
)
HERO_EDITORIAL = (
    "https://images.unsplash.com/photo-1603561591411-07134e71a2a9"
    "?auto=format&fit=crop&w=1600&q=82"
)

# Per demo product slug — used by seed_demo and optional admin defaults
# Extra gallery shots per slug (HTTPS; mix of Unsplash/Pexels jewellery)
_U1 = "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=900&q=82"
_U2 = "https://images.unsplash.com/photo-1535632066927-ab7c9ab0b602?auto=format&fit=crop&w=900&q=82"
_U3 = "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=900&q=82"
_P1 = "https://images.pexels.com/photos/1018137/pexels-photo-1018137.jpeg?auto=compress&cs=tinysrgb&w=900"
_P2 = "https://images.pexels.com/photos/1454175/pexels-photo-1454175.jpeg?auto=compress&cs=tinysrgb&w=900"
_P3 = "https://images.pexels.com/photos/248077/pexels-photo-248077.jpeg?auto=compress&cs=tinysrgb&w=900"
_U4 = "https://images.unsplash.com/photo-1632816307542-6a707d8a1c3c?auto=format&fit=crop&w=900&q=82"
_U5 = "https://images.unsplash.com/photo-1724937721110-862ebf74ed7a?auto=format&fit=crop&w=900&q=82"

DEMO_PRODUCT_GALLERY_URLS: dict[str, list[str]] = {
    "diamond-necklace": [_U2, _P2, _U4, _U3],
    "sapphire-ring": [_U1, _P3, _U5, _P1],
    "gemstone-bracelet": [_U4, _P1, _U2, _U3],
    "diamond-earrings": [_U5, _P2, _U1, _U3],
    "statement-necklace": [_U3, _P1, _U2, _P3],
    "emerald-ring": [_P3, _U4, _P2, _U5],
}

DEMO_PRODUCT_IMAGE_URLS = {
    "diamond-necklace": (
        "https://images.pexels.com/photos/1018137/pexels-photo-1018137.jpeg"
        "?auto=compress&cs=tinysrgb&w=1200"
    ),
    "sapphire-ring": (
        "https://images.pexels.com/photos/1454175/pexels-photo-1454175.jpeg"
        "?auto=compress&cs=tinysrgb&w=1200"
    ),
    "gemstone-bracelet": (
        "https://images.unsplash.com/photo-1632816307542-6a707d8a1c3c"
        "?auto=format&fit=crop&w=1200&q=82"
    ),
    "diamond-earrings": (
        "https://images.unsplash.com/photo-1724937721110-862ebf74ed7a"
        "?auto=format&fit=crop&w=1200&q=82"
    ),
    "statement-necklace": (
        "https://images.unsplash.com/photo-1771626965799-a6ec8b44aede"
        "?auto=format&fit=crop&w=1200&q=82"
    ),
    "emerald-ring": (
        "https://images.pexels.com/photos/248077/pexels-photo-248077.jpeg"
        "?auto=compress&cs=tinysrgb&w=1200"
    ),
}

IMAGE_ATTRIBUTION = (
    "Hero & product photos: Unsplash and Pexels (free licenses). "
    "See static/img/IMAGE_CREDITS.txt for links."
)
