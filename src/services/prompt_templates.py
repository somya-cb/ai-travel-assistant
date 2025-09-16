# prompt_templates.py

def build_itinerary_prompt(persona, destination, dates, hotel=None, weather=None, special_requirements=None):
    hotel_info = ""
    if hotel:
        hotel_name = hotel.get('name', 'Selected hotel')
        hotel_address = hotel.get('address', '')
        hotel_info = f"- 🏨 Hotel: {hotel_name}{f', {hotel_address}' if hotel_address else ''}"
    
    # Weather context if available
    weather_info = ""
    if weather:
        weather_info = f"- 🌤️ Expected Weather: {weather}"
    
    # Special requirements handling
    requirements_info = ""
    if special_requirements:
        requirements_info = f"- ⚠️ Special Requirements: {', '.join(special_requirements)}"
    
    # Enhanced activity formatting with fallbacks
    activities = persona.get('activities', [])
    activities_str = ', '.join(activities) if activities else 'general sightseeing'
    
    companions = persona.get('companions', [])
    companions_str = ', '.join(companions) if companions else 'solo travel'
    
    # Calculate trip duration 
    days_count = dates.get('days', 1)
    duration_context = ""
    if days_count <= 2:
        duration_context = "Focus on must-see highlights and key experiences."
    elif days_count <= 5:
        duration_context = "Balance popular attractions with local experiences."
    else:
        duration_context = "Include both tourist highlights and off-the-beaten-path discoveries."

    return f"""You are an expert travel planner with deep local knowledge. Create a personalized, practical itinerary that balances must-see attractions with authentic local experiences.

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
❌ No meta-commentary or planning process explanations
❌ No generic placeholder text

FORMAT TEMPLATE:

# 🌍 {destination.get("city", "Your Destination")} Adventure

## 📋 Trip Snapshot
- 📅 **Dates**: {dates.get('start', 'TBD')} to {dates.get('end', 'TBD')} ({days_count} days)
- 📍 **Destination**: {destination.get("city", "City")}, {destination.get("country", "Country")}
- 🏨 **Accommodation**: {hotel.get('name', 'To be selected') if hotel else 'To be selected'}
- 💰 **Budget**: {persona.get("budget", "mid-range").title()}
- 🎯 **Focus**: {persona.get("travel_style", "balanced").title()} travel

---

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
- **Pharmacy/Medical**: [Nearest healthcare options]

Generate a comprehensive, actionable itinerary that feels personally crafted for this traveler's interests and constraints.""".strip()

# Alternative version for shorter trips (1-3 days)
def build_short_itinerary_prompt(persona, destination, dates, hotel=None):
    return f"""You are a local expert creating a focused itinerary for a short trip. Prioritize must-do experiences and efficient routing.

TRAVELER: {persona.get("travel_style", "efficient").title()} style, {persona.get("budget", "mid-range")} budget
TRIP: {destination.get("city")}, {destination.get("country")} | {dates.get('days', 1)} days
INTERESTS: {', '.join(persona.get('activities', ['highlights']))}

Create a **streamlined itinerary** focusing on:
- Top 3-5 must-see attractions
- 1-2 authentic local experiences  
- Efficient routing to maximize time
- Specific timing and logistics

Use the same markdown format as above but condensed for quick trip planning."""