# itinerary_builder.py

from datetime import datetime
import logging
import re

from services.prompt_templates import build_itinerary_prompt
from services.bedrock_service import call_llama4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────
# Utility Functions
# ────────────────────────────────────────────────
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit safely."""
    try:
        return (celsius * 9 / 5) + 32
    except (TypeError, ValueError):
        return celsius


def month_range(start: datetime, end: datetime) -> list[int]:
    """Get a list of month numbers (as ints) between two dates inclusive."""
    months = set()
    current = start.replace(day=1)
    while current <= end:
        months.add(current.month)
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    return sorted(months)


# ────────────────────────────────────────────────
# Temperature Information
# ────────────────────────────────────────────────
def get_temperature_info(destination: dict, start_date: str, end_date: str) -> str:
    """Extract and calculate temperature information for the travel period."""
    try:
        logger.debug("Getting temperature info for %s (%s → %s)",
                     destination.get("city", "Unknown"), start_date, end_date)

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            logger.warning("Date parsing error: %s", e)
            return "Temperature data not available (invalid date format)"

        temp_data = destination.get("avg_temp_monthly", {})
        if not temp_data:
            return "Temperature data not available"

        months = month_range(start, end)
        totals = {"avg": 0, "max": 0, "min": 0}
        valid_months = 0

        for m in months:
            data = temp_data.get(str(m))
            if data:
                totals["avg"] += data.get("avg", 0)
                totals["max"] += data.get("max", 0)
                totals["min"] += data.get("min", 0)
                valid_months += 1

        if not valid_months:
            return "Temperature data not available for travel dates"

        avg_c, max_c, min_c = [totals[k] / valid_months for k in ("avg", "max", "min")]
        avg_f, max_f, min_f = map(celsius_to_fahrenheit, (avg_c, max_c, min_c))

        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        if len(months) == 1:
            month_label = month_names[months[0]]
        else:
            month_label = f"{month_names[months[0]]}–{month_names[months[-1]]}"

        return (f"Weather ({month_label}): "
                f"Avg {avg_f:.0f}°F ({avg_c:.0f}°C), "
                f"High {max_f:.0f}°F ({max_c:.0f}°C), "
                f"Low {min_f:.0f}°F ({min_c:.0f}°C)")

    except Exception as e:
        logger.error("Error calculating temperature: %s", e)
        return "Temperature data unavailable"


# ────────────────────────────────────────────────
# Itinerary Generation
# ────────────────────────────────────────────────
def generate_itinerary(persona: dict, destination: dict, dates: dict, hotel: dict = None) -> str:
    if not destination.get("city") or not dates.get("start"):
        return "Error: Missing required information"
    
    # Weather info 
    weather_info = get_temperature_info(destination, dates["start"], dates["end"])
    
    # Build LLM prompt
    prompt = build_itinerary_prompt(persona, destination, dates, hotel, weather_info)
    response = call_llama4(prompt)
    if not response:
        return "Error: Could not generate itinerary"

    # Extract details
    city = destination.get("city", "Unknown")
    country = destination.get("country", "")
    days = dates.get("days", "?")

    # ---- Trip summary ----
    summary = f"""# Your {days}-Day Trip to {city}, {country}

- 👤 Traveler: {persona.get('user_id', 'Guest')}
- 🏨 Hotel: {hotel.get('name') if hotel else "Not selected"}
- 📅 Dates: {dates.get('start')} → {dates.get('end')}
- 🌤️ {weather_info}
"""

    # ---- Combine summary + LLM itinerary ----
    return f"""{summary}

{response}"""


