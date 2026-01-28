# AI-IMUTIS Architecture & Quick Reference

---

## Section 0: Security Architecture

**Reference**: Complete implementation in [SECURITY_GUIDE.md](SECURITY_GUIDE.md)

### Security Layers Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                  CLIENT LAYER (Mobile App)                       │
│  • Secure Storage (expo-secure-store)                           │
│  • Certificate Pinning                                           │
│  • Jailbreak/Root Detection                                      │
│  • Biometric Authentication                                      │
│  • Input Validation                                              │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS/TLS 1.3
┌────────────────────────────┴─────────────────────────────────────┐
│                  NETWORK LAYER (WAF/CDN)                         │
│  • CloudFlare DDoS Protection                                    │
│  • AWS WAF Rules (SQL injection, XSS)                           │
│  • Rate Limiting (IP-based)                                      │
│  • Geo-blocking                                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                APPLICATION LAYER (FastAPI)                       │
│  • Firebase Token Verification                                   │
│  • Multi-tier Rate Limiting (Redis)                             │
│  • Adaptive Throttling                                           │
│  • Input Sanitization (HTML, SQL, Path)                         │
│  • Session Management (Device-bound)                             │
│  • CORS (Whitelist origins)                                      │
│  • Security Headers (HSTS, CSP, etc.)                           │
└────────────────────────────┬─────────────────────────────────────┘
                             │ Parameterized Queries
┌────────────────────────────┴─────────────────────────────────────┐
│                 DATABASE LAYER (PostgreSQL)                      │
│  • Row-Level Security (RLS)                                      │
│  • Audit Logging                                                 │
│  • Encryption at Rest                                            │
│  • SSL/TLS Connections                                           │
│  • Least Privilege Access                                        │
└──────────────────────────────────────────────────────────────────┘
```

### Rate Limiting Strategy

| Tier | Requests/Min | Window | Endpoints |
|------|--------------|--------|-----------|
| Anonymous | 10 | 60s | All |
| Authenticated | 100 | 60s | General |
| Premium | 500 | 60s | General |
| AI Endpoints | 20 | 60s | /ai/* |
| Booking | 5 | 60s | /book* |

### Critical Security Rules

```python
# DDoS Protection Triggers (Auto-block if):
- More than 100 requests in 5 minutes
- More than 10 requests per second
- SQL injection patterns detected
- XSS patterns detected
- Path traversal attempts

