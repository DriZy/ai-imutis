# Comprehensive Implementation Prompt
## AI-IMUTIS: AI-Assisted Inter-Urban Mobility and Urban Tourism Information System

---

## PROJECT 1: AI-IMUTIS (AI-Assisted Inter-Urban Mobility and Urban Tourism Information System)

### 1.1 Project Overview
**Title:** AI-Assisted Inter-Urban Mobility and Urban Tourism Information System (AI-IMUTIS) for Cameroon  
**Institution:** College of Technology, University of Buea  
**Program:** M.Tech – Software Engineering  
**Team Members:**
- Gena Norman Kamando
- Tabi Idris Nfongang
- Bakiambu Rose Eneke

### 1.2 Problem Statement & Context

#### Inter-Urban Mobility Challenges
- No structured digital visibility of estimated travel windows
- Manual decision-making and unpredictable waiting times
- Fragmented information across transport agencies
- Inconsistent departure times and informal communication channels
- Limited digital access to travel information

#### Urban Tourism Challenges
- Incomplete or outdated digital information on attractions
- Limited centralised digital resources for visitors
- Fragmented tourism information across cities
- Low visibility of tourist attractions

### 1.3 Project Objectives

#### Technical Objectives
1. **AI Integration:** Integrate an existing lightweight pretrained AI model (TensorFlow, OpenAI, or Gemini Nano API)
2. **Travel Window Estimation:** Generate approximate departure window suggestions using AI
3. **Tourism Information:** Provide curated urban tourism information for major Cameroonian cities
4. **Modular Architecture:** Implement modular architecture with clear separation of concerns:
   - Frontend Layer
   - Backend API Layer
   - AI Microservice Layer
   - Database Layer
5. **DevOps & Cloud:** Demonstrate DevOps workflows and cloud deployment practices
6. **Software Engineering:** Apply advanced software engineering principles throughout

#### Academic & Entrepreneurial Objectives
- Improve accessibility of travel information for end-users
- Support urban tourism visibility and discoverability
- Demonstrate scalability potential in an academic setting
- Showcase competencies in architecture, DevOps, and AI integration

### 1.4 Project Scope

#### Included Deliverables
- **Frontend UI:** React or Flutter-based responsive interface
- **Backend API:** Node.js/Express or FastAPI RESTful API
- **AI Microservice:** Python-based service using existing pretrained models
- **Database:** PostgreSQL relational database
- **Notifications:** Simple reminders/notifications system
- **CI/CD Pipeline:** GitHub Actions for automated testing and deployment
- **Cloud Deployment:** Free-tier cloud services deployment
- **Documentation:** Comprehensive system documentation and architecture diagrams

#### Out of Scope
- Custom AI model training
- Real-time geolocation tracking
- Payment processing
- Advanced analytics

### 1.5 Detailed Technical Requirements

#### 1.5.1 Frontend Layer
**Technology Stack:** React Native with Expo (mobile) + React.js (web dashboard)
**Platform:** iOS and Android with responsive web fallback
**Authentication:** Firebase Authentication
**Features:**
- Firebase auth (email, phone OTP, Google Sign-In, Apple Sign-In)
- Search functionality for inter-urban travels with Google Maps integration
- Real-time departure window estimation display
- City-based tourism information browsing with map visualization
- Cross-platform native performance (iOS/Android)
- Push notifications via Firebase Cloud Messaging
- User profile, booking history, and saved preferences
- Offline support for critical features (cached routes/attractions)
- Device IP tracking for user location and device identification
- Session tracking using mobile device IP address

**Requirements:**
- Clean, intuitive native UI/UX following iOS/Android guidelines
- Accessibility compliance (WCAG 2.1 equivalent for web, iOS/Android standards for mobile)
- Performance optimization (code splitting, lazy loading, caching with AsyncStorage)
- Error handling and user feedback mechanisms
- Camera access for document/profile verification
- Location permissions for map-based features (background location for drivers)
- Gesture navigation and platform-specific interactions

