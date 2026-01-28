# API Documentation Guide (Swagger/OpenAPI)

**Project:** AI-IMUTIS  
**Framework:** FastAPI  
**OpenAPI Version:** 3.0.0  
**Last Updated:** December 26, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Accessing API Documentation](#accessing-api-documentation)
3. [FastAPI Configuration](#fastapi-configuration)
4. [Documentation Best Practices](#documentation-best-practices)
5. [Endpoint Documentation Examples](#endpoint-documentation-examples)
6. [Pydantic Models](#pydantic-models)
7. [Security Schemes](#security-schemes)
8. [Response Examples](#response-examples)
9. [Testing with Swagger UI](#testing-with-swagger-ui)
10. [Exporting OpenAPI Specification](#exporting-openapi-specification)

---

## Overview

FastAPI automatically generates interactive API documentation using the OpenAPI specification. This provides:

- **Interactive Testing:** Try API endpoints directly from the browser
- **Auto-generated Schemas:** Pydantic models automatically generate request/response schemas
- **Authentication Support:** Test protected endpoints with Firebase tokens
- **Code Examples:** Auto-generated code samples in multiple languages
- **Real-time Updates:** Documentation updates automatically as code changes

---

## Accessing API Documentation

### Development Environment

```
http://localhost:8000/docs       # Swagger UI
http://localhost:8000/redoc      # ReDoc
http://localhost:8000/openapi.json  # Raw OpenAPI spec
```

### Production Environment

```
https://api.ai-imutis.com/docs
https://api.ai-imutis.com/redoc
https://api.ai-imutis.com/openapi.json
```

---

## FastAPI Configuration

### Basic Setup

```python
from fastapi import FastAPI

app = FastAPI(
    title="AI-IMUTIS API",
    description="AI-Assisted Inter-Urban Mobility and Tourism Information System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

### Complete Configuration

```python
from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI-IMUTIS API",
    description="""
    # AI-Assisted Inter-Urban Mobility and Tourism Information System
    
    This API provides comprehensive services for:
    
    ## 🚌 Travel Management
    - Search inter-urban routes
    - Book trips with real-time availability
    - AI-powered departure window predictions
    - Real-time traffic and departure updates
    
    ## 🏛️ Tourism Information
    - Browse cities and attractions
    - Location-based recommendations
    - User reviews and ratings
    - Tourism guides and tips
    
    ## 🤖 AI Services
    - Departure time prediction (LSTM/GRU models)
    - Traffic flow forecasting (Graph Neural Networks)
    - Personalized tourism recommendations
    - Natural language tourist guide generation
    
    ## 📱 Device Management
    - Session tracking with device IP
    - Multi-device login management
    - Location tracking for analytics
    - Fraud detection and security
    
    ## 🔔 Real-time Features
    - WebSocket support for live updates
    - Push notifications via Firebase Cloud Messaging
    - Real-time departure and traffic alerts
    
    ## Authentication
    Most endpoints require Firebase Authentication. Include your Firebase ID token:
    ```
    Authorization: Bearer <your-firebase-id-token>
    ```
    
    ## Rate Limiting
    - **Standard**: 100 requests per minute per IP
    - **Authenticated**: 500 requests per minute per user
    - **WebSocket**: 10 concurrent connections per user
    
    ## Contact
    - **Email**: support@ai-imutis.com
    - **Website**: https://ai-imutis.com
    - **GitHub**: https://github.com/ai-imutis
    """,
    version="1.0.0",
    terms_of_service="https://ai-imutis.com/terms",
    contact={
        "name": "AI-IMUTIS Development Team",
        "email": "dev@ai-imutis.com",
        "url": "https://ai-imutis.com/contact",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas section by default
        "displayRequestDuration": True,  # Show request duration
        "filter": True,  # Enable search/filter
        "syntaxHighlight.theme": "monokai",  # Syntax highlighting theme
    },
)

security = HTTPBearer()

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Security schemes
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
        "DeviceIP": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Device-IP",
            "description": "Device IP address for analytics and fraud detection",
        },
    }
    
    # Reusable responses
    openapi_schema["components"]["responses"] = {
        "UnauthorizedError": {
            "description": "Authentication token missing or invalid",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"},
                        },
                        "example": {"detail": "Invalid authentication credentials"},
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
                            "detail": {"type": "string"},
                        },
                        "example": {"detail": "Resource not found"},
                    },
                },
            },
        },
        "ValidationError": {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "loc": {"type": "array", "items": {"type": "string"}},
                                        "msg": {"type": "string"},
                                        "type": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "RateLimitError": {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"},
                        },
                        "example": {"detail": "Rate limit exceeded. Try again in 60 seconds."},
                    },
                },
            },
        },
    }
    
    # API tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "Travel",
            "description": "Inter-urban travel route management and booking",
            "externalDocs": {
                "description": "Travel API Guide",
                "url": "https://docs.ai-imutis.com/travel",
            },
        },
        {
            "name": "Tourism",
            "description": "City and attraction information services",
            "externalDocs": {
                "description": "Tourism API Guide",
                "url": "https://docs.ai-imutis.com/tourism",
            },
        },
        {
            "name": "User",
            "description": "User profile, preferences, and account management",
        },
        {
            "name": "Device",
            "description": "Device session tracking and IP management",
        },
        {
            "name": "Notifications",
            "description": "Push notifications and real-time alerts",
        },
        {
            "name": "AI",
            "description": "AI-powered predictions and recommendations",
            "externalDocs": {
                "description": "AI Models Documentation",
                "url": "https://docs.ai-imutis.com/ai-models",
            },
        },
        {
            "name": "Admin",
            "description": "Administrative endpoints (requires admin role)",
        },
    ]
    
    # Add servers
    openapi_schema["servers"] = [
        {"url": "https://api.ai-imutis.com", "description": "Production"},
        {"url": "https://staging-api.ai-imutis.com", "description": "Staging"},
        {"url": "http://localhost:8000", "description": "Development"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## Documentation Best Practices

### 1. Use Descriptive Names

```python
@router.post(
    "/search",
    summary="Search available trips",  # Short, clear summary
    description="Search for available inter-urban trips based on origin, destination, and date",
    tags=["Travel"],
)
```

### 2. Document Parameters

```python
from pydantic import Field

class TripSearch(BaseModel):
    origin: str = Field(..., description="Origin city ID", example="douala")
    destination: str = Field(..., description="Destination city ID", example="yaounde")
    passengers: int = Field(1, ge=1, le=20, description="Number of passengers (1-20)")
```

### 3. Provide Examples

```python
class TripSearch(BaseModel):
    origin: str
    destination: str
    departure_date: datetime
    passengers: int
    
    class Config:
        schema_extra = {
            "example": {
                "origin": "douala",
                "destination": "yaounde",
                "departure_date": "2025-12-27T08:00:00Z",
                "passengers": 2,
            }
        }
```

### 4. Document Responses

```python
@router.post(
    "/search",
    response_model=List[TripResponse],
    responses={
        200: {"description": "List of available trips", "model": List[TripResponse]},
        400: {"description": "Invalid search parameters"},
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        429: {"$ref": "#/components/responses/RateLimitError"},
    },
)
```

### 5. Use Detailed Docstrings

```python
async def search_trips(search: TripSearch):
    """Search for available inter-urban trips.
    
    This endpoint searches for available trips matching the provided criteria
    and returns AI-powered departure window estimations with confidence scores.
    
    ## Search Parameters
    - **origin**: City ID for the departure location (e.g., 'douala', 'yaounde')
    - **destination**: City ID for the arrival location
    - **departure_date**: Preferred departure date and time (ISO 8601 format)
    - **passengers**: Number of passengers (between 1 and 20)
    
    ## AI Predictions
    Each trip includes:
    - Estimated departure time based on historical data
    - Confidence score (0.0 to 1.0) indicating prediction reliability
    - Traffic conditions affecting the route
    
    ## Rate Limiting
    This endpoint is rate-limited to 100 requests per minute per IP address.
    """
    pass
```

---

## Endpoint Documentation Examples

### Travel Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/travels", tags=["Travel"])

class TripSearchRequest(BaseModel):
    """Request model for trip search."""
    
    origin: str = Field(
        ...,
        description="Origin city ID",
        example="douala",
        min_length=2,
        max_length=50,
    )
    destination: str = Field(
        ...,
        description="Destination city ID",
        example="yaounde",
        min_length=2,
        max_length=50,
    )
    departure_date: datetime = Field(
        ...,
        description="Desired departure date (must be in the future)",
        example="2025-12-27T08:00:00Z",
    )
    passengers: int = Field(
        1,
        ge=1,
        le=20,
        description="Number of passengers",
        example=2,
    )
    max_price: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum price per seat in XAF",
        example=10000,
    )
    
    @validator("departure_date")
    def validate_future_date(cls, v):
        if v < datetime.now():
            raise ValueError("Departure date must be in the future")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "origin": "douala",
                "destination": "yaounde",
                "departure_date": "2025-12-27T08:00:00Z",
                "passengers": 2,
                "max_price": 8000,
            }
        }

