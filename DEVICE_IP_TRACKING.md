# Device IP Tracking Implementation Guide

**Document Version:** 1.0  
**Date:** December 26, 2025  
**Status:** ✅ Integrated into AI-IMUTIS Architecture

---

## Overview

Mobile device IP tracking has been integrated throughout the AI-IMUTIS system to provide:
- Session management and multi-device tracking
- Device identification and fraud detection
- Location-based analytics
- Security monitoring and IP rotation detection
- User activity auditing

---

## Database Schema Changes

### 1. Device Sessions Table

```sql
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
```

**Purpose:**
- Track every active session for each user
- Store device IP address and device metadata
- Monitor IP rotation (potential security issue)
- Maintain session lifecycle (start, last activity, end)

**Key Fields:**
- `device_ip`: Mobile device's IP address (IPv4 or IPv6)
- `device_fingerprint`: Unique device identifier (vendor + model + OS)
- `ip_rotation_detected`: Flag when IP changes unexpectedly
- `ip_changes`: Counter for how many times IP changed in session
- `is_active`: Boolean to mark active vs. terminated sessions

---

### 2. User Locations Table

```sql
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
```

**Purpose:**
- Record GPS location with corresponding device IP
- Track user movement and route adherence
- Support geospatial analytics and heatmaps
- Link location to specific session

**Key Fields:**
- `location`: PostGIS POINT for geographic queries
- `device_ip`: IP address when location was recorded
- `device_session_id`: Link to specific device session
- `timestamp`: Precise timestamp for analytics

---

## Backend API Endpoints

### Session Management

**Get Active Sessions**
```
GET /api/users/sessions
Response:
{
  "sessions": [
    {
      "session_id": "uuid",
      "device_ip": "192.168.1.100",
      "device_type": "iPhone",
      "device_os": "iOS",
      "device_os_version": "17.2",
      "session_start": "2025-01-15T10:30:00Z",
      "last_activity": "2025-01-15T14:45:22Z",
      "is_active": true,
      "ip_rotation_detected": false
    }
  ]
}
```

**Revoke Session**
```
DELETE /api/users/sessions/{session_id}
```

**Get Session Details**
```
GET /api/users/sessions/{session_id}
Response includes:
- Device IP
- Device fingerprint
- IP rotation history
- Activity timeline
- Location history in this session
```

---

### Location Tracking

**Record Current Location**
```
POST /api/users/locations/track
Request:
{
  "latitude": 4.0511,
  "longitude": 9.7679,
  "accuracy_meters": 15,
  "activity_type": "traveling"
}

Response:
{
  "location_id": "uuid",
  "device_ip": "203.0.113.45",
  "recorded_at": "2025-01-15T14:45:22Z"
}
```

**Get Location History**
```
GET /api/users/locations?from=2025-01-01&to=2025-01-31
Response:
{
  "locations": [
    {
      "timestamp": "2025-01-15T14:45:22Z",
      "latitude": 4.0511,
      "longitude": 9.7679,
      "device_ip": "203.0.113.45",
      "route_id": "uuid",
      "accuracy_meters": 15
    }
  ]
}
```

---

## Frontend Implementation (React Native + Expo)

### Getting Device IP

```javascript
// In React Native app using native modules or Expo libraries
import * as Network from 'expo-network';
import { Platform } from 'react-native';

async function getDeviceIP() {
  try {
    const ipAddress = await Network.getIpAddressAsync();
    const ipv4Address = await Network.getNetworkStateAsync();
    
    return {
      ipv4: ipAddress,
      network: ipv4Address.details.ipv4?.address
    };
  } catch (error) {
    console.error('Error getting IP:', error);
    return null;
  }
}

// Get device info
import { getUniqueId, getModel, getSystemVersion } from 'react-native-device-info';

const deviceInfo = {
  fingerprint: getUniqueId(),
  model: getModel(),
  osVersion: getSystemVersion(),
  type: Platform.OS === 'ios' ? 'iPhone' : 'Android'
};
```

### Sending Device IP with Requests

```javascript
// In API client interceptor
import axios from 'axios';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${firebaseToken}`,
    'X-Device-IP': deviceIP,
    'X-Device-Fingerprint': deviceFingerprint
  }
});

// On every authenticated request
apiClient.interceptors.request.use(async (config) => {
  const currentIP = await getDeviceIP();
  config.headers['X-Device-IP'] = currentIP.ipv4;
  return config;
});
```

### Tracking Location Changes

```javascript
// In location tracking hook
import { useEffect } from 'react';
import * as Location from 'expo-location';

