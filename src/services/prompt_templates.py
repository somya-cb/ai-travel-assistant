# prompt_templates.py

def build_itinerary_prompt(persona, destination, dates, hotel=None, weather=None, special_requirements=None):
    hotel_info = ""
    if hotel:
        hotel_name = hotel.get('name', 'Selected hotel')
        hotel_address = hotel.get('address', '')
        hotel_info = f"- 🏨 Hotel: {hotel_name}{f', {hotel_address}' if hotel_address else ''}"
    
    weather_info = f"- 🌤️ Expected Weather: {weather}" if weather else ""
    requirements_info = f"- ⚠️ Special Requirements: {', '.join(special_requirements)}" if special_requirements else ""
    
    activities = persona.get('activities', []) or ['general sightseeing']
    activities_str = ', '.join(activities)
    companions = persona.get('companions', []) or ['solo travel']
    companions_str = ', '.join(companions)
    
    days_count = dates.get('days', 1)
    if days_count <= 2:
        duration_context = "Focus on must-see highlights and key experiences."
    elif days_count <= 5:
        duration_context = "Balance popular attractions with local experiences."
    else:
        duration_context = "Include both tourist highlights and off-the-beaten-path discoveries."
    
    return f"""You are an expert travel planner. Create a personalized, practical itinerary that balances must-see attractions with authentic local experiences.

TRAVELER PROFILE:
- Travel Style: {persona.get("travel_style", "balanced").title()}
- Budget Level: {persona.get("budget", "mid-range").title()}
- Preferred Activities: {activities_str}
- Travel Group: {companions_str}
- Mobility/Dietary Restrictions: {', '.join(special_requirements) if special_requirements else 'None specified'}

TRIP CONTEXT:
- Destination: {destination.get("city", "Unknown City")}, {destination.get("country", "Unknown Country")}
- Duration: {dates.get('start', 'TBD')} to {dates.get('end', 'TBD')} ({days_count} days)
{hotel_info}
{weather_info}
{requirements_info}

PLANNING GUIDANCE: {duration_context}

RESPONSE REQUIREMENTS:
✅ Use **Markdown formatting only**
✅ Include specific venue names, addresses when possible
✅ Provide estimated costs for budget-conscious travelers
✅ Suggest transportation between locations
✅ Include backup indoor options for weather contingencies
✅ Mention local customs/etiquette tips where relevant
❌ Do NOT include any title, trip snapshot, or summary section
❌ No meta-commentary or placeholder text

FORMAT TEMPLATE:

## 🗓️ Daily Itinerary

### Day 1: [Descriptive Day Theme]
**🌅 Morning (9:00 AM - 12:00 PM)**
- **Activity**: [Specific venue/experience]
- **Location**: [Address or area]
- **Cost**: [Estimated price range]
- **Why**: [Brief reason this fits their profile]

**☀️ Afternoon (12:00 PM - 5:00 PM)**
- **Lunch**: [Restaurant recommendation with cuisine type]
- **Activity**: [Main afternoon experience]
- **Transport**: [How to get there]

**🌆 Evening (5:00 PM - 9:00 PM)**
- **Activity**: [Evening experience]
- **Dining**: [Dinner suggestion]
- **Local Tip**: [Cultural insight or practical advice]

### Day 2: [Next day theme]
[Continue same detailed format...]

## 💡 Pro Tips
- **Getting Around**: [Local transportation advice]
- **Money Matters**: [Currency, tipping, payment methods]
- **Cultural Notes**: [Key etiquette or customs]
- **Weather Backup**: [Indoor alternatives if weather turns]
- **Local Phrases**: [2-3 useful phrases in local language]

## 📱 Essential Info
- **Emergency Numbers**: [Local emergency contacts]
- **WiFi**: [Where to find internet access]
- **Pharmacy/Medical**: [Nearest healthcare options]""".strip()