class DeparturePrediction(BaseModel):
    """AI-powered departure prediction."""
    
    estimated_time: datetime = Field(..., description="Predicted departure time")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    factors: dict = Field(..., description="Factors influencing the prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "estimated_time": "2025-12-27T08:30:00Z",
                "confidence": 0.87,
                "factors": {
                    "traffic": "light",
                    "passenger_load": "moderate",
                    "time_of_day": "morning",
                },
            }
        }

class TripResponse(BaseModel):
    """Response model for trip information."""
    
    id: str = Field(..., description="Unique trip identifier")
    route_id: str = Field(..., description="Route identifier")
    departure_time: datetime = Field(..., description="Scheduled departure time")
    estimated_arrival: datetime = Field(..., description="Estimated arrival time")
    duration_minutes: int = Field(..., description="Trip duration in minutes")
    available_seats: int = Field(..., ge=0, description="Number of available seats")
    total_seats: int = Field(..., description="Total seats in vehicle")
    price_per_seat: float = Field(..., ge=0, description="Price per seat in XAF")
    vehicle_type: str = Field(..., description="Type of vehicle")
    driver_name: str = Field(..., description="Driver name")
    departure_prediction: DeparturePrediction = Field(..., description="AI prediction")
    amenities: List[str] = Field(default=[], description="Vehicle amenities")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "trip-abc123",
                "route_id": "route-douala-yaounde",
                "departure_time": "2025-12-27T08:00:00Z",
                "estimated_arrival": "2025-12-27T11:30:00Z",
                "duration_minutes": 210,
                "available_seats": 15,
                "total_seats": 18,
                "price_per_seat": 5000.0,
                "vehicle_type": "minibus",
                "driver_name": "Jean Mballa",
                "departure_prediction": {
                    "estimated_time": "2025-12-27T08:30:00Z",
                    "confidence": 0.87,
                    "factors": {
                        "traffic": "light",
                        "passenger_load": "moderate",
                    },
                },
                "amenities": ["AC", "WiFi", "USB charging"],
            }
        }