#### 1.5.2 Backend API Layer
**Technology Stack:** FastAPI (Python)
**Rationale - Why FastAPI over Node.js/Express:**
FastAPI provides superior performance for AI/ML-heavy workloads with native async support. Key advantages for this project:
- **Performance:** 2-3x faster request handling for concurrent AI model inference vs. Express
- **Async Native:** Built-in async/await for non-blocking AI predictions and database queries
- **AI Integration:** Seamless ecosystem with TensorFlow, scikit-learn, Hugging Face transformers
- **Memory Efficiency:** Better garbage collection for loaded ML models
- **Real-Time:** WebSocket support for live traffic updates and notifications
- **Validation:** Automatic request validation via Pydantic (reduces boilerplate)
- **Auto-Docs:** Self-generating OpenAPI/Swagger documentation
- **Scalability:** Proven at production scale with proper ASGI server (Uvicorn + Gunicorn)

**Architecture Pattern:** RESTful API with WebSocket support for real-time features

**API Documentation:** Automatic OpenAPI/Swagger documentation
- **Swagger UI:** Available at `/docs` (interactive API testing)
- **ReDoc:** Available at `/redoc` (clean documentation interface)
- **OpenAPI Schema:** Available at `/openapi.json` (machine-readable spec)
- **Auto-generated:** All endpoints documented automatically via Pydantic models
- **Authentication:** Swagger UI supports Firebase token testing

**Core Endpoints:**
- **Travel Routes:**
  - `GET /api/travels` - List available routes
  - `POST /api/travels/estimate` - Get departure window estimation
  - `GET /api/travels/{routeId}` - Get route details
  - `POST /api/travels/book` - Book a travel

- **Tourism:**
  - `GET /api/cities` - List available cities
  - `GET /api/cities/{cityId}/attractions` - Get attractions in a city
  - `GET /api/attractions/{attractionId}` - Get attraction details
  - `POST /api/attractions/search` - Search attractions

- **User Management (Firebase-managed auth):**
  - `POST /api/auth/verify-token` - Verify Firebase ID token
  - `GET /api/users/profile` - Get user profile metadata
  - `PUT /api/users/profile` - Update profile (preferences, language)
  - `DELETE /api/users/account` - Account deletion with cascade cleanup
  - `POST /api/users/preferences` - Save notification and language preferences
  - `GET /api/users/sessions` - Get all active device sessions with IP addresses
  - `DELETE /api/users/sessions/{session_id}` - Revoke specific device session
  - `POST /api/users/locations/track` - Record current location with device IP

- **Notifications:**
  - `GET /api/notifications` - List user notifications
  - `POST /api/notifications/subscribe` - Subscribe to alerts
  - `DELETE /api/notifications/{notificationId}` - Dismiss notification
  - `WS /api/ws/user/{user_id}/notifications` - Real-time notification stream

**Requirements:**
- Pydantic models for automatic request validation and OpenAPI schema generation
- Comprehensive async error handling with intelligent retry logic for transient failures
- Input sanitization for security (SQL injection prevention, XSS protection)
- Firebase token verification middleware on protected endpoints
- **Security Implementation (see SECURITY_GUIDE.md for complete details):**
  - **Rate Limiting:** Multi-tier with Redis (10-500 req/min based on user tier)
  - **Throttling:** Adaptive DDoS protection with IP blocking (>100 req/5min)
  - **Input Validation:** Sanitize all inputs (HTML, SQL, path traversal)
  - **SQL Injection Prevention:** Use parameterized queries only
  - **Authentication:** Firebase token verification with device binding
  - **Session Security:** Device-bound sessions with IP rotation detection
  - **CORS:** Whitelist specific origins only
- **Device IP tracking middleware:**
  - Capture client IP address from X-Forwarded-For header (proxy-aware)
  - Store device IP in device_sessions table for every request
  - Track session continuity using IP + Firebase UID combination
  - Implement IP rotation detection for security
- **Swagger/OpenAPI Configuration:**
  ```python
  from fastapi import FastAPI
  from fastapi.openapi.utils import get_openapi
  
  app = FastAPI(
      title="AI-IMUTIS API",
      description="Inter-Urban Mobility and Tourism Information System",
      version="1.0.0",
      contact={
          "name": "AI-IMUTIS Team",
          "email": "support@ai-imutis.com",
      },
      license_info={
          "name": "MIT",
      },
      docs_url="/docs",
      redoc_url="/redoc",
      openapi_url="/openapi.json",
  )
  
  # Custom OpenAPI schema with security
  def custom_openapi():
      if app.openapi_schema:
          return app.openapi_schema
      openapi_schema = get_openapi(
          title="AI-IMUTIS API",
          version="1.0.0",
          description="Complete API for mobility and tourism management",
          routes=app.routes,
      )
      openapi_schema["components"]["securitySchemes"] = {
          "FirebaseAuth": {
              "type": "http",
              "scheme": "bearer",
              "bearerFormat": "JWT",
              "description": "Firebase ID Token",
          }
      }
      app.openapi_schema = openapi_schema
      return app.openapi_schema
  
  app.openapi = custom_openapi
  ```
  - Log IP changes per session for fraud detection
