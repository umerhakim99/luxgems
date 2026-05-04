from decimal import Decimal, InvalidOperation

from django import template
register = template.Library()


@register.filter
def pkr(value):
    """Format amount as Pakistani Rupees (whole rupees, comma separators)."""
    if value is None or value == "":
        return "—"
    try:
        v = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return str(value)
    whole = int(v.quantize(Decimal("1")))
    return f"Rs. {whole:,}"


@register.inclusion_tag("catalog/includes/star_rating.html")
def star_rating(avg, count=None):
    try:
        a = float(avg)
    except (TypeError, ValueError):
        a = 0.0
    a = max(0.0, min(5.0, a))
    full = int(a)
    half = 1 if (a - full) >= 0.499 else 0
    empty = max(0, 5 - full - half)
    return {
        "full_range": range(full),
        "half": half,
        "empty_range": range(empty),
        "avg": round(a, 1),
        "count": count,
    }
