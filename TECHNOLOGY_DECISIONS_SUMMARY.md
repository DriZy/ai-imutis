# AI-IMUTIS Technology Stack Decisions Summary

**Last Updated:** December 26, 2025  
**Status:** Approved for Implementation

---

## Executive Summary

The AI-IMUTIS implementation has been optimized for performance, maintainability, and rapid deployment. All technology selections prioritize **2-3x performance gains** for AI model inference and seamless integration with the data science ecosystem.

---

## Technology Selections & Rationale

### 1. Mobile Frontend: React Native + Expo ✅

**Selection:** React Native + Expo for iOS/Android  
**Alternatives Considered:** Flutter, native iOS/Android  

**Why React Native + Expo:**
- **Cross-platform:** Single codebase for iOS, Android, and web
- **Rapid deployment:** Expo EAS Build automates iOS/Android builds (no Mac required for Android)
- **Shared components:** Reuse React knowledge across web dashboard
- **Development speed:** Hot reload for fast iteration
- **Cost:** Free tier covers MVP needs
- **Ecosystem:** Mature libraries for maps (react-native-maps), Firebase integration

**Limitations mitigated:**
- Native performance: Expo Go for rapid testing, EAS for optimized builds
- Module availability: Expo managed workflow includes Firebase, Maps, etc.

---

### 2. Backend: FastAPI (Python) ✅

**Selection:** FastAPI  
**Alternatives Considered:** Node.js/Express, Django REST Framework  

**Performance Comparison:**
| Metric | FastAPI | Express | Django |
|--------|---------|---------|--------|
| Concurrent AI Inference | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Async Support | Native ASGI | Promise-based | Limited |
| ML Integration | Direct (Python) | Child processes | Django REST |
| Startup Time | 2-3s | 0.5s | 3-4s |
| Model Inference Speed | **2-3x faster** | Baseline | Baseline |

**Key Advantages:**

1. **Native Async/Await**
   - AI predictions run non-blocking using FastAPI's Starlette ASGI server
   - Prevents API timeouts during long inference operations
   - Direct asyncio integration with Python async libraries

2. **Python Ecosystem**
   - TensorFlow Lite: `from tensorflow.lite import Interpreter`
   - HuggingFace Transformers: Direct model loading
   - Scikit-learn: Direct usage without child processes
   - Express would require spawning separate Python processes (network overhead)

3. **Memory Efficiency**
   - All models (TF Lite ~200MB, Sentence-Transformers ~500MB, others ~300MB) loaded once at startup
   - Total: 1-1.5GB RAM for all models
   - Shared memory across requests (no spawning new processes per request)

4. **Real-Time WebSocket Support**
   - Native WebSocket implementation for live traffic/departure updates
   - 5 lines of code vs. complex socket.io setup in Express

5. **Automatic Request Validation**
   - Pydantic models: Type-safe input validation
   - Auto-generated OpenAPI documentation
   - Prevents malformed data from crashing AI models

6. **Development Velocity**
   - Python developers can be productive immediately
   - FastAPI syntax is intuitive and well-documented
   - Excellent authentication middleware ecosystem (python-jose, PyJWT, passlib)

**Implementation Path:**
```
Week 1-2: FastAPI scaffold + SQLAlchemy models + Firebase token verification
Week 3: API endpoints (travels, tourism, notifications)
Week 4-5: AI model integration + async inference
Week 6: WebSocket real-time features
Week 7-8: Testing + optimization
```

---

### 3. Authentication: Firebase Authentication ✅

**Selection:** Firebase Authentication  
**Alternatives Considered:** Auth0, Cognito, custom JWT  

**Why Firebase:**
- **Managed service:** No backend authentication logic required
- **Multiple auth methods:**
  - Email/password with OTP verification
  - Phone number with SMS OTP (crucial for Cameroon market)
  - Google Sign-In
  - Apple Sign-In
- **Zero backend work:** Firebase handles token refresh, session management
- **Cost:** Free tier covers MVP, pay-as-you-grow
- **Integration:** Native Firebase SDKs for React Native and web
- **Security:** Enterprise-grade security, complies with regulations

