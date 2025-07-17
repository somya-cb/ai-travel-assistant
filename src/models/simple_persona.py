
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class SimpleTravelPersona:
    """Simplified travel persona for MVP"""
    
    # Basic Info
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    
    # Core Preferences (from onboarding)
    traveler_types: List[str] = field(default_factory=list)  # max 3
    budget_style: str = ""  # budget_conscious, mid_range, luxury
    accommodation_style: List[str] = field(default_factory=list)
    travel_companions: str = ""  # solo, couple, family, friends
    activity_preferences: List[str] = field(default_factory=list)  # max 5
    
    # Practical Info
    dietary_restrictions: List[str] = field(default_factory=list)
    accessibility_needs: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Couchbase storage"""
        return {
            "type": "travel_persona",
            "user_id": self.user_id,
            "name": self.name,
            "traveler_types": self.traveler_types,
            "budget_style": self.budget_style,
            "accommodation_style": self.accommodation_style,
            "travel_companions": self.travel_companions,
            "activity_preferences": self.activity_preferences,
            "dietary_restrictions": self.dietary_restrictions,
            "accessibility_needs": self.accessibility_needs,
            "created_at": self.created_at.isoformat(),
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimpleTravelPersona':
        """Create from Couchbase document"""
        return cls(
            user_id=data.get("user_id", ""),
            name=data.get("name", ""),
            traveler_types=data.get("traveler_types", []),
            budget_style=data.get("budget_style", ""),
            accommodation_style=data.get("accommodation_style", []),
            travel_companions=data.get("travel_companions", ""),
            activity_preferences=data.get("activity_preferences", []),
            dietary_restrictions=data.get("dietary_restrictions", []),
            accessibility_needs=data.get("accessibility_needs", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            completed=data.get("completed", False)
        )
    
    def get_persona_summary(self) -> str:
        """Get a text summary for AI prompts"""
        summary_parts = []
        
        if self.traveler_types:
            summary_parts.append(f"Travel style: {', '.join(self.traveler_types)}")
        
        if self.budget_style:
            summary_parts.append(f"Budget: {self.budget_style}")
        
        if self.travel_companions:
            summary_parts.append(f"Traveling: {self.travel_companions}")
        
        if self.activity_preferences:
            summary_parts.append(f"Interests: {', '.join(self.activity_preferences)}")
        
        if self.dietary_restrictions and 'no_restrictions' not in self.dietary_restrictions:
            clean_restrictions = [r for r in self.dietary_restrictions if r != 'no_restrictions']
            if clean_restrictions:
                summary_parts.append(f"Dietary: {', '.join(clean_restrictions)}")
        
        return "; ".join(summary_parts)