export function useLocationTracking() {
  useEffect(() => {
    const trackLocation = async () => {
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.LocationAccuracy.Balanced
      });
      
      const deviceIP = await getDeviceIP();
      
      // Send to backend
      await apiClient.post('/api/users/locations/track', {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        accuracy_meters: location.coords.accuracy,
        device_ip: deviceIP.ipv4,
        activity_type: 'traveling'
      });
    };

    const subscription = Location.watchPositionAsync(
      {
        accuracy: Location.LocationAccuracy.Balanced,
        timeInterval: 10000, // 10 seconds
        distanceInterval: 100 // 100 meters
      },
      trackLocation
    );

    return () => subscription.then(s => s.remove());
  }, []);
}
```

---

## Backend Implementation (FastAPI)

### Middleware for IP Extraction

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class DeviceIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get client IP (proxy-aware)
        client_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not client_ip:
            client_ip = request.client.host
        
        # Get device fingerprint
        device_fingerprint = request.headers.get('X-Device-Fingerprint')
        
        # Store in request state for use in endpoints
        request.state.device_ip = client_ip
        request.state.device_fingerprint = device_fingerprint
        
        response = await call_next(request)
        return response
```

### Session Management Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/users/sessions")

@router.get("/{user_id}")
async def get_user_sessions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active sessions for user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403)
    
    sessions = db.query(DeviceSession).filter(
        DeviceSession.user_id == user_id,
        DeviceSession.is_active == True
    ).all()
    
    return {
        "sessions": [
            {
                "session_id": str(s.id),
                "device_ip": s.device_ip,
                "device_type": s.device_type,
                "device_os": s.device_os,
                "session_start": s.session_start.isoformat(),
                "last_activity": s.last_activity.isoformat(),
                "is_active": s.is_active,
                "ip_rotation_detected": s.ip_rotation_detected
            }
            for s in sessions
        ]
    }