@router.post(
    "/search",
    response_model=List[TripResponse],
    status_code=status.HTTP_200_OK,
    summary="Search available trips",
    description="Search for inter-urban trips with AI-powered departure predictions",
    responses={
        200: {
            "description": "List of available trips matching search criteria",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "trip-abc123",
                            "route_id": "route-douala-yaounde",
                            "departure_time": "2025-12-27T08:00:00Z",
                            "available_seats": 15,
                            "price_per_seat": 5000.0,
                        }
                    ]
                }
            },
        },
        400: {"description": "Invalid search parameters"},
        401: {"$ref": "#/components/responses/UnauthorizedError"},
        429: {"$ref": "#/components/responses/RateLimitError"},
    },
    tags=["Travel"],
)
async def search_trips(
    search: TripSearchRequest,
    user: dict = Depends(verify_firebase_token),
) -> List[TripResponse]:
    """
    Search for available inter-urban trips with AI-powered departure predictions.
    
    This endpoint performs the following:
    
    1. **Search Matching Routes**: Finds trips from origin to destination
    2. **Check Availability**: Filters trips with available seats
    3. **AI Prediction**: Generates departure window estimations using LSTM model
    4. **Price Filter**: Applies maximum price filter if specified
    5. **Sort Results**: Orders by departure time and confidence score
    
    ## Parameters
    
    - **origin** (required): City ID for departure (e.g., 'douala', 'yaounde', 'bamenda')
    - **destination** (required): City ID for arrival
    - **departure_date** (required): Preferred departure date (ISO 8601 format, must be future)
    - **passengers** (optional): Number of passengers, default 1 (1-20)
    - **max_price** (optional): Maximum price filter in XAF
    
    ## AI Prediction Details
    
    Each trip includes an AI-generated departure prediction with:
    - **estimated_time**: Predicted actual departure time
    - **confidence**: Model confidence score (0.0-1.0)
      - 0.85+: High confidence
      - 0.70-0.85: Medium confidence
      - <0.70: Low confidence
    - **factors**: Key factors influencing the prediction
    
    ## Rate Limiting
    
    - **Unauthenticated**: 10 requests per minute
    - **Authenticated**: 100 requests per minute
    
    ## Example Usage
    
    ```python
    import requests
    
    response = requests.post(
        "https://api.ai-imutis.com/api/travels/search",
        headers={"Authorization": f"Bearer {firebase_token}"},
        json={
            "origin": "douala",
            "destination": "yaounde",
            "departure_date": "2025-12-27T08:00:00Z",
            "passengers": 2,
        }
    )
    trips = response.json()
    ```
    
    ## Notes
    
    - Results are cached for 5 minutes to improve performance
    - Real-time availability updates via WebSocket at `/ws/route/{route_id}/availability`
    - Departure predictions refresh every 10 minutes
    """
    # Implementation
    pass