**Backend Integration:**
- FastAPI middleware: Verify Firebase ID tokens on protected routes
- Custom claims for RBAC (admin, premium, standard user)
- Sync user metadata with PostgreSQL for travel history, preferences

**User Flows:**
```
Mobile App User → Firebase Auth → Firebase ID Token
                                       ↓
                            FastAPI Middleware
                                       ↓
                            Verify token + check RBAC
                                       ↓
                            Serve API response
```

---

### 4. Maps & GIS: Google Maps API + PostGIS ✅

**Selection:** Google Maps API (primary) + PostGIS (backend queries)  
**Alternatives Considered:** Mapbox, OpenStreetMap  

**Why Google Maps:**
- **Coverage:** Best satellite imagery and street view for Cameroon/Central Africa
- **Real-time traffic:** Google's traffic prediction algorithms
- **Reliability:** Proven in regions with variable connectivity
- **Rich place data:** Restaurants, hotels, reviews near attractions
- **Tested at scale:** Used by millions of apps globally

**Specific APIs Used:**
1. **Maps JavaScript SDK** - Display maps in React Native (via react-native-maps)
2. **Routes API** - Real-time route calculation with traffic factors
3. **Places API** - Attraction discovery and enrichment
4. **Distance Matrix API** - Calculate travel times between segments
5. **Geocoding API** - Address validation for attractions
6. **Elevation API** - Terrain info for route difficulty

**PostGIS (Backend Spatial Database):**
- PostgreSQL with PostGIS extension for geographic queries
- Store geometries: Routes (LINESTRINGs), cities (POLYGONs), attractions (POINTs)
- Efficient queries: "Find attractions within 5km of route" using ST_DWithin()
- Spatial indexing: GIST and BRIN indices for sub-100ms queries

**Fallback Strategy:**
- Mapbox as premium alternative if Google quota exceeded
- OpenStreetMap for offline mapping
- MBTiles format for offline route caching

**Cost:** Google Maps pricing is per-request, set spending limits in Cloud Console

---

### 5. AI Models: TensorFlow Lite + Gemini Nano API ✅

**Selection:** Lightweight pretrained models (no custom training)

#### A. Departure Window Prediction
- **Model:** LSTM or GRU time-series network
- **Framework:** TensorFlow Lite (quantized for edge)
- **Input:** Route ID, time of day, day of week, seasonality, user patterns
- **Output:** Confidence-weighted departure time windows
- **Target:** <500ms latency, >85% accuracy
- **Source:** Pretrained model or fine-tune on historical Cameroon data

#### B. Traffic Flow Prediction
- **Model:** Graph Neural Network or LSTM
- **Framework:** TensorFlow or PyTorch converted to ONNX
- **Input:** Road segments, historical speeds, weather, events
- **Output:** Congestion probability + speed estimates per segment
- **Target:** <300ms for entire route, >80% accuracy
- **Data:** OpenStreetMap + Google Maps traffic APIs for training data

#### C. Tourist Guide Generation
- **Model:** Gemini Nano API (lightweight LLM)
- **Alternative:** Mistral 7B self-hosted (if internet unreliable)
- **Input:** Attraction ID, user language, preferences
- **Output:** Natural language travel tips, historical context, practical advice
- **Target:** <2 seconds per full guide
- **Cost:** Gemini Nano free tier, upgrade if needed

#### D. Tourism Data Curation
- **Model:** Sentence-Transformers (HuggingFace)
- **Algorithm:** Cosine similarity + DBSCAN clustering
- **Input:** User profile, visited attractions, explicit preferences
- **Output:** Ranked recommendations with relevance scores
- **Target:** <200ms for top-10 recommendations
- **Size:** ~500MB (single model handles all embeddings)

**Model Deployment Strategy:**
```
FastAPI Startup:
├── Load TensorFlow Lite models (Departure + Traffic)
├── Load Sentence-Transformers (Tourism curation)
├── Initialize Gemini Nano API client
└── Cache models in memory for request handling

Per-Request Flow:
Input Validation → Model Inference (async) → Confidence Check → Fallback if needed → Cache Result
```

