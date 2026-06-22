def format_currency(value: float, currency: str = "EUR") -> str:
    """Format float into currency string natively."""
    symbols = {"EUR": "€", "USD": "$", "GBP": "£", "AED": "د.إ"}
    sym = symbols.get(currency, currency)
    return f"{sym}{value:,.2f}"

def render_badge(text: str, badge_type: str = "primary") -> str:
    """Render an HTML badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'
