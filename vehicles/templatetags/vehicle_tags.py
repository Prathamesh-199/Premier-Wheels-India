from django import template


register = template.Library()


@register.filter
def indian_number(value):
    """Format an integer using the Indian comma system."""

    try:
        number = int(value)
    except (TypeError, ValueError):
        return value

    text = str(number)

    if len(text) <= 3:
        return text

    last_three = text[-3:]
    remaining = text[:-3]
    groups = []

    while len(remaining) > 2:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    if remaining:
        groups.insert(0, remaining)

    return ",".join(groups + [last_three])


@register.filter
def indian_currency(value):
    """Format an integer as Indian Rupees."""

    return f"₹{indian_number(value)}"