**Fallback Mechanisms:**
- Confidence <60%: Return heuristic-based defaults
- API timeout: Use cached previous prediction
- Model error: Return safe defaults (e.g., "peak hours" for departures)

---

### 6. Database: PostgreSQL + PostGIS (Supabase) ✅

**Selection:** PostgreSQL with PostGIS extension on Supabase  
**Alternatives Considered:** MongoDB, DynamoDB, NeonDB  

**Why PostgreSQL + PostGIS:**
- **Spatial queries:** PostGIS extends PostgreSQL for geographic operations
- **ACID compliance:** Transactional integrity for bookings and payments
- **Full-text search:** Search attractions by description
- **JSON support:** JSONB for flexible metadata (trip details, preferences)
- **Time-series:** Native support for historical traffic/booking patterns
- **Managed:** Supabase handles backups, replication, SSL

**PostGIS Capabilities:**
```sql
-- Find attractions within 5km of route
SELECT * FROM attractions 
WHERE ST_DWithin(location, route_geometry, 5000);

-- Calculate distance along route
SELECT ST_Length(route_geometry) as distance_meters;

-- Find which city contains this point
SELECT * FROM cities 
WHERE ST_Contains(city_boundary, user_location);
```

**Core Tables with Spatial Types:**
| Table | Key Spatial Columns | Key Features |
|-------|-------------------|--------------|
| `users` | - | Firebase linked, preferences |
| `device_sessions` | - | IP tracking, session management, login history |
| `user_locations` | `location` (POINT) | GPS + device IP, activity history |
| `routes` | `route_geometry` (LINESTRING) | Route paths, geometry |
| `route_segments` | `segment_geometry` (LINESTRING) | Traffic prediction data |
| `cities` | `city_boundary` (POLYGON) | City boundaries |
| `attractions` | `location` (POINT) | Attraction locations, proximity queries |

**Supabase-Specific Benefits:**
- Row-Level Security (RLS) for user data isolation
- Real-time subscriptions (optional for V2)
- Built-in SQL editor for debugging
- Automated daily backups with 7-day retention
- Connection pooling via PgBouncer
- PostGIS pre-installed and tested

---

### 7. External Services Integration

#### Google Maps API
**Cost Model:** Pay-as-you-go (set limits in Cloud Console)
```
• Maps JS SDK: $16.50/1000 requests
• Routes API: $10/1000 requests
• Places API: $17/1000 requests
• Distance Matrix: $10/1000 requests
```
**Estimate (MVP):** 10k-50k requests/month = $50-200/month

#### Firebase Cloud Messaging (FCM)
**Cost:** Free (unlimited push notifications)
**Use:** Real-time notifications for departure delays, new attractions

#### Stripe Payments
**Cost Model:** 2.9% + $0.30 per transaction
**Why Stripe:** 
- Supports Cameroon (though limited local payment methods)
- Mobile-optimized checkout
- Webhook integration for FastAPI

#### Gemini Nano API
**Cost:** Free tier, pay-per-token for higher usage
**Estimate:** ~$0-50/month (MVP usage)

---

## Performance Architecture

### Request Flow Optimization

```
User Request
    ↓
[Vercel/Expo] Frontend
    ↓
[Railway/Fly.io] FastAPI Backend
    ├─ Firebase Token Verification (middleware)
    ├─ Database Query (PostgreSQL)
    ├─ AI Model Inference (async, non-blocking)
    │  ├─ Departure: 500ms (LSTM)
    │  ├─ Traffic: 300ms (GNN)
    │  ├─ Tourism: 200ms (embeddings)
    │  └─ Guide: 2000ms (Gemini Nano)
    ├─ Response Formatting
    └─ Return JSON
    ↓
[React Native/React] Frontend
    ↓
[Google Maps] Visualization
```

### Latency Targets

