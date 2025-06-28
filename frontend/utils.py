"""
Utility functions for formatting and data processing
"""

def format_volume(volume):
    """Format volume numbers for display"""
    if volume >= 1_000_000:
        return f"${volume/1_000_000:.1f}M"
    elif volume >= 1_000:
        return f"${volume/1_000:.1f}K"
    else:
        return f"${volume:.0f}"

def format_price(price):
    """Format price as percentage"""
    if price is None:
        return "N/A"
    return f"{price*100:.1f}¢"

def get_platform_icon(platform):
    """Get icon for platform"""
    return "🟣" if platform == "Polymarket" else "🔵"

def get_trend_icon(yes_price):
    """Get trend icon based on yes price"""
    return "📈" if yes_price > 0.5 else "📉" if yes_price < 0.5 else "➡️"

def format_end_date(end_date):
    """Format end date for display"""
    from datetime import datetime
    
    if end_date and end_date != 'Unknown':
        try:
            parsed_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            return parsed_date.strftime('%m/%d')
        except:
            return "?"
    else:
        return "?"