```

### Device Tracking Endpoint

```python
@router.get(
    "/sessions",
    response_model=List[DeviceSession],
    summary="Get active device sessions",
    description="Retrieve all active sessions for the authenticated user",
    responses={
        200: {"description": "List of active device sessions"},
        401: {"$ref": "#/components/responses/UnauthorizedError"},
    },
    tags=["Device"],
)
async def get_user_sessions(
    user: dict = Depends(verify_firebase_token),
) -> List[DeviceSession]:
    """
    Get all active device sessions for the current user.
    
    This endpoint returns a list of all devices currently logged in with the user's account,
    including device information and IP addresses.
    
    ## Use Cases
    
    - **Security Monitoring**: Review devices with access to your account
    - **Session Management**: Identify and revoke unauthorized sessions
    - **Analytics**: Track device usage patterns
    
    ## Response Details
    
    Each session includes:
    - **session_id**: Unique identifier for this session
    - **device_ip**: IP address of the device
    - **device_type**: Device model (e.g., "iPhone 14", "Samsung Galaxy S23")
    - **device_os**: Operating system and version
    - **last_activity**: Timestamp of most recent API request
    - **ip_rotation_detected**: Flag if IP has changed suspiciously
    
    ## Security Notes
    
    - Sessions automatically expire after 30 days of inactivity
    - IP rotation detection flags potential account compromise
    - Use `DELETE /api/users/sessions/{session_id}` to revoke suspicious sessions
    """
    pass
```

---

## Pydantic Models

### Best Practices for Schema Generation

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration."""
    user = "user"
    driver = "driver"
    admin = "admin"

class UserProfile(BaseModel):
    """User profile information."""
    
    uid: str = Field(..., description="Firebase user ID")
    email: EmailStr = Field(..., description="User email address")
    phone_number: Optional[str] = Field(None, description="Phone number in E.164 format", example="+237600000000")
    display_name: str = Field(..., min_length=2, max_length=100, description="User's display name")
    role: UserRole = Field(default=UserRole.user, description="User role")
    preferred_language: str = Field("en", description="Preferred language (ISO 639-1)", example="en")
    created_at: datetime = Field(..., description="Account creation timestamp")
    email_verified: bool = Field(default=False, description="Email verification status")
    
    @validator("phone_number")
    def validate_phone(cls, v):
        if v and not v.startswith("+"):
            raise ValueError("Phone number must be in E.164 format (+237...)")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "uid": "firebase-uid-123",
                "email": "user@example.com",
                "phone_number": "+237670123456",
                "display_name": "John Doe",
                "role": "user",
                "preferred_language": "en",
                "created_at": "2025-01-15T10:00:00Z",
                "email_verified": True,
            }
        }
```

---

## Security Schemes

### Firebase Authentication in Swagger

```python
# In endpoint definition
@router.get(
    "/profile",
    dependencies=[Security(security)],  # Shows lock icon in Swagger UI
)
async def get_profile(
    user: dict = Depends(verify_firebase_token),
):
    pass
```

### Testing Authentication in Swagger UI

1. Click **"Authorize"** button in Swagger UI
2. Enter Firebase ID token: `Bearer <your-token>`
3. Click **"Authorize"**
4. All subsequent requests include the token

---

## Response Examples

### Success Response

```python
from fastapi import status
from fastapi.responses import JSONResponse

@router.post("/book", status_code=status.HTTP_201_CREATED)
async def book_trip():
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "booking_id": "book-123",
            "status": "confirmed",
            "message": "Booking created successfully",
        },
    )
```

### Error Responses

```python
from fastapi import HTTPException

@router.get("/trips/{trip_id}")
async def get_trip(trip_id: str):
    trip = db.get_trip(trip_id)
    if not trip:
        raise HTTPException(
            status_code=404,
            detail=f"Trip {trip_id} not found",
        )
    return trip
```

---

## Testing with Swagger UI

### Step-by-Step

1. **Open Swagger UI**: Navigate to `http://localhost:8000/docs`

2. **Authenticate**:
   - Click "Authorize" button
   - Enter Firebase token
   - Click "Authorize"

3. **Select Endpoint**:
   - Choose endpoint (e.g., `POST /api/travels/search`)
   - Click "Try it out"

4. **Enter Parameters**:
   - Fill in request body
   - Swagger shows validation rules

5. **Execute Request**:
   - Click "Execute"
   - View response code, headers, body

6. **Copy Code**:
   - Click language tab (curl, Python, JavaScript)
   - Copy generated code

---

## Exporting OpenAPI Specification

### Download JSON

```bash
# Download OpenAPI spec
curl http://localhost:8000/openapi.json > openapi.json
```

### Generate Client SDKs

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./client-sdk

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client
```

### Import to Postman

1. Open Postman
2. Click "Import"
3. Enter URL: `http://localhost:8000/openapi.json`
4. Postman auto-generates collection

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/metadata/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Swagger UI Configuration](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/)

---

**Last Updated:** December 26, 2025  
**Maintained By:** AI-IMUTIS Development Team
