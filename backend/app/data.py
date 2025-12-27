"""Static demo data used to stub API responses."""
from datetime import datetime, timedelta
from typing import Any, Dict, List


now = datetime.utcnow()

travels: List[Dict[str, Any]] = [
    {
        "id": "route-yaounde-douala",
        "origin": "Yaounde",
        "destination": "Douala",
        "departure_time": now.replace(hour=8, minute=30, second=0, microsecond=0),
        "estimated_arrival": now.replace(hour=12, minute=0, second=0, microsecond=0),
        "available_seats": 14,
        "price_per_seat": 5000.0,
        "confidence": 0.86,
        "distance_km": 230.0,
        "duration_minutes": 210,
        "amenities": ["AC", "WiFi"],
    },
    {
        "id": "route-douala-buea",
        "origin": "Douala",
        "destination": "Buea",
        "departure_time": now.replace(hour=10, minute=0, second=0, microsecond=0),
        "estimated_arrival": now.replace(hour=11, minute=30, second=0, microsecond=0),
        "available_seats": 9,
        "price_per_seat": 3500.0,
        "confidence": 0.78,
        "distance_km": 70.0,
        "duration_minutes": 90,
        "amenities": ["AC"],
    },
]

cities: List[Dict[str, Any]] = [
    {
        "id": "douala",
        "name": "Douala",
        "country": "Cameroon",
        "description": "Economic capital with vibrant markets and coastline",
        "population": 2000000,
    },
    {
        "id": "yaounde",
        "name": "Yaounde",
        "country": "Cameroon",
        "description": "Political capital with lush hills and museums",
        "population": 1500000,
    },
]

attractions: List[Dict[str, Any]] = [
    {
        "id": "douala-waterfront",
        "city_id": "douala",
        "name": "Douala Waterfront",
        "description": "Harbor views and seafood stalls",
        "category": "nature",
        "rating": 4.6,
        "opening_hours": "08:00-18:00",
        "entry_fee": "2000 XAF",
        "location": {"latitude": 4.052, "longitude": 9.7679, "accuracy_meters": 15},
        "tags": ["waterfront", "sunset", "seafood"],
    },
    {
        "id": "yaounde-mfoundi",
        "city_id": "yaounde",
        "name": "Mfoundi Market",
        "description": "Bustling central market with local crafts",
        "category": "culture",
        "rating": 4.2,
        "opening_hours": "07:00-17:00",
        "entry_fee": "Free",
        "location": {"latitude": 3.848, "longitude": 11.502, "accuracy_meters": 20},
        "tags": ["market", "shopping", "culture"],
    },
]

notifications: List[Dict[str, Any]] = [
    {
        "id": "notif-1",
        "title": "Departure delay",
        "body": "Yaounde → Douala departure delayed by 15 minutes",
        "created_at": now - timedelta(minutes=10),
        "read": False,
        "category": "travel",
    }
]

sessions: List[Dict[str, Any]] = [
    {
        "session_id": "session-1",
        "device_ip": "203.0.113.45",
        "device_type": "iPhone",
        "device_os": "iOS",
        "session_start": now - timedelta(hours=4),
        "last_activity": now - timedelta(minutes=5),
        "is_active": True,
        "ip_rotation_detected": False,
    }
]
