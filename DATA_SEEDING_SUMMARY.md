# Travel & Tourism Data Seeding Summary

## Overview
Comprehensive seed data has been added to the backend for the travel and tourism endpoints in `app/data.py`.

## Data Statistics

### Cities
- **Total:** 3 cities
  - Douala (economic capital)
  - Yaounde (political capital)
  - Buea (garden city)

### Travel Routes
- **Total:** 12 travel routes
  - Yaounde ↔ Douala: 5 routes (various time slots)
  - Douala ↔ Buea: 3 routes
  - Yaounde ↔ Buea: 2 routes
  - Buea ↔ Douala: 2 routes

Each route includes:
- Departure/arrival times
- Available seat counts (6-18 seats)
- Price per seat (3500-6500 XAF)
- Confidence ratings (0.78-0.91)
- Distance and duration information
- Amenities (AC, WiFi, USB Charging, Snacks)

### Attractions
- **Total:** 16 attractions
- **Douala:** 5 attractions
  - Waterfront
  - Bonanjo Business District
  - Maritime Museum
  - Akwa Palace
  - Littoral State Museum
  
- **Yaounde:** 6 attractions
  - Mfoundi Central Market
  - National Museum
  - Mount Fébé Viewpoint
  - Benedictine Cathedral
  - Mvog Betsi Zoo
  - Museum of Cameroonian Art
  
- **Buea:** 5 attractions
  - Botanical Garden
  - Mount Cameroon
  - Historic Colonial Buildings
  - Museum of Buea
  - Limbe Beach (nearby)

Each attraction includes:
- Category (nature/culture)
- Ratings (4.0-4.9 stars)
- Opening hours
- Entry fees
- Geographic locations (latitude/longitude)
- Descriptive tags and details

## Endpoints Now Available with Seed Data

### Tourism Endpoints
- `GET /api/cities` - List all 3 cities
- `GET /api/cities/{city_id}/attractions` - Get attractions by city
- `GET /api/attractions/{attraction_id}` - Get specific attraction details
- `POST /api/attractions/search` - Search attractions by query/category

### Travel Endpoints
- `GET /api/travels` - List all 12 travel routes
- `GET /api/travels/{route_id}` - Get specific route details
- `POST /api/travels/search` - Search routes by origin/destination
- `POST /api/travels/estimate` - Get departure window estimates
- `POST /api/travels/book` - Book a travel route

## Data Format
All seed data is defined as Python dictionaries in `app/data.py` and automatically validated against Pydantic schemas:
- `app/schemas/tourism.py` - City and Attraction schemas
- `app/schemas/travels.py` - Travel-related schemas

## Testing
Run the following to verify the data loads correctly:

```bash
cd /Users/idristabi/Projects/school/CEC-601/backend
.venv/bin/python -c "from app import data; print(f'Routes: {len(data.travels)}, Cities: {len(data.cities)}, Attractions: {len(data.attractions)}')"
```

Expected output:
```
Routes: 12, Cities: 3, Attractions: 16
```

## Next Steps
- Deploy and test the API endpoints with the seeded data
- Add more routes/attractions as needed by editing `app/data.py`
- Consider migrating to a database with proper models for production
