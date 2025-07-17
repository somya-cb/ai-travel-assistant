# AI Travel Assistant - Architecture Overview

## Project Overview
A personalized travel recommendation system that uses AI to suggest destinations and create detailed itineraries based on user preferences.

## Core Components

### 1. Frontend (Streamlit)
- **main.py** - Single-page web application
- User authentication (email-based)
- Travel profile onboarding
- Chat interface for recommendations
- Session state management

### 2. Data Storage (Couchbase)
**Two Collections:**
- `user_profiles` - User accounts and travel personas
- `destinations` - Travel destinations with vector embeddings

**Document Types:**
- `user_record` - Authentication and metadata
- `travel_persona` - User preferences and travel style
- `destination` - City data with embeddings for search

### 3. AI Services
- **Amazon Bedrock** - Large language model for itinerary generation
- **Vector Search** - Similarity matching for destination recommendations
- **Embedding Generation** - Convert destination descriptions to vectors

### 4. Business Logic
- **RecommendationService** - Handles destination search and matching
- **ConversationHandler** - Manages recommendation flow state
- **SimpleTravelPersona** - User preference data model

### 5. Data Source
- **CSV File** - `Worldwide Travel Cities Dataset Ratings and Climate.csv`
- Contains destination details, ratings, and travel metadata

## Data Flow

### User Journey
1. **Login** → Email/name → User record creation/retrieval
2. **Onboarding** → Travel questionnaire → Persona creation
3. **Chat** → Recommendation request → Vector search → AI-enhanced response
4. **Itinerary** → Destination selection → Detailed planning via Bedrock

### Recommendation Flow
1. User: "Recommend places for May"
2. System: Ask clarifying questions (duration, preferences)
3. Vector search on destination embeddings
4. Bedrock enhances with personalized itineraries
5. Display formatted recommendations

## Technical Architecture

### Service Dependencies
- **Couchbase** - Document storage and vector search
- **AWS Bedrock** - AI model inference
- **Streamlit** - Web framework
- **Python Libraries** - Data processing and embeddings

### Integration Points
- CSV data loaded into Couchbase destinations collection
- User profiles stored as travel personas
- Real-time vector search for recommendations
- Bedrock API calls for itinerary generation

## Files Structure
```
app/
├── main.py                           # Main Streamlit app
├── src/
│   ├── models/
│   │   └── simple_persona.py         # User preference model
│   └── services/
│       ├── couchbase_service.py      # Database operations
│       ├── bedrock_service.py        # AI model integration
│       ├── recommendation_service.py # Destination search
│       └── conversation_handler.py   # Chat flow management
└── data/
    └── Worldwide Travel Cities Dataset.csv   # Destination data