| Endpoint | AI Model | Target Latency |
|----------|----------|-----------------|
| `/api/ai/estimate-departure` | LSTM | 500ms |
| `/api/ai/traffic-prediction/{route}` | GNN | 300ms |
| `/api/ai/recommend-attractions` | Embeddings | 200ms |
| `/api/ai/tourist-guide/{attraction}` | Gemini | 2000ms |

### Scalability Roadmap

**Phase 1 (MVP - 100k users):**
- Single FastAPI instance (1-2GB RAM)
- PostgreSQL single instance (10-20GB)
- Models loaded in memory

**Phase 2 (1M users):**
- Multiple FastAPI replicas (auto-scaling)
- PostgreSQL read replicas
- Redis cache for embeddings
- Separate inference service (optional)

**Phase 3 (10M+ users):**
- Microservices: prediction, recommendation, routing services
- TensorFlow Serving for model management
- Kubernetes orchestration

---

## Development Environment Setup

### Local Development
```bash
# Backend
python -m venv venv
pip install fastapi uvicorn sqlalchemy pydantic tensorflow 
uvicorn main:app --reload

# Frontend (React Native)
npx expo init ai-imutis-app
npm install react-native-maps @react-navigation/native firebase

# Database (via Docker)
docker run -e POSTGRES_PASSWORD=password postgres:15-alpine
```

### CI/CD Pipeline (GitHub Actions)
```yaml
on: [push, pull_request]

jobs:
  backend-test:
    - Lint (pylint)
    - Unit tests (pytest)
    - Build Docker image
    - Push to registry
    
  frontend-test:
    - ESLint check
    - Unit tests (Jest)
    - Build (Expo)
```

---

## Cost Estimation (Monthly)

| Service | Free Tier | Estimated Cost |
|---------|-----------|-----------------|
| Firebase Auth | 10k identities | Free* |
| Google Maps API | - | $50-200 |
| Gemini Nano API | Free tier | Free-50 |
| PostgreSQL (Supabase) | 500MB | Free* |
| FastAPI Hosting (Railway) | - | $5-20 |
| React Hosting (Vercel) | 100GB/month | Free |
| **Total** | | **$55-270/month** |

*With free tier limits; upgrade as needed

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|-----------|
| Google Maps API quota exceeded | Mapbox fallback, offline MBTiles, request caching |
| AI model latency high | Lighter models (DistilBERT), caching, fallback heuristics |
| PostgreSQL performance | PostGIS spatial indexing, query optimization, caching |
| Firebase outage | 15-minute cache, graceful degradation |
| Network latency in Cameroon | Offline support, request batching, edge caching |
| Device spoofing/fraud | IP tracking validation, device fingerprinting, rate limiting per IP |
| Session hijacking | IP rotation detection, device change alerts, re-authentication |

#### Operational Risks

| Risk | Mitigation |
|------|-----------|
| Model staleness | Feedback loop for accuracy tracking, A/B testing |
| Data quality | Input validation, user feedback, periodic audits |
| Security | Firebase managed auth, SQLAlchemy ORM, HTTPS only, device IP tracking |
| Cost overruns | Cloud spending limits, usage monitoring, auto-scaling |
| Privacy concerns | Data encryption, RLS policies, GDPR compliance, IP anonymization after 90 days |

---

## Conclusion

**FastAPI as backend** provides the optimal balance of:
- ✅ Performance (2-3x faster AI inference)
- ✅ Developer velocity (Python ecosystem)
- ✅ Operational simplicity (single Docker container)
- ✅ Cost efficiency (no infrastructure complexity)

**React Native + Expo** ensures:
- ✅ Rapid cross-platform deployment
- ✅ Code sharing with web dashboard
- ✅ Access to native device capabilities

**Google Maps + PostGIS** delivers:
- ✅ Best-in-class mapping for Cameroon
- ✅ Sophisticated geographic queries
- ✅ Proven reliability at scale

This stack is **production-ready** and scales from MVP (100k users) to enterprise (10M+ users).

---

**Document Version:** 1.0  
**Prepared by:** AI-IMUTIS Technical Team  
**Approved:** December 26, 2025