- Role-based access control (RBAC) stored in database (admin, premium, standard)
- Structured logging to cloud logging service (Cloud Logging, DataDog, or Sentry)
- Redis-based rate limiting (100 requests/min standard tier, 1000 for premium)
- Auto-generated Swagger/OpenAPI documentation from code annotations
- CORS configuration for React Native and web app origins
- Request ID tracking for distributed tracing across services
- Graceful degradation when external services (Google Maps, Gemini API) are unavailable

#### 1.5.3 AI Model Layer (Integrated in FastAPI Backend)
**Technology Stack:** Python with TensorFlow Lite, HuggingFace Transformers, Gemini Nano API

**AI Endpoints:**
- `POST /api/ai/estimate-departure` - Predict optimal departure windows using LSTM time-series model
- `GET /api/ai/traffic-prediction/{route_id}` - Real-time traffic prediction for route segments
- `POST /api/ai/recommend-attractions` - Personalized attraction recommendations using semantic embeddings
- `POST /api/ai/tourist-guide/{attraction_id}` - AI-generated contextual travel tips using text generation
- `GET /api/ai/tourism-suggestions/{city_id}` - Curated tourism content using clustering and ranking
- `POST /api/ai/analyze-travel-pattern` - Pattern analysis for repeat travelers
- `WS /api/ws/route/{route_id}/traffic` - WebSocket for live traffic prediction updates
- `GET /ai/models/status` - Model health, version, and resource usage

**Specific AI Models:**

1. **Departure Window Prediction (LSTM/GRU)**
   - Input: Historical route data, time of day, day of week, seasonality
   - Output: Confidence-weighted departure time windows
   - Framework: TensorFlow Lite (quantized for mobile inference)
   - Latency target: <500ms for prediction

2. **Traffic Flow Prediction (Graph Neural Network or LSTM)**
   - Input: Historical traffic patterns, road segments, weather, special events
   - Output: Congestion probability and speed estimates by segment
   - Framework: TensorFlow or PyTorch, converted to ONNX for portability
   - Latency target: <300ms for entire route prediction

3. **Tourist Guide Generation (Fine-tuned LLM)**
   - Input: Attraction ID, user language, user preferences
   - Output: Natural language travel tips, historical context, practical advice
   - Model: Google Gemini Nano API (lightweight) or Mistral 7B (self-hosted)
   - Latency target: <2 seconds for full guide generation

4. **Tourism Data Curation (Semantic Embeddings + Clustering)**
   - Input: User profile, visited attractions, preferences
   - Output: Ranked recommendations with relevance scores
   - Model: Sentence-Transformers (HuggingFace) for embeddings
   - Algorithm: Cosine similarity + DBSCAN clustering
   - Latency target: <200ms for top-N recommendations

**Requirements:**
- Models loaded into memory at startup with locking to prevent race conditions
- Async inference queue for non-blocking predictions using asyncio
- Input validation and sanitization for adversarial protection
- Output confidence scoring with fallback heuristics when confidence <60%
- Model versioning (semantic versioning, switchable via environment variable)
- Batch prediction support for bulk requests
- Monitoring: Request latency, model accuracy (via feedback), resource usage (CPU, memory)
- Fallback mechanisms: Return heuristic-based defaults if model fails

#### 1.5.3.5 Geospatial Services & Mapping
**Primary Map Service:** Google Maps API
**Justification for Cameroon Context:**
- Superior satellite imagery and street view coverage for Central Africa
- Reliable real-time traffic data and prediction algorithms
- Proven performance in developing regions with varying connectivity
- Route optimization with real-time traffic factors
- Rich place search and business information (restaurants, hotels near attractions)

**Specific APIs Used:**
- **Maps JavaScript SDK:** Display maps in web and React Native (via `react-native-maps`)
- **Routes API:** Real-time route calculation with traffic-aware recommendations
- **Places API:** Attraction discovery, place details, and reviews
- **Distance Matrix API:** Calculate travel times between multiple route segments
- **Geocoding API:** Convert addresses to coordinates for attraction data enrichment
- **Elevation API:** Terrain information for route difficulty assessment