# Block duration: 60 minutes
# Repeated violations: Permanent ban + SOC alert
```

---

## Section 1: API Documentation (Swagger/OpenAPI)

### 1.1 Documentation Endpoints

**Automatic API Documentation:**
```
GET /docs          - Interactive Swagger UI for API testing
GET /redoc         - Clean ReDoc documentation interface  
GET /openapi.json  - Machine-readable OpenAPI 3.0 specification
```

### 1.2 FastAPI Configuration

```python
from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="AI-IMUTIS API",
    description="""AI-Assisted Inter-Urban Mobility and Tourism Information System
    
    ## Features
    * **Travel Management**: Search routes, book trips, track departures
    * **Tourism Information**: Browse cities and attractions
    * **AI Predictions**: Departure window estimation, traffic forecasting
    * **Device Tracking**: Session management with IP tracking
    * **Real-time Updates**: WebSocket support for live notifications
    
    ## Authentication
    All protected endpoints require Firebase ID token in Authorization header:
    ```
    Authorization: Bearer <firebase-id-token>
    ```
    """,
    version="1.0.0",
    contact={
        "name": "AI-IMUTIS Development Team",
        "email": "dev@ai-imutis.com",
        "url": "https://ai-imutis.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

security = HTTPBearer()

# Custom OpenAPI schema with security definitions
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "FirebaseAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Firebase ID Token obtained from Firebase Authentication",
        },
        "DeviceFingerprint": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Device-Fingerprint",
            "description": "Unique device identifier for session tracking",
        },
    }
    
    # Add example responses
    openapi_schema["components"]["responses"] = {
        "UnauthorizedError": {
            "description": "Authentication token missing or invalid",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string", "example": "Invalid authentication credentials"},
                        },
                    },
                },
            },
        },
        "NotFoundError": {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string", "example": "Resource not found"},
                        },
                    },
                },
            },
        },
    }
    
    # Add tags metadata
    openapi_schema["tags"] = [
        {"name": "Travel", "description": "Inter-urban travel route management"},
        {"name": "Tourism", "description": "City and attraction information"},
        {"name": "User", "description": "User profile and preferences"},
        {"name": "Device", "description": "Device session and IP tracking"},
        {"name": "Notifications", "description": "Push notifications and alerts"},
        {"name": "AI", "description": "AI-powered predictions and recommendations"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 1.3 Example Endpoint Documentation

```python
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/travels", tags=["Travel"])

class TripSearchRequest(BaseModel):
    origin: str = Field(..., description="Origin city ID", example="douala")
    destination: str = Field(..., description="Destination city ID", example="yaounde")
    departure_date: datetime = Field(..., description="Desired departure date")
    passengers: int = Field(1, ge=1, le=20, description="Number of passengers")
    
    class Config:
        schema_extra = {
            "example": {
                "origin": "douala",
                "destination": "yaounde",
                "departure_date": "2025-12-27T08:00:00Z",
                "passengers": 2,
            }
        }

class TripResponse(BaseModel):
    id: str = Field(..., description="Unique trip identifier")
    departure_time: datetime = Field(..., description="Scheduled departure time")
    estimated_arrival: datetime = Field(..., description="Estimated arrival time")
    available_seats: int = Field(..., description="Number of available seats")
    price_per_seat: float = Field(..., description="Price per seat in XAF")
    confidence: float = Field(..., ge=0, le=1, description="Departure prediction confidence")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "trip-123",
                "departure_time": "2025-12-27T08:30:00Z",
                "estimated_arrival": "2025-12-27T12:00:00Z",
                "available_seats": 15,
                "price_per_seat": 5000.0,
                "confidence": 0.87,
            }
        }

@router.post(
    "/search",
    response_model=List[TripResponse],
    summary="Search available trips",
    description="Search for available inter-urban trips based on origin, destination, and date",
    responses={
        200: {"description": "List of available trips"},
        400: {"description": "Invalid search parameters"},
        401: {"$ref": "#/components/responses/UnauthorizedError"},
    },
    tags=["Travel"],
)
async def search_trips(
    search: TripSearchRequest,
    user: dict = Depends(verify_firebase_token),
):
    """Search for available trips with AI-powered departure predictions.
    
    This endpoint returns a list of available trips matching the search criteria,
    including AI-generated departure window estimations with confidence scores.
    
    - **origin**: City ID for departure location
    - **destination**: City ID for arrival location
    - **departure_date**: Preferred departure date and time
    - **passengers**: Number of passengers (1-20)
    """
    # Implementation
    pass
```

---

## 2. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                                  │
├──────────────────────┬──────────────────────┬────────────────────┤
│  React Native App    │  Web Dashboard       │  Admin Portal      │
│  (Expo)              │  (React.js)          │  (React.js)        │
│  ├─ Travels         │  ├─ Analytics       │  ├─ Users         │
│  ├─ Tourism         │  ├─ Bookings        │  ├─ Routes        │
│  ├─ Notifications   │  └─ Reports         │  └─ Content       │
│  └─ User Profile    │                      │                   │
│                      │ Firebase Auth       │ Firebase Auth     │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
              HTTPS       │
                          ▼
        ┌────────────────────────────────────────┐
        │    FastAPI Backend (Railway/Fly.io)   │
        ├────────────────────────────────────────┤
        │  API Gateway & Authentication          │
        │  ├─ Firebase JWT Verification          │
        │  ├─ RBAC (Role-Based Access Control)  │
        │  └─ Rate Limiting (Redis)              │
        │                                        │
        │  API Endpoints                         │
        │  ├─ /api/travels/* (Route management) │
        │  ├─ /api/attractions/* (Tourism)      │
        │  ├─ /api/ai/* (AI predictions)        │
        │  ├─ /api/users/* (User data)          │
        │  └─ /api/notifications/* (Alerts)    │
        │                                        │
        │  AI Model Inference Layer              │
        │  ├─ TensorFlow Lite (Departure)       │
        │  ├─ TensorFlow Lite (Traffic)         │
        │  ├─ Sentence-Transformers (Tourism)   │
        │  └─ Gemini Nano Client (LLM)         │
        │                                        │
        │  WebSocket Server                      │
        │  ├─ /ws/route/{id}/traffic            │
        │  └─ /ws/user/{id}/notifications       │
        │                                        │
        │  Integration Middleware                │
        │  ├─ Google Maps API client             │
        │  ├─ Firebase Admin SDK                 │
        │  ├─ Stripe webhook handler            │
        │  └─ SendGrid/Twilio client            │
        └────┬─────┬──────────┬────────┬─────────┘
             │     │          │        │
    ┌────────▼─┐  │    ┌──────▼─┐    │
    │PostgreSQL│  │    │Firebase │    │
    │+ PostGIS │  │    │Services │    │
    ├──────────┤  │    ├─────────┤    │
    │ Tables:  │  │    │ • Auth  │    │
    │ • users  │  │    │ • FCM   │    │
    │ • routes │  │    │ • Storage│   │
    │ • cities │  │    └─────────┘    │
    │ • attract.│ │                    │
    │ • bookings│ │    ┌──────────────▼┐
    │ • patterns│ │    │ Google Maps   │
    │          │  │    │ • Maps API    │
    │Supabase  │  │    │ • Routes API  │
    │Hosting   │  │    │ • Places API  │
    └──────────┘  │    │ • Distance M. │
                  │    └───────────────┘
         ┌────────▼──────────┐
         │ External Services │
         ├───────────────────┤
         │ • Stripe          │
         │ • SendGrid        │
         │ • Twilio          │
         │ • Gemini API      │
         └───────────────────┘
```

---

## Data Flow: Departure Window Prediction

```
1. USER INITIATES
   Mobile User: "When can I leave for Douala?"
   
2. FRONTEND REQUEST
   POST /api/ai/estimate-departure
   {
     "route_id": "yaounde-douala",
     "current_time": "2025-01-15T08:00:00Z",
     "user_preferences": { "comfort": "high", "cost": "low" }
   }
   
3. BACKEND PROCESSING
   a) Firebase Token Verification
      ├─ Decode JWT token
      └─ Check user permissions
      
   b) Database Query (PostgreSQL)
      ├─ Fetch route details (ID: yaounde-douala)
      ├─ Fetch historical traffic patterns
      ├─ Fetch user travel history
      └─ Query road conditions via spatial join
      
   c) AI Model Inference (FastAPI Async)
      ├─ Input Validation (Pydantic)
      ├─ Load TensorFlow Lite LSTM model
      ├─ Prepare feature vector:
      │  ├─ Time of day encoding
      │  ├─ Day of week encoding
      │  ├─ Historical departure patterns
      │  ├─ Seasonal factors
      │  └─ User preferences
      ├─ Run model inference (non-blocking)
      ├─ Generate 3 time windows with confidence
      └─ Cache result in memory
      
   d) External API Call (Google Maps)
      ├─ Get real-time traffic conditions
      ├─ Update confidence scores based on current traffic
      └─ Add traffic.predictedDuration to response
      
   e) Response Formatting
      └─ Return JSON with confidence & explanation
      
4. RESPONSE
   {
     "departure_windows": [
       {
         "start_time": "08:30",
         "end_time": "09:00",
         "confidence": 0.92,
         "explanation": "Avoid rush hour (7-8am)"
       },
       {
         "start_time": "14:00",
         "end_time": "15:00",
         "confidence": 0.78,
         "explanation": "Off-peak hours"
       },
       {
         "start_time": "20:00",
         "end_time": "21:00",
         "confidence": 0.65,
         "explanation": "Night travel (less traffic, more risk)"
       }
     ],
     "estimated_duration": "4h 15m",
     "traffic_level": "moderate",
     "timestamp": "2025-01-15T08:15:00Z"
   }
   
5. FRONTEND RENDERING
   Mobile App:
   ├─ Display 3 departure windows on card
   ├─ Color-code by confidence (green > orange > red)
   ├─ Show estimated arrival times
   ├─ Display traffic map via Google Maps
   └─ Offer one-tap booking
```

---

## Real-Time Traffic Updates Flow

```
CLIENT (React Native)
  │
  ├─ WebSocket Connection Established
  │  ws://api.ai-imutis.com/api/ws/route/{route_id}/traffic
  │
  └─ Open: User viewing route from Yaounde to Douala
  
BACKEND (FastAPI)
  │
  ├─ Accept WebSocket connection
  │
  ├─ Start periodic updates (every 30 seconds)
  │  ├─ Query real-time traffic from Google Maps API
  │  ├─ Run LSTM model for next-hour prediction
  │  └─ Compare with previous state
  │
  ├─ On change detected:
  │  ├─ Prepare update object
  │  └─ Send via WebSocket
  │
  └─ Connection closes: User navigates away or closes app
  
DATA STRUCTURE (sent to client)
{
  "timestamp": "2025-01-15T08:45:00Z",
  "route_id": "yaounde-douala",
  "segments": [
    {
      "id": "segment_1",
      "current_speed": 45,
      "speed_limit": 110,
      "congestion_level": "moderate", // low, moderate, heavy, standstill
      "eta_without_traffic": 15,      // minutes
      "eta_with_traffic": 28,
      "traffic_prediction_30min": "heavy",
      "incidents": [
        {
          "type": "construction",
          "location": "km 15-20",
          "impact": "minor"
        }
      ]
    },
    // ... more segments
  ],
  "revised_departure_window": "09:15-09:30" // Based on current traffic
}
```

---

## Tourism Recommendation Flow

```
1. USER ACTION
   User scrolls "Attractions near Douala"
   
2. FRONTEND REQUEST
   GET /api/ai/tourism-suggestions/douala?limit=10&user_profile=premium
   
3. BACKEND LOGIC
   a) Fetch User Profile from Database
      ├─ Travel history
      ├─ Saved attractions
      ├─ Ratings & preferences
      ├─ Language preference
      └─ Budget tier
      
   b) Load AI Models
      ├─ Sentence-Transformers (embedding model)
      └─ Precomputed attraction embeddings (cache)
      
   c) Embedding Search & Ranking
      ├─ Create user preference embedding
      │  └─ "History + culture" + "nature" + "family-friendly"
      ├─ Compute cosine similarity with all attractions
      ├─ Apply business logic filters
      │  ├─ Distance from user location
      │  ├─ Opening hours
      │  ├─ Entry fee within budget
      │  └─ Rating > 4.0
      ├─ Cluster similar attractions (DBSCAN)
      └─ Select top-10 with diversity
      
   d) Enrich with Gemini Nano
      For top 3 recommendations:
      ├─ Generate personalized guide text
      │  ├─ "Why visit this attraction"
      │  ├─ "Best time to visit"
      │  └─ "Local tips"
      └─ Cache result for 24 hours
      
   e) Include Google Maps Data
      ├─ Current reviews (from Places API)
      ├─ Photos
      ├─ Operating hours
      └─ Maps link
      
4. RESPONSE
   {
     "attractions": [
       {
         "id": "attr_123",
         "name": "Mount Cameroon",
         "category": "nature",
         "distance_km": 15,
         "relevance_score": 0.94,
         "ai_guide": "Mount Cameroon is a 4,095m active volcano...",
         "rating": 4.7,
         "review_count": 342,
         "opening_hours": "06:00-18:00",
         "entry_fee_xaf": 5000,
         "images": ["url1", "url2"],
         "maps_url": "https://..."
       },
       // ... 9 more attractions
     ]
   }
   
5. FRONTEND
   ├─ Display grid of attractions
   ├─ Show distance & relevance visually
   ├─ Lazy-load images
   ├─ Offer "More info" → full guide
   └─ Allow saving/sharing
```

---

## Authentication Flow

```
MOBILE SIGNUP
  │
  ├─ User enters phone number
  │
  └─ Firebase Phone Auth
     ├─ Send SMS OTP
     ├─ User enters OTP
     └─ Firebase returns ID Token + Refresh Token
  
BACKEND VERIFICATION (on every request)
  │
  ├─ Request arrives with Authorization header
  │  Authorization: Bearer {idToken}
  │
  ├─ FastAPI Middleware
  │  ├─ Extract token from header
  │  ├─ Call Firebase Admin SDK
  │  │  └─ Verify signature + expiration
  │  ├─ Decode token payload
  │  │  └─ Get user UID, email, phone
  │  └─ Inject user context into request
  │
  ├─ Query database for user details
  │  ├─ Load preferences
  │  ├─ Check RBAC role
  │  └─ Verify account status
  │
  └─ Proceed with business logic
  
TOKEN REFRESH
  │
  ├─ Frontend detects token expiration (60 min)
  │
  ├─ Firebase SDK automatically refreshes
  │  └─ Uses refresh token
  │
  └─ New ID token sent in next request

LOGOUT
  │
  ├─ Firebase SDK clears local tokens
  │
  └─ Backend: No action required (tokens expire)
```

---

## Database Schema (Key Tables)

```sql
-- Users (linked to Firebase)
CREATE TABLE users (
  id UUID PRIMARY KEY,
  firebase_uid TEXT UNIQUE NOT NULL,
  phone_number TEXT,
  email TEXT,
  first_name TEXT,
  last_name TEXT,
  language VARCHAR(5) DEFAULT 'en',
  notification_settings JSONB,
  preferences JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Device Sessions (IP tracking and session management)
CREATE TABLE device_sessions (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_ip INET NOT NULL,
  device_fingerprint TEXT,
  device_type VARCHAR(50),
  device_os VARCHAR(50),
  device_os_version VARCHAR(50),
  app_version VARCHAR(20),
  firebase_token TEXT,
  session_start TIMESTAMP NOT NULL,
  session_end TIMESTAMP,
  last_activity TIMESTAMP,
  ip_rotation_detected BOOLEAN DEFAULT FALSE,
  ip_changes INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  INDEX idx_user_ip (user_id, device_ip),
  INDEX idx_active_sessions (user_id, is_active)
);

-- User Locations (GPS tracking with IP)
CREATE TABLE user_locations (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_session_id UUID REFERENCES device_sessions(id),
  location GEOMETRY(POINT, 4326) NOT NULL,
  latitude NUMERIC(10, 8),
  longitude NUMERIC(11, 8),
  accuracy_meters NUMERIC,
  device_ip INET,
  route_id UUID REFERENCES routes(id),
  activity_type VARCHAR(50),
  timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP,
  INDEX idx_user_location (user_id, timestamp),
  INDEX idx_location (location),
  INDEX idx_route_location (route_id, timestamp)
);

-- Routes (with geometry)
CREATE TABLE routes (
  id UUID PRIMARY KEY,
  name TEXT,
  origin_city_id UUID REFERENCES cities(id),
  destination_city_id UUID REFERENCES cities(id),
  route_geometry GEOMETRY(LINESTRING, 4326),
  distance_km NUMERIC,
  estimated_duration_minutes INTEGER,
  difficulty_level VARCHAR(20),
  created_at TIMESTAMP
);

-- Route Segments (for traffic prediction)
CREATE TABLE route_segments (
  id UUID PRIMARY KEY,
  route_id UUID REFERENCES routes(id),
  sequence_number INTEGER,
  segment_geometry GEOMETRY(LINESTRING, 4326),
  segment_length_km NUMERIC,
  road_type VARCHAR(50),
  speed_limit_kmh INTEGER,
  created_at TIMESTAMP
);

-- Cities (with boundary)
CREATE TABLE cities (
  id UUID PRIMARY KEY,
  name TEXT,
  country VARCHAR(2),
  latitude NUMERIC,
  longitude NUMERIC,
  city_boundary GEOMETRY(POLYGON, 4326),
  population INTEGER,
  climate_zone VARCHAR(50),
  created_at TIMESTAMP
);

-- Attractions (with location)
CREATE TABLE attractions (
  id UUID PRIMARY KEY,
  name TEXT,
  description TEXT,
  category VARCHAR(50),
  location GEOMETRY(POINT, 4326),
  city_id UUID REFERENCES cities(id),
  rating NUMERIC(3,1),
  review_count INTEGER,
  opening_hours JSON,
  entry_fee_xaf INTEGER,
  ai_generated_guide TEXT,
  images TEXT[],
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  INDEX idx_location USING GIST (location)
);

-- Bookings (with predictions)
CREATE TABLE bookings (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  route_id UUID REFERENCES routes(id),
  departure_time TIMESTAMP,
  predicted_departure TIMESTAMP,
  actual_departure TIMESTAMP,
  status VARCHAR(50),
  payment_status VARCHAR(50),
  price_xaf NUMERIC,
  created_at TIMESTAMP
);

-- AI Predictions (audit log)
CREATE TABLE ai_predictions (
  id UUID PRIMARY KEY,
  model_type VARCHAR(50),
  model_version VARCHAR(10),
  input_data JSONB,
  prediction JSONB,
  confidence NUMERIC(3,2),
  user_feedback NUMERIC(1),
  created_at TIMESTAMP,
  INDEX idx_model_type (model_type),
  INDEX idx_created_at (created_at)
);
```

---

## API Endpoints Quick Reference

### Travel Management
```
GET    /api/travels                     # List available routes
POST   /api/travels/search              # Search with filters
GET    /api/travels/{route_id}          # Get route details
POST   /api/travels/book                # Create booking
GET    /api/travels/{route_id}/history  # User's travel history
```

### AI Predictions
```
POST   /api/ai/estimate-departure       # Departure window prediction
GET    /api/ai/traffic-prediction/{id}  # Real-time traffic
POST   /api/ai/recommend-attractions    # Tourism recommendations
GET    /api/ai/tourist-guide/{attr_id}  # AI-generated guide
```

### Tourism
```
GET    /api/cities                      # List major cities
GET    /api/cities/{city_id}/attractions # Attractions in city
GET    /api/attractions/{id}            # Attraction details
POST   /api/attractions/search          # Full-text search
```

### Real-Time
```
WS     /api/ws/route/{id}/traffic       # Live traffic updates
WS     /api/ws/user/{id}/notifications  # User notifications
```

### User Management
```
GET    /api/users/profile               # Get user info
PUT    /api/users/profile               # Update profile
POST   /api/users/preferences           # Save preferences
DELETE /api/users/account               # Delete account
```

---

## Deployment Checklist

- [ ] **Firebase Setup**
  - [ ] Create Firebase project
  - [ ] Enable Authentication (phone, email, Google, Apple)
  - [ ] Set up Web and iOS/Android apps
  - [ ] Configure Firebase Cloud Messaging

- [ ] **Google Maps API**
  - [ ] Create GCP project
  - [ ] Enable Maps, Routes, Places, Distance Matrix, Geocoding APIs
  - [ ] Create API key with restrictions
  - [ ] Set spending limits

- [ ] **Database**
  - [ ] Create Supabase project
  - [ ] Enable PostGIS extension
  - [ ] Create all tables
  - [ ] Set up RLS policies
  - [ ] Configure backups

- [ ] **Backend Deployment**
  - [ ] Create Railway/Fly.io account
  - [ ] Build Docker image
  - [ ] Configure environment variables
  - [ ] Set up auto-scaling
  - [ ] Configure custom domain

- [ ] **Frontend Deployment**
  - [ ] Build React/React Native apps
  - [ ] Deploy web to Vercel
  - [ ] Build iOS via EAS
  - [ ] Build Android via EAS
  - [ ] Set up App Store/Google Play accounts

- [ ] **Monitoring**
  - [ ] Set up Sentry error tracking
  - [ ] Configure Datadog APM (optional)
  - [ ] Create monitoring dashboards
  - [ ] Set up alerts for critical metrics

---

**Version:** 1.0  
**Created:** December 26, 2025
