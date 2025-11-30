from firebase_admin import firestore
from ..core.firebase import db
from google.cloud.firestore_v1 import FieldFilter
import datetime
from typing import Optional, Dict, Any

class OutfitRepository:
    def __init__(self):
        self.collection = db.collection('outfits')

    def get_outfit_by_date(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches the outfit for a specific date.
        If no date is provided, defaults to today.
        """
        if not date:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        # Create filter
        field_filter = FieldFilter('date', '==', date)
        
        # Query
        query = self.collection.where(filter=field_filter).limit(1)
        docs = query.stream()
        
        for doc in docs:
            data = doc.to_dict()
            patterns = data.get('patterns', {})
            
            # Handle patterns being a map or list (defensive)
            description = "Unknown"
            season = "Unknown"
            
            if isinstance(patterns, dict):
                description = patterns.get('title', 'Unknown')
                season = patterns.get('season', 'Unknown')
            elif isinstance(patterns, list) and patterns:
                # Fallback if it is a list
                description = ", ".join(patterns)
            
            return {
                "id": doc.id,
                "formula": description, # Mapping title to formula/description
                "description": description,
                "image_url": data.get('image'),
                "dress_it_up": data.get('dress_it_up'),
                "dress_it_down": data.get('dress_it_down'),
                "season": season,
                "date": data.get('date')
            }
            
        return None