**Fallback Strategy:**
- OpenStreetMap + Leaflet.js as backup for map rendering (open-source)
- Mapbox as premium alternative if Google Maps quota exceeded
- Offline map tiles (MBTiles format) for critical inter-urban routes

**PostGIS Integration (Spatial Database):**
- PostgreSQL with PostGIS extension for geographic queries
- Store route geometries (LINE strings), city boundaries (POLYGONs), attraction locations (POINTs)
- Spatial indexing (GIST and BRIN) for efficient distance and containment queries
- Example queries:
  - "Find all attractions within 5km of route" → ST_DWithin()
  - "Find which city contains this coordinate" → ST_Contains()
  - "Calculate driving distance along route" → ST_Length(geometry)

**GIS Implementation:**
- Frontend uses Google Maps for UI, backend uses PostGIS for spatial logic
- Store attraction locations with high precision (PostGIS POINT)
- Route segments with elevation profiles stored as LINESTRINGs
- Distance calculations done in PostGIS before sending to frontend

#### 1.5.4 Database Layer
**Technology Stack:** PostgreSQL with PostGIS

**Core Tables:**
- `users` - User accounts and profiles
  - Firebase UID as primary identifier
  - Phone number, language preferences, notification settings
- `device_sessions` - Device IP tracking and session management
  - Mobile device IP address (IPv4/IPv6)
  - Device fingerprint/identifier
  - Session start/end timestamps
  - Last activity timestamp
  - Device type, OS version, app version
- `user_locations` - Location history with IP tracking
  - Timestamp, latitude/longitude (from GPS or network-based location)
  - Device IP address at time of location
  - Route ID (if traveling)
  - Accuracy radius
- `routes` - Inter-urban travel routes (with geometry)
  - `route_geometry` (LINE geometry type via PostGIS)
  - Origin/destination cities with coordinates
  - Route characteristics (distance, terrain, estimated duration)
- `route_segments` - Detailed segment data for AI predictions
  - Segment geometry, historical speed data
  - Traffic patterns by time-of-day and day-of-week
- `cities` - City information with geographic boundaries
  - `city_boundary` (POLYGON geometry for spatial queries)
  - Population, climate zone, key statistics
- `attractions` - Tourism attractions with rich metadata
  - `location` (POINT geometry for proximity queries)
  - Category, rating, opening hours, images, entry fees
  - AI-generated descriptions and tags
- `bookings` - Travel bookings with prediction tracking
  - Booking status, departure time, actual arrival vs. prediction
  - Device IP at booking time
  - Actual vs. predicted departure (feedback for model training)
- `travel_patterns` - Analytics table for machine learning
  - Historical travel data for training departure and traffic models
  - Patterns indexed by route, time, user behavior
- `notifications` - System notifications and delivery status
  - Delivery status, read/unread flags, Firebase token tracking
  - Device IP for delivery verification
- `ai_predictions` - Audit log of all AI model outputs
  - Timestamp, model version, input data, prediction, confidence score
  - User feedback on prediction accuracy (for continuous improvement)

**Requirements:**
- PostGIS spatial indexing (GIST/BRIN) for efficient geographic queries
- Foreign key constraints with CASCADE delete where appropriate
- Data integrity checks and uniqueness constraints
- Audit trail for critical operations (bookings, payments, user data changes)
- Time-series data partitioning for predictions table (monthly partitions for performance)
- Automated backup and point-in-time recovery (Supabase handles this daily)
- Row-level security (RLS) policies for user data isolation
- Indexing on frequently queried columns (route_id, user_id, created_at)

#### 1.5.5 Authentication & Security Layer
**Technology:** Firebase Authentication (Cloud service)

**Features:**
- Email/password authentication with verification
- Phone number authentication with OTP via SMS
- Google Sign-In (mobile and web)
- Apple Sign-In (iOS platform requirement)
- Persistent session management with automatic token refresh
- Multi-device login tracking and session revocation
- **Device IP address tracking for each session**

**Device IP Tracking Implementation:**
- Capture X-Forwarded-For header from HTTP requests (proxy-aware)
- Store device IP in device_sessions table on every authenticated request
- Track session using combination of Firebase UID + device IP
- Detect and log IP rotation for anomaly detection
- Implement rate limiting per device IP (100 req/min standard)
- Allow users to view all active sessions with device IPs
- Provide one-click device/session revocation from mobile app
- Alert users on new device login attempts

