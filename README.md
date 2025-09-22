# AI Travel Assistant

## Overview

The **AI Travel Assistant** is an interactive travel planning application that helps users discover personalized destinations, browse hotels, and generate complete itineraries based on their preferences. It combines AI-driven recommendations with structured user inputs for a guided, step-by-step planning experience.

The app leverages:

* **Streamlit** for the frontend interface
* **Couchbase** for storing user profiles, destinations, hotels, and itineraries
* **AWS Bedrock** (via `bedrock_service.py`) for AI-powered recommendations and itinerary generation

---

## Features

* **Persona-Based Recommendations**: Build personalized travel profiles and get AI-driven suggestions

* **Flexible Trip Planning**: Choose between two modes:

  * **Filter-Based Search**: Uses Couchbase hybrid search to match destinations based on user-selected filters
  * **Surprise Me**: Uses Couchbase vector search for AI-powered recommendations without specific filters

* **Destination Discovery**: Recommended destinations displayed as interactive cards

* **Travel Date & Duration Handling**: Plan trips by specifying start and end dates

* **Hotel Browsing & Selection**: Optional hotel search and detailed views integrated with destination selection

* **Itinerary Generation**: AI-driven itineraries based on persona, destination, dates, and hotels

* **Persistence**: Save itineraries to Couchbase for future access

* **Session-Based Multi-Step Flow**: Stepwise travel planning using Streamlit’s session state

---

## Project Structure

```
ai-travel-assistant/
│
├─ app/
│  └─ main.py                   # Streamlit app entry point
│
├─ src/services/
│  ├─ __init__.py
│  ├─ bedrock_service.py        # Interfaces with AWS Bedrock for AI generation
│  ├─ config.py                 # Load app and Couchbase configuration
│  ├─ couchbase_connection.py   # Couchbase connection setup
│  ├─ couchbase_service.py      # DB operations: destinations, hotels, itineraries
│  ├─ persona_handler.py        # Load/create user personas
│  ├─ trip_input_handler.py     # Trip mode selection and filter handling
│  ├─ recommendation_service.py # Generates AI recommendations
│  ├─ destination_card.py       # Display destination cards
│  ├─ hotel_service.py          # Hotel search & formatting
│  ├─ hotel_cards.py            # Hotel cards & detailed views
│  ├─ itinerary_builder.py      # Itinerary generation logic
│  ├─ process_documents.py      # Preprocess and vectorize destination and hotel documents
│  └─ prompt_templates.py       # LLM prompt templates for recommendations
│
├─ config.template.json         # Template config with placeholders
├─ requirements.txt             # Python dependencies
└─ README.md
```

---

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/somya-cb/ai-travel-assistant.git
cd ai-travel-assistant
```

2. **Create a Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

---

## Configuration

1. **Copy the Template**

```bash
cp config.template.json config.json
```

2. **Edit `config.json`**

Fill in your credentials and connection details:

* Couchbase: host, username, password, bucket, collections
* AWS Bedrock or other AI service keys

The app reads this file at runtime to connect to the database and AI services.

---

## Running the App

```bash
streamlit run app/main.py
```

Open `http://localhost:8501` in your browser.

---

## Usage Flow

1. **Persona Setup**: Define user preferences and profile
2. **Trip Mode Selection**: Choose between two planning modes:

   * **Filter-Based Search**: Matches destinations using Couchbase hybrid search based on user-selected filters
   * **Surprise Me**: Generates recommendations using Couchbase vector search without requiring filters
3. **Destination Selection**: AI-powered recommendations displayed as cards
4. **Travel Dates**: Pick start and end dates for the trip
5. **Hotel Selection (Optional)**: Browse hotels for the chosen destination
6. **Itinerary Generation**: AI creates a complete travel itinerary
7. **Save Itinerary**: Persist in Couchbase for later use
8. **Plan Another Trip**: Reset session to start a new trip