@router.delete("/{session_id}")
async def revoke_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke/end a specific device session"""
    session = db.query(DeviceSession).filter(
        DeviceSession.id == session_id,
        DeviceSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404)
    
    session.is_active = False
    session.session_end = datetime.utcnow()
    db.commit()
    
    return {"message": "Session revoked", "session_id": session_id}
```

### Location Tracking Endpoint

```python
from fastapi import Request

@router.post("/locations/track")
async def track_location(
    location_data: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = Depends()
):
    """Record user location with device IP"""
    
    device_ip = request.state.device_ip
    
    # Create location record
    location = UserLocation(
        user_id=current_user.id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        accuracy_meters=location_data.accuracy_meters,
        device_ip=device_ip,
        activity_type=location_data.activity_type,
        location=f"POINT({location_data.longitude} {location_data.latitude})",
        timestamp=datetime.utcnow()
    )
    
    db.add(location)
    
    # Update session last_activity
    session = db.query(DeviceSession).filter(
        DeviceSession.user_id == current_user.id,
        DeviceSession.device_ip == device_ip,
        DeviceSession.is_active == True
    ).first()
    
    if session:
        # Check for IP rotation
        if session.device_ip != device_ip:
            session.ip_rotation_detected = True
            session.ip_changes += 1
        
        session.last_activity = datetime.utcnow()
    
    db.commit()
    
    return {
        "location_id": str(location.id),
        "device_ip": device_ip,
        "recorded_at": datetime.utcnow().isoformat()
    }
```

---

## Security & Privacy Considerations

### IP Address Handling

**Storage:**
- Store device IPs in INET data type (PostgreSQL native)
- Encrypt sensitive device session data at rest
- Implement data retention policy (keep for 90 days only)

**Transmission:**
- Send IPs only over HTTPS/TLS
- Use X-Forwarded-For header from trusted proxies only
- Validate IP format before storing

### Privacy Compliance

**GDPR/Privacy Regulations:**
- Get explicit user consent for IP tracking
- Allow users to view all tracked locations
- Implement right to deletion (cascade delete)
- Provide data export functionality
- Anonymize IPs after 90 days (keep only anonymized hashes)

**User Controls:**
- Allow disabling location tracking
- Revoke sessions remotely
- Export location history
- Delete historical data

### Fraud Detection

**Anomalies to Monitor:**
```python
# IP rotation detection
if session.device_ip != new_ip:
    alert_user("New device login detected")

# Geographic impossibility
distance = calculate_distance(last_location, new_location)
time_elapsed = current_time - last_timestamp
required_speed = distance / time_elapsed

if required_speed > speed_of_light:  # Obviously impossible
    flag_for_review(user_id)

# Impossible IP-to-location jumps
ip_location = geoip_lookup(device_ip)
if distance(gps_location, ip_location) > 100km:
    require_additional_verification()
```

---

## Analytics & Reporting

### Available Metrics

**User Activity:**
- Active sessions per user
- Device diversity (iOS, Android, web)
- Session duration
- IP rotation frequency

**Location Analytics:**
- Routes most frequently traveled
- Peak travel times
- Geographic coverage
- Location accuracy distribution

**Security Metrics:**
- Failed authentication attempts per IP
- IP rotation incidents
- Suspicious geographic patterns
- Blocked sessions

### Example Queries

```sql
-- Most active devices by IP
SELECT device_ip, COUNT(*) as activity_count
FROM device_sessions
WHERE is_active = TRUE
GROUP BY device_ip
ORDER BY activity_count DESC
LIMIT 10;

-- User travel patterns
SELECT 
  u.phone_number,
  ul.activity_type,
  COUNT(*) as location_records,
  ST_AsText(ST_MakeEnvelope(
    MIN(ul.longitude), MIN(ul.latitude),
    MAX(ul.longitude), MAX(ul.latitude)
  )) as bbox
FROM users u
JOIN user_locations ul ON u.id = ul.user_id
WHERE ul.timestamp > NOW() - INTERVAL '30 days'
GROUP BY u.phone_number, ul.activity_type;

-- IP rotation events
SELECT 
  user_id,
  COUNT(*) as rotation_events,
  MAX(ip_changes) as max_ip_changes
FROM device_sessions
WHERE ip_rotation_detected = TRUE
GROUP BY user_id;
```

---

## Testing & Validation

### Unit Tests

```python
def test_device_ip_extraction():
    """Test IP extraction from headers"""
    request = create_test_request(
        headers={'X-Forwarded-For': '203.0.113.45'}
    )
    assert extract_device_ip(request) == '203.0.113.45'

def test_session_creation():
    """Test device session creation"""
    session = DeviceSession(
        user_id=user.id,
        device_ip='203.0.113.45',
        device_fingerprint='abc123'
    )
    assert session.is_active == True

def test_location_tracking():
    """Test location recording with IP"""
    location = track_location(
        user_id=user.id,
        latitude=4.0511,
        longitude=9.7679,
        device_ip='203.0.113.45'
    )
    assert location.device_ip == '203.0.113.45'
```

### Integration Tests

```python
def test_full_tracking_flow():
    """Test complete device tracking flow"""
    # 1. User logs in
    firebase_token = auth_user()
    
    # 2. Create session with device IP
    session = create_device_session(
        user_id=user.id,
        device_ip='203.0.113.45'
    )
    assert session.is_active
    
    # 3. Track location
    location = track_location(
        user_id=user.id,
        device_ip='203.0.113.45',
        latitude=4.0511,
        longitude=9.7679
    )
    
    # 4. Verify records
    assert location.device_ip == session.device_ip
    assert session.last_activity is not None
```

---

## Implementation Checklist

- [ ] Create `device_sessions` table with proper indices
- [ ] Create `user_locations` table with spatial type
- [ ] Implement DeviceIPMiddleware in FastAPI
- [ ] Add IP extraction to all authenticated endpoints
- [ ] Create session management endpoints (/api/users/sessions/*)
- [ ] Create location tracking endpoint (/api/users/locations/track)
- [ ] Implement IP rotation detection logic
- [ ] Add device fingerprinting in frontend
- [ ] Implement location tracking in React Native
- [ ] Add IP tracking headers to all API requests
- [ ] Create fraud detection alerts
- [ ] Implement data retention policy (90-day cleanup)
- [ ] Add GDPR compliance features (export, delete)
- [ ] Create admin dashboard for viewing sessions
- [ ] Write unit and integration tests
- [ ] Document privacy policy implications
- [ ] Test with real devices (iOS + Android)

---

## Deployment Considerations

1. **Database Migration:**
   - Run migrations to create new tables
   - Create indices for performance
   - Test with production-like data volume

2. **Feature Rollout:**
   - Start with read-only tracking (no blocking)
   - Monitor for IP-related issues
   - Enable fraud alerts gradually
   - Roll out to 100% of users

3. **Monitoring:**
   - Track IP extraction success rate
   - Monitor session creation rates
   - Alert on IP rotation anomalies
   - Dashboard for device activity

4. **Privacy Communication:**
   - Update privacy policy
   - Notify users of IP tracking
   - Add in-app consent flow
   - Document data retention

---

## Future Enhancements

1. **Machine Learning:**
   - Anomaly detection for suspicious IPs
   - Predictive fraud scoring
   - Unusual pattern recognition

2. **Advanced Analytics:**
   - Route heatmaps
   - Traffic pattern prediction
   - User segmentation by location

3. **Enhanced Security:**
   - Step-up authentication on IP change
   - Biometric verification for new devices
   - Risk scoring for sessions

4. **Privacy Enhancements:**
   - IP anonymization options
   - Location privacy zones
   - Selective tracking per route

---

**Status:** ✅ Implementation Ready  
**Dependencies:** PostgreSQL 12+, PostGIS 2.5+  
**Compatibility:** FastAPI 0.95+, React Native 0.73+

This device IP tracking implementation provides a robust foundation for session management, location analytics, and fraud detection while maintaining user privacy and security.