**Backend Integration with FastAPI:**
- Verify Firebase ID tokens in middleware for all protected routes
- Extract client IP using: `request.client.host` or `X-Forwarded-For` header
- Store device IP, user agent, and last activity in database
- Implement custom claims for RBAC (admin, premium, standard user)
- Secure cookie-based session handling for web frontend (httpOnly, Secure flags)
- Token refresh strategy: Client requests new ID token before expiration
- Track session continuity and device changes

**Security Requirements:**
- Enforce HTTPS for all communication (strict-transport-security headers)
- Firebase security rules for Firestore (if used)
- Rate limiting on authentication attempts (5 failed logins → 30 min lockout per IP)
- IP-based fraud detection (alert on unusual geographic patterns)
- Optional 2FA implementation for premium users (TOTP)
- Data encryption at rest (PostgreSQL) and in transit (TLS 1.3)
- Device IP logging for compliance and security investigation
- Regular security audits and penetration testing (quarterly minimum)

### 1.6 Software Engineering Principles

#### Code Quality
- **Clean Code:** Follow SOLID principles and design patterns
- **Code Style:** Consistent formatting, naming conventions
- **DRY Principle:** Avoid code duplication
- **Documentation:** Inline comments for complex logic, docstrings for functions

#### Testing Strategy
- **Unit Tests:** Minimum 80% code coverage
- **Integration Tests:** API endpoint testing
- **AI Output Validation:** Verify AI predictions meet business logic
- **End-to-End Tests:** Complete user workflows
- **Load Testing:** Performance under expected load

#### Error Handling
- Graceful error messages to users
- Proper HTTP status codes
- Detailed server-side logging
- Exception handling at all layers

#### API Documentation
- Swagger/OpenAPI specification
- Clear endpoint descriptions
- Request/response examples
- Authentication requirements
- Rate limiting information

### 1.7 DevOps & Cloud Architecture

#### Version Control
- **Repository:** Git + GitHub
- **Branching Strategy:** Git Flow (main, develop, feature/*, hotfix/*)
- **Commit Message:** Conventional Commits (feat:, fix:, docs:, etc.)
- **Pull Request Process:** Code review mandatory before merge

#### Containerization
- **Docker:** Containerize all services
- **Docker Compose:** Local development environment
- **Container Registry:** Docker Hub or GitHub Container Registry

#### CI/CD Pipeline (GitHub Actions)
**Workflow Stages:**
1. **Trigger:** On push to develop/main, on PR
2. **Checkout:** Clone repository
3. **Dependencies:** Install project dependencies
4. **Linting:** ESLint/Pylint for code quality
5. **Testing:** Run all test suites with coverage reports
6. **Build:** Build application artifacts and Docker images
7. **Push:** Push images to registry
8. **Deploy:** Deploy to cloud services

**Deployment Environments:**
- Development: Auto-deploy on develop branch
- Staging: Manual approval before deploy
- Production: Manual approval from main branch

#### Cloud Deployment Architecture

**Frontend Deployment:**
- **Platform:** Vercel (React web) or Netlify
n- **Mobile:** Expo EAS Build for iOS/Android distribution
- **Configuration:** Automatic deployment on Git push
- **CDN:** Global content delivery network
- **Environment secrets:** Managed via Vercel dashboard (Firebase config, Google Maps key)

**Backend Deployment (FastAPI):**
- **Platform:** Railway or Fly.io (both have excellent Python support)
- **Server:** Gunicorn + Uvicorn for ASGI (async) operation
- **Containerization:** Docker image built and deployed automatically on push
- **Auto-scaling:** Based on CPU usage (70%) and memory (80%)
- **Health Checks:** `/api/health` endpoint monitoring database, model cache, external services
- **Zero-downtime Deployments:** Blue-green or rolling update strategy
- **Environment Variables:** Firebase service account, Google Maps API key, Stripe key via secrets
- **WebSocket Support:** Both Railway and Fly.io support persistent WebSocket connections

**AI Models Deployment:**
- **Models Hosting:** TensorFlow Lite and other models bundled in Docker image
- **Memory Requirements:** 1-1.5GB RAM for all models loaded in memory
- **Model Inference:** Direct in FastAPI process (no separate microservice needed for MVP)
- **Timeout Configuration:** 30-second timeout for complex predictions, 5-second for simple
- **Async Inference Queue:** Celery + Redis for long-running predictions (optional for V2)
- **Model Versioning:** Semantic versioning in code, switchable via environment variable
- **GPU Support:** Optional for production scale-up (Fly.io GPU pricing available)

**Database Deployment:**
- **Platform:** Supabase or NeonDB (both are PostgreSQL + PostGIS compatible)
- **PostGIS Extension:** Enabled by default on Supabase/NeonDB
- **Automatic Backups:** Daily backups with 7-day point-in-time recovery
- **Connection Pooling:** PgBouncer via Supabase to prevent connection exhaustion
- **SSL/TLS:** Enforced encrypted connections
- **Row-Level Security:** RLS policies for user data isolation

**Firebase Integration:**
- **Authentication:** Fully managed by Firebase (no backend work)
- **Cloud Messaging:** FCM for push notifications (integrated with app frontend)
- **Realtime Database (optional):** For real-time features in V2
- **Storage:** Firebase Storage for user profile images and attraction photos

**External Service Integration:**
- **Google Maps API:** Billed by usage, set spending limits in Cloud Console
- **Gemini Nano API:** Free tier available, upgrade for higher usage
- **Stripe Payments:** Webhook receiver endpoint in FastAPI (secured with signature verification)
- **SendGrid/Twilio:** Email and SMS for notifications (optional alternative to FCM)

#### Infrastructure as Code (IaC)
- **Tool:** Terraform (minimal configuration)
- **VCS Integration:** Infrastructure changes in Git
- **Environment Management:** Separate tfvars for dev/staging/prod

#### Monitoring & Logging
- **Cloud Logs:** Built-in platform logging
- **Error Tracking:** Sentry or Rollbar (optional)
- **Performance Monitoring:** Application Performance Monitoring (APM)
- **Metrics Dashboard:** Prometheus/Grafana (local setup optional)
- **Alerts:** Notifications for critical errors or performance degradation

### 1.8 Implementation Methodology

#### SDLC Phases (Linear Iterative)
1. **Requirements Analysis:** Define detailed requirements (Week 1-2)
2. **Architecture Design:** Design system architecture and data models (Week 3)
3. **Module Development:** Develop each component independently (Week 4-8)
4. **Integration:** Combine components and ensure compatibility (Week 9)
5. **Testing:** Comprehensive testing across all levels (Week 10)
6. **Deployment:** Deploy to cloud infrastructure (Week 11)
7. **Documentation:** Complete documentation and diagrams (Week 12)

#### Development Workflow
- Agile sprint-based approach (2-week sprints)
- Daily standups for team synchronization
- Weekly code reviews and knowledge sharing
- Continuous integration and deployment

### 1.9 Expected Deliverables

#### Documentation
- [ ] Comprehensive project report (10-15 pages)
- [ ] Software Requirements Specification (SRS)
- [ ] Software Design Document (SDD)
- [ ] Architecture diagrams (C4 model)
- [ ] Database schema diagram
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Deployment guide
- [ ] User manual
- [ ] Developer guide

#### Code & Repository
- [ ] Complete source code on GitHub
- [ ] README with setup instructions
- [ ] Docker configuration files
- [ ] CI/CD workflow definitions
- [ ] Environment configuration templates
- [ ] Database migration scripts

#### Deployment
- [ ] Hosted working prototype (frontend + backend + AI service)
- [ ] Cloud infrastructure setup
- [ ] Monitoring and logging configured
- [ ] Backup and recovery procedures documented

#### Testing
- [ ] Unit test results with coverage report
- [ ] Integration test results
- [ ] AI model validation tests
- [ ] Load testing results
- [ ] User acceptance test cases

#### AI Integration & Model Specifics
- [ ] **Departure Window Prediction Model:**
  - [ ] LSTM/GRU time-series model trained on historical route data
  - [ ] Input: time of day, day of week, route conditions, user preferences
  - [ ] Output: Optimal departure time windows with confidence scores
  - [ ] Performance target: <500ms latency, >85% prediction accuracy
  
- [ ] **Traffic Flow Prediction Model:**
  - [ ] Graph Neural Network or LSTM on historical traffic patterns
  - [ ] Input: road segments, historical speeds, weather, events, time patterns
  - [ ] Output: Congestion probability and speed estimates per segment
  - [ ] Performance target: <300ms for full route, >80% accuracy
  
- [ ] **Tourist Guide Generation (LLM):**
  - [ ] Google Gemini Nano API or Mistral 7B fine-tuned model
  - [ ] Input: Attraction ID, user language, preferences, context
  - [ ] Output: Natural language travel tips, historical info, practical advice
  - [ ] Performance target: <2 seconds per full guide
  
- [ ] **Tourism Data Curation (Embeddings + Clustering):**
  - [ ] Sentence-Transformers for semantic embeddings
  - [ ] Cosine similarity ranking + DBSCAN clustering
  - [ ] Input: User profile, travel history, explicit preferences
  - [ ] Output: Personalized ranked attraction recommendations
  - [ ] Performance target: <200ms for top-10 recommendations
  
- [ ] **Model Serving & Monitoring:**
  - [ ] Models loaded at startup with version tracking
  - [ ] Async inference queue implementation
  - [ ] Input/output validation with confidence thresholds
  - [ ] Fallback heuristics when model confidence <60%
  - [ ] Feedback loop for continuous improvement
  - [ ] A/B testing framework for model updates





---

## TECHNICAL STACK SUMMARY

### AI-IMUTIS Stack
| Layer | Technology | Rationale |
|-------|-----------|----------|
| Mobile Frontend | React Native + Expo | Cross-platform (iOS/Android), rapid deployment, shared codebase |
| Web Dashboard | React.js | Admin panel for content management and stakeholder monitoring |
| Backend API | FastAPI (Python) | 2-3x faster AI inference than Node.js, native async, ML ecosystem |
| Authentication | Firebase Authentication | Managed auth, no backend burden, social logins, SMS OTP |
| Maps/GIS | Google Maps API + PostGIS | Best Cameroon coverage, real-time traffic, spatial queries |
| AI Models | TensorFlow Lite + Gemini Nano | Lightweight, pre-trained, edge-compatible for production |
| Database | PostgreSQL + PostGIS (Supabase) | Spatial queries, time-series, ACID compliance, managed backups |
| Payments | Stripe via FastAPI webhook | PCI-compliant, local currency support |
| Notifications | Firebase Cloud Messaging | Cross-platform push notifications |
| DevOps | Docker + GitHub Actions | Containerization, automated CI/CD |
| Backend Hosting | Railway or Fly.io | Python support, auto-scaling, WebSocket enabled |
| Frontend Hosting | Vercel (web), Expo EAS (mobile) | Optimal React/React Native deployment |
| Monitoring | Datadog or New Relic APM | AI latency tracking, API performance |
| Error Tracking | Sentry | Real-time error monitoring |

### Development Tools
- **Version Control:** Git/GitHub with conventional commits and Git Flow
- **IDE:** VS Code (all), PyCharm (Python backend), Xcode (iOS testing)
- **Frontend Testing:** Jest (React), Detox (React Native E2E), React Native Testing Library
- **Backend Testing:** Pytest (unit tests), FastAPI TestClient (integration), Locust (load testing)
- **API Documentation:** Auto-generated Swagger via FastAPI, Postman collections
- **Database Tools:** pgAdmin, Supabase Studio, QGIS (PostGIS visualization)
- **AI/ML:** TensorFlow Lite Inspector, ONNX Model Visualizer, Weights & Biases (experiment tracking)
- **Mobile Emulation:** Android Emulator, iOS Simulator, Expo Go for rapid testing
- **Performance:** Lighthouse (web), Firebase Performance Monitoring (mobile), Py-Spy (Python profiling)
- **DevOps:** Docker Desktop, Railway CLI, Fly.io CLI for local deployment simulation

---

## BACKEND TECHNOLOGY CHOICE: FASTAPI vs NODE.JS/EXPRESS

### Why FastAPI is Superior for AI-IMUTIS

#### Performance Metrics
| Metric | FastAPI | Node.js/Express | Winner |
|--------|---------|-----------------|--------|
| Concurrent AI Requests | 2-3x faster | Baseline | FastAPI |
| Memory for ML Models | 20-30% less | Baseline | FastAPI |
| Async Operations | Native support | Callback/Promise | FastAPI |
| Startup Time | ~2s (with models) | ~1s | Express |
| Model Inference | Non-blocking | Blocking risk | FastAPI |

#### Technical Advantages

**1. Async/Await for AI Workloads**
- FastAPI: Native async with ASGI server (Uvicorn)
- Express: Event-driven but callbacks can block the event loop
- Impact: AI predictions run non-blocking in FastAPI, preventing API timeouts

**2. Python Ecosystem for ML**
- FastAPI has direct imports: `from tensorflow.lite import interpreter`
- Express would require child processes for Python models (extra overhead)
- Scientific computing libraries (NumPy, Pandas, Scikit-learn) are native Python

**3. Memory Efficiency for Loaded Models**
- TensorFlow Lite (~200MB), Sentence-Transformers (~500MB), Gemini Nano (~300MB)
- FastAPI: All models in single Python process, shared memory
- Express: Would require separate Python processes or HTTP calls (network overhead)

**4. WebSocket Native Support**
- FastAPI: WebSockets in 5 lines of code
- Express: Requires additional libraries (socket.io complexity)
- Use case: Real-time traffic updates, live departure window changes

**5. Request Validation with Pydantic**
- FastAPI: Automatic request validation, OpenAPI docs generated from code
- Express: Manual validation or additional libraries (Joi, Yup)
- Benefit: Type safety prevents AI model crashes from bad inputs

#### Performance Benchmarks

**Scenario: 100 concurrent requests, each triggers AI inference (500ms)**
- FastAPI: All handled concurrently, total time ~5 seconds
- Express: Single-threaded, sequential processing, total time ~50 seconds

**Scenario: 1000 daily AI predictions across 4 endpoints**
- FastAPI: Uses ~300MB RAM (models loaded once)
- Express: Could spike to 1.5GB (spawning Python subprocesses repeatedly)

#### Implementation Cost Analysis

**FastAPI Setup Time:** ~2 weeks
- Familiar syntax for Python developers
- Existing authentication middleware (python-jose, PyJWT)
- SQLAlchemy for database (mature, stable)

**Express + Python Integration:** ~3-4 weeks
- Extra complexity managing child processes
- Network overhead between Node and Python services
- Deployment complexity (managing two runtime environments)

### Architecture Recommendation

```
┌─────────────────────────────────────────┐
│  React Native/React Frontends           │
└────────────┬────────────────────────────┘
             │
    ┌────────▼─────────────────┐
    │ FastAPI Backend Server   │
    ├──────────────────────────┤
    │ • Authentication (JWT)   │
    │ • API Logic              │
    │ • Database (SQLAlchemy)  │
    │ • AI Inference (Async)   │
    │ • WebSocket Streams      │
    └────────┬───────────────┬─┘
             │               │
      ┌──────▼──────┐   ┌───▼──────────────┐
      │ PostgreSQL  │   │ External APIs    │
      │ + PostGIS   │   │ • Google Maps    │
      │             │   │ • Gemini Nano    │
      │             │   │ • Firebase       │
      └─────────────┘   │ • Stripe         │
                        └──────────────────┘
```

This single-service architecture with FastAPI:
- Simplifies deployment (one Docker image)
- Reduces operational overhead
- Enables tight coupling of AI models with business logic
- Scales vertically before needing horizontal scaling

### Migration Path (Future Scaling)

If demand exceeds FastAPI capacity, evolution path:
1. **Phase 1 (Current):** Monolithic FastAPI with embedded AI models
2. **Phase 2 (100k+ DAU):** Separate AI inference service with TensorFlow Serving (optional)
3. **Phase 3 (1M+ DAU):** Microservices with separate recommendation, prediction, and route services

---

### AI-IMUTIS
- ✅ Modular architecture with clear separation of concerns
- ✅ Integrated pretrained AI model with validated outputs
- ✅ Hosted prototype accessible to stakeholders
- ✅ CI/CD pipeline with automated testing and deployment
- ✅ Comprehensive documentation and diagrams
- ✅ 80%+ test coverage
- ✅ Clean, maintainable code
- ✅ Performance meets acceptance criteria


---

## REVISION & APPROVAL

**Document Version:** 1.0  
**Created:** December 26, 2025  
**Last Updated:** December 26, 2025  
**Status:** Ready for Implementation  

**Prepared by:** [Your Name/Team]  
**Approved by:** [Stakeholder Approval]  
**Next Review:** [30 days from implementation start]

---

*This comprehensive prompt serves as the authoritative guide for implementing the AI-IMUTIS initiative. All team members should reference this document throughout the project lifecycle.*
