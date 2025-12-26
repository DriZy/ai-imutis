# Security Implementation Guide

**Project:** AI-IMUTIS  
**Version:** 1.0  
**Last Updated:** December 26, 2025  
**Classification:** Critical Security Documentation

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Backend API Security](#backend-api-security)
3. [Mobile Application Security](#mobile-application-security)
4. [Server & Infrastructure Security](#server--infrastructure-security)
5. [Database Security](#database-security)
6. [Network Security](#network-security)
7. [Monitoring & Incident Response](#monitoring--incident-response)
8. [Compliance & Privacy](#compliance--privacy)

---

## Security Overview

### Security Principles

- **Defense in Depth:** Multiple layers of security controls
- **Least Privilege:** Minimal permissions for all components
- **Zero Trust:** Verify everything, trust nothing
- **Fail Secure:** Default to denial when errors occur
- **Security by Design:** Built-in from the start, not bolted on

### Threat Model

**Primary Threats:**
- Unauthorized access to user data
- API abuse and DoS attacks
- SQL injection and code injection
- Man-in-the-middle attacks
- Session hijacking
- Data breaches
- Account takeover
- Malicious file uploads

---

## Backend API Security

### 1. Rate Limiting

#### Implementation with Redis

```python
from fastapi import FastAPI, Request, HTTPException
from redis import Redis
from datetime import datetime, timedelta
import hashlib

app = FastAPI()
redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

class RateLimiter:
    """Advanced rate limiter with multiple strategies."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int,
        endpoint: str = "general"
    ) -> bool:
        """
        Check if request is within rate limits.
        
        Args:
            identifier: User ID, IP address, or session ID
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            endpoint: Endpoint identifier for granular limits
        
        Returns:
            True if within limits, raises HTTPException otherwise
        """
        key = f"rate_limit:{endpoint}:{identifier}"
        current_time = datetime.utcnow().timestamp()
        
        # Remove old entries outside the window
        self.redis.zremrangebyscore(
            key,
            0,
            current_time - window_seconds
        )
        
        # Count requests in current window
        request_count = self.redis.zcard(key)
        
        if request_count >= max_requests:
            retry_after = self.redis.zrange(key, 0, 0, withscores=True)
            if retry_after:
                oldest_request_time = retry_after[0][1]
                retry_seconds = int(window_seconds - (current_time - oldest_request_time))
                
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {retry_seconds} seconds.",
                    headers={"Retry-After": str(retry_seconds)}
                )
        
        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window_seconds)
        
        return True

# Rate limit tiers
RATE_LIMITS = {
    "anonymous": {"requests": 10, "window": 60},      # 10 req/min
    "authenticated": {"requests": 100, "window": 60}, # 100 req/min
    "premium": {"requests": 500, "window": 60},       # 500 req/min
    "ai_endpoints": {"requests": 20, "window": 60},   # 20 req/min for AI
    "booking": {"requests": 5, "window": 60},         # 5 bookings/min
}

rate_limiter = RateLimiter(redis_client)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting based on user tier and endpoint."""
    
    # Get identifier (user ID or IP)
    user = getattr(request.state, "user", None)
    identifier = user.get("uid") if user else request.client.host
    
    # Determine tier
    if not user:
        tier = "anonymous"
    elif user.get("role") == "premium":
        tier = "premium"
    else:
        tier = "authenticated"
    
    # Special limits for specific endpoints
    path = request.url.path
    if "/ai/" in path:
        limit_config = RATE_LIMITS["ai_endpoints"]
        endpoint = "ai_endpoints"
    elif "/book" in path:
        limit_config = RATE_LIMITS["booking"]
        endpoint = "booking"
    else:
        limit_config = RATE_LIMITS[tier]
        endpoint = tier
    
    try:
        await rate_limiter.check_rate_limit(
            identifier=identifier,
            max_requests=limit_config["requests"],
            window_seconds=limit_config["window"],
            endpoint=endpoint
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers=e.headers
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(limit_config["requests"])
    response.headers["X-RateLimit-Window"] = str(limit_config["window"])
    
    return response
```

### 2. Request Throttling & DDoS Protection

```python
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class AdaptiveThrottler:
    """Adaptive throttling based on system load and attack detection."""
    
    def __init__(self):
        self.request_patterns = defaultdict(list)
        self.blocked_ips = {}
        self.suspicious_patterns = set()
    
    async def detect_attack_pattern(self, ip: str, endpoint: str) -> bool:
        """Detect potential DDoS or brute force attacks."""
        
        current_time = datetime.utcnow()
        pattern_key = f"{ip}:{endpoint}"
        
        # Track request pattern
        self.request_patterns[pattern_key].append(current_time)
        
        # Clean old entries (last 5 minutes)
        self.request_patterns[pattern_key] = [
            t for t in self.request_patterns[pattern_key]
            if t > current_time - timedelta(minutes=5)
        ]
        
        requests = self.request_patterns[pattern_key]
        
        # Attack indicators
        if len(requests) > 100:  # More than 100 requests in 5 minutes
            return True
        
        # Check for rapid-fire requests (>10 req/second)
        recent_requests = [
            t for t in requests
            if t > current_time - timedelta(seconds=1)
        ]
        if len(recent_requests) > 10:
            return True
        
        return False
    
    async def block_ip(self, ip: str, duration_minutes: int = 60):
        """Temporarily block an IP address."""
        self.blocked_ips[ip] = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        # Log to security system
        logger.warning(f"IP {ip} blocked for {duration_minutes} minutes due to suspicious activity")
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked."""
        if ip in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False

throttler = AdaptiveThrottler()

@app.middleware("http")
async def ddos_protection_middleware(request: Request, call_next):
    """DDoS protection middleware."""
    
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    
    # Check if IP is blocked
    if throttler.is_blocked(client_ip):
        return JSONResponse(
            status_code=403,
            content={"detail": "Access temporarily blocked due to suspicious activity"}
        )
    
    # Detect attack patterns
    if await throttler.detect_attack_pattern(client_ip, request.url.path):
        await throttler.block_ip(client_ip, duration_minutes=60)
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Access temporarily blocked."}
        )
    
    response = await call_next(request)
    return response
```

### 3. Input Validation & Sanitization

```python
from pydantic import BaseModel, validator, Field
from typing import Optional
import re
import html
import bleach

class SecurityValidator:
    """Comprehensive input validation and sanitization."""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove potentially dangerous HTML/JavaScript."""
        allowed_tags = ['p', 'br', 'strong', 'em', 'u']
        return bleach.clean(text, tags=allowed_tags, strip=True)
    
    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Prevent SQL injection in text fields."""
        dangerous_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|\#|\/\*|\*\/)",
            r"('|\"|\;|\||&)",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Input contains potentially dangerous SQL patterns")
        
        return text
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        """Prevent directory traversal attacks."""
        dangerous_patterns = [
            r"\.\.",
            r"\/\.\.",
            r"\.\.",
            r"~",
            r"\$",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, path):
                raise ValueError("Path contains dangerous patterns")
        
        return path
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return email.lower()
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate phone number (E.164 format)."""
        phone_pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(phone_pattern, phone):
            raise ValueError("Phone must be in E.164 format (+237...)")
        return phone

# Example usage in Pydantic models
class SecureUserInput(BaseModel):
    """Secure user input model with validation."""
    
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    
    @validator("name")
    def validate_name(cls, v):
        # Remove HTML tags
        v = SecurityValidator.sanitize_html(v)
        # Check for SQL injection
        v = SecurityValidator.sanitize_sql(v)
        return v.strip()
    
    @validator("email")
    def validate_email(cls, v):
        return SecurityValidator.validate_email(v)
    
    @validator("phone")
    def validate_phone(cls, v):
        if v:
            return SecurityValidator.validate_phone(v)
        return v
    
    @validator("bio")
    def validate_bio(cls, v):
        if v:
            v = SecurityValidator.sanitize_html(v)
            v = SecurityValidator.sanitize_sql(v)
        return v
```

### 4. SQL Injection Protection

```python
from sqlalchemy import text
from sqlalchemy.orm import Session

class SecureDatabase:
    """Database operations with SQL injection protection."""
    
    @staticmethod
    async def safe_query(db: Session, query: str, params: dict):
        """
        Execute parameterized query to prevent SQL injection.
        NEVER use string concatenation for SQL queries.
        """
        # BAD (vulnerable to SQL injection):
        # query = f"SELECT * FROM users WHERE email = '{email}'"
        
        # GOOD (parameterized query):
        result = db.execute(text(query), params)
        return result.fetchall()
    
    @staticmethod
    async def get_user_by_email(db: Session, email: str):
        """Safe user lookup with parameterized query."""
        query = text("SELECT * FROM users WHERE email = :email")
        result = db.execute(query, {"email": email})
        return result.fetchone()
    
    @staticmethod
    async def search_trips(
        db: Session,
        origin: str,
        destination: str,
        date: str
    ):
        """Safe trip search with multiple parameters."""
        query = text("""
            SELECT * FROM trips 
            WHERE origin = :origin 
            AND destination = :destination 
            AND departure_date >= :date
            ORDER BY departure_date
        """)
        
        params = {
            "origin": origin,
            "destination": destination,
            "date": date
        }
        
        result = db.execute(query, params)
        return result.fetchall()

# Using ORM (preferred - automatic SQL injection protection)
from sqlalchemy.orm import Session
from models import User, Trip

async def get_user_secure(db: Session, user_id: str):
    """ORM automatically prevents SQL injection."""
    return db.query(User).filter(User.id == user_id).first()

async def search_trips_secure(db: Session, origin: str, destination: str):
    """ORM with filters - safe by default."""
    return db.query(Trip).filter(
        Trip.origin == origin,
        Trip.destination == destination
    ).all()
```

### 5. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# Strict CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-imutis.com",
        "https://app.ai-imutis.com",
        "https://admin.ai-imutis.com",
        # Add specific mobile app origins
        "capacitor://localhost",  # Capacitor apps
        "ionic://localhost",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Device-Fingerprint",
        "X-Device-IP",
        "X-App-Version",
    ],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

### 6. Authentication Security

```python
from firebase_admin import auth, credentials
import firebase_admin
from functools import wraps
from typing import Optional

# Initialize Firebase Admin
cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred)

class FirebaseAuthSecurity:
    """Enhanced Firebase authentication with security features."""
    
    @staticmethod
    async def verify_token(token: str) -> dict:
        """Verify Firebase ID token with additional checks."""
        try:
            # Verify token
            decoded_token = auth.verify_id_token(token, check_revoked=True)
            
            # Additional security checks
            current_time = datetime.utcnow().timestamp()
            
            # Check token age (reject if older than 1 hour)
            auth_time = decoded_token.get("auth_time", 0)
            if current_time - auth_time > 3600:
                raise HTTPException(
                    status_code=401,
                    detail="Token expired. Please re-authenticate."
                )
            
            # Check if email is verified for critical operations
            if not decoded_token.get("email_verified", False):
                logger.warning(f"Unverified email access attempt: {decoded_token.get('email')}")
            
            return decoded_token
            
        except auth.RevokedIdTokenError:
            raise HTTPException(status_code=401, detail="Token has been revoked")
        except auth.ExpiredIdTokenError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except auth.InvalidIdTokenError:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    @staticmethod
    async def check_permissions(user: dict, required_role: str) -> bool:
        """Check if user has required role."""
        user_role = user.get("role", "user")
        
        role_hierarchy = {
            "user": 0,
            "driver": 1,
            "admin": 2,
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return True

# Dependency for protected endpoints
async def verify_firebase_token(
    authorization: str = Header(None)
) -> dict:
    """Verify Firebase token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    return await FirebaseAuthSecurity.verify_token(token)

# Role-based access control decorator
def require_role(required_role: str):
    """Decorator for role-based access control."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict = None, **kwargs):
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            await FirebaseAuthSecurity.check_permissions(user, required_role)
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

# Usage example
@router.post("/admin/users")
@require_role("admin")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(verify_firebase_token)
):
    """Admin-only endpoint."""
    pass
```

### 7. Session Security

```python
from datetime import datetime, timedelta
import secrets

class SessionManager:
    """Secure session management with device tracking."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def create_session(
        self,
        user_id: str,
        device_ip: str,
        device_fingerprint: str
    ) -> str:
        """Create secure session with device binding."""
        
        # Generate cryptographically secure session ID
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "device_ip": device_ip,
            "device_fingerprint": device_fingerprint,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "login_attempts": 0,
        }
        
        # Store session with 30-day expiry
        self.redis.setex(
            f"session:{session_id}",
            timedelta(days=30),
            json.dumps(session_data)
        )
        
        return session_id
    
    async def validate_session(
        self,
        session_id: str,
        current_ip: str,
        current_fingerprint: str
    ) -> bool:
        """Validate session with IP rotation detection."""
        
        session_key = f"session:{session_id}"
        session_data = self.redis.get(session_key)
        
        if not session_data:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        session = json.loads(session_data)
        
        # Check IP rotation
        if session["device_ip"] != current_ip:
            logger.warning(
                f"IP rotation detected for user {session['user_id']}: "
                f"{session['device_ip']} -> {current_ip}"
            )
            
            # Require re-authentication
            raise HTTPException(
                status_code=401,
                detail="Session validation failed. Please re-authenticate."
            )
        
        # Check device fingerprint
        if session["device_fingerprint"] != current_fingerprint:
            logger.warning(
                f"Device fingerprint mismatch for user {session['user_id']}"
            )
            raise HTTPException(
                status_code=401,
                detail="Device validation failed"
            )
        
        # Update last activity
        session["last_activity"] = datetime.utcnow().isoformat()
        self.redis.setex(
            session_key,
            timedelta(days=30),
            json.dumps(session)
        )
        
        return True
    
    async def revoke_session(self, session_id: str):
        """Revoke session (logout)."""
        self.redis.delete(f"session:{session_id}")
```

---

## Mobile Application Security

### 1. Secure Storage

```typescript
// services/storage/secureStorage.ts
import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';

class SecureStorageService {
  /**
   * Store sensitive data encrypted in secure storage.
   */
  async setSecureItem(key: string, value: string): Promise<void> {
    try {
      // Encrypt before storing (additional layer)
      const encrypted = await this.encrypt(value);
      await SecureStore.setItemAsync(key, encrypted);
    } catch (error) {
      console.error('Error storing secure item:', error);
      throw new Error('Failed to store secure data');
    }
  }

  async getSecureItem(key: string): Promise<string | null> {
    try {
      const encrypted = await SecureStore.getItemAsync(key);
      if (!encrypted) return null;
      
      return await this.decrypt(encrypted);
    } catch (error) {
      console.error('Error retrieving secure item:', error);
      return null;
    }
  }

  async deleteSecureItem(key: string): Promise<void> {
    await SecureStore.deleteItemAsync(key);
  }

  private async encrypt(data: string): Promise<string> {
    // Use expo-crypto for encryption
    const digest = await Crypto.digestStringAsync(
      Crypto.CryptoDigestAlgorithm.SHA256,
      data
    );
    return digest;
  }

  private async decrypt(encrypted: string): Promise<string> {
    // Decryption logic
    return encrypted;
  }
}

export const secureStorage = new SecureStorageService();

// Usage: Store Firebase token securely
await secureStorage.setSecureItem('firebase_token', token);
```

### 2. Network Security (Certificate Pinning)

```typescript
// services/api/certificatePinning.ts
import axios from 'axios';
import * as FileSystem from 'expo-file-system';

const EXPECTED_CERTIFICATE_HASH = 'sha256/AAAAAAAAAA...'; // Your cert hash

class SecureAPIClient {
  private client;

  constructor() {
    this.client = axios.create({
      baseURL: 'https://api.ai-imutis.com',
      timeout: 15000,
      // Certificate pinning configuration
      httpsAgent: {
        rejectUnauthorized: true, // Reject self-signed certs
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for security headers
    this.client.interceptors.request.use(async (config) => {
      // Add security headers
      config.headers['X-App-Version'] = process.env.APP_VERSION;
      config.headers['X-Request-ID'] = this.generateRequestId();
      
      // Validate SSL certificate
      await this.validateCertificate(config.url);
      
      return config;
    });

    // Response interceptor for attack detection
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Detect potential MITM attacks
        if (error.code === 'CERT_HAS_EXPIRED') {
          console.error('SECURITY ALERT: SSL certificate expired');
          throw new Error('Security validation failed');
        }
        
        if (error.code === 'SELF_SIGNED_CERT_IN_CHAIN') {
          console.error('SECURITY ALERT: Self-signed certificate detected');
          throw new Error('Security validation failed');
        }
        
        throw error;
      }
    );
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  private async validateCertificate(url: string): Promise<void> {
    // Certificate pinning validation
    // In production, verify SSL certificate fingerprint
    return;
  }
}

export const secureAPI = new SecureAPIClient();
```

### 3. Input Validation (Mobile Side)

```typescript
// utils/inputValidator.ts
class MobileInputValidator {
  /**
   * Validate and sanitize user input before sending to API.
   */
  
  static sanitizeString(input: string): string {
    // Remove potentially dangerous characters
    return input
      .replace(/<[^>]*>/g, '') // Remove HTML tags
      .replace(/[<>\"']/g, '') // Remove dangerous chars
      .trim();
  }

  static validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  static validatePhone(phone: string): boolean {
    const phoneRegex = /^\+[1-9]\d{1,14}$/;
    return phoneRegex.test(phone);
  }

  static sanitizeSearchQuery(query: string): string {
    // Prevent SQL injection in search queries
    const sanitized = query
      .replace(/['";]/g, '') // Remove SQL special chars
      .replace(/--/g, '')    // Remove SQL comments
      .replace(/\/\*/g, '')  // Remove block comments
      .trim();
    
    return sanitized.substring(0, 100); // Limit length
  }

  static validateBookingData(data: any): boolean {
    // Validate booking data structure
    const required = ['tripId', 'passengers', 'paymentMethod'];
    
    for (const field of required) {
      if (!data[field]) {
        throw new Error(`Missing required field: ${field}`);
      }
    }
    
    // Validate passengers (1-20)
    if (data.passengers < 1 || data.passengers > 20) {
      throw new Error('Invalid passenger count');
    }
    
    return true;
  }
}

export default MobileInputValidator;
```

### 4. Jailbreak/Root Detection

```typescript
// security/deviceSecurity.ts
import * as Device from 'expo-device';
import { Platform } from 'react-native';

class DeviceSecurityChecker {
  async checkDeviceSecurity(): Promise<{
    isSecure: boolean;
    warnings: string[];
  }> {
    const warnings: string[] = [];

    // Check if device is rooted/jailbroken
    if (await this.isRooted()) {
      warnings.push('Device appears to be rooted/jailbroken');
    }

    // Check if running in emulator
    if (await Device.isDevice === false) {
      warnings.push('Running on emulator');
    }

    // Check if debugging is enabled
    if (__DEV__) {
      warnings.push('Development mode enabled');
    }

    return {
      isSecure: warnings.length === 0,
      warnings,
    };
  }

  private async isRooted(): Promise<boolean> {
    if (Platform.OS === 'android') {
      // Check for common root indicators on Android
      const rootPaths = [
        '/system/app/Superuser.apk',
        '/sbin/su',
        '/system/bin/su',
        '/system/xbin/su',
      ];
      
      // In production, use native module to check these paths
      return false; // Placeholder
    }
    
    if (Platform.OS === 'ios') {
      // Check for jailbreak indicators on iOS
      const jailbreakPaths = [
        '/Applications/Cydia.app',
        '/Library/MobileSubstrate/MobileSubstrate.dylib',
        '/bin/bash',
        '/usr/sbin/sshd',
      ];
      
      // In production, use native module to check these paths
      return false; // Placeholder
    }
    
    return false;
  }

  async enforceSecurityPolicy(): Promise<void> {
    const securityCheck = await this.checkDeviceSecurity();
    
    if (!securityCheck.isSecure) {
      console.warn('Security warnings:', securityCheck.warnings);
      
      // In production environment, restrict access
      if (process.env.NODE_ENV === 'production') {
        throw new Error(
          'Application cannot run on this device due to security concerns'
        );
      }
    }
  }
}

export const deviceSecurity = new DeviceSecurityChecker();
```

### 5. Biometric Authentication

```typescript
// services/auth/biometricAuth.ts
import * as LocalAuthentication from 'expo-local-authentication';

class BiometricAuthService {
  async isBiometricSupported(): Promise<boolean> {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    const isEnrolled = await LocalAuthentication.isEnrolledAsync();
    return hasHardware && isEnrolled;
  }

  async authenticate(reason: string = 'Verify your identity'): Promise<boolean> {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: reason,
        cancelLabel: 'Cancel',
        disableDeviceFallback: false,
        requireConfirmation: true,
      });

      return result.success;
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return false;
    }
  }

  async enableBiometricLogin(userId: string): Promise<void> {
    const isSupported = await this.isBiometricSupported();
    
    if (!isSupported) {
      throw new Error('Biometric authentication not available');
    }

    // Store flag in secure storage
    await secureStorage.setSecureItem(
      `biometric_enabled_${userId}`,
      'true'
    );
  }
}

export const biometricAuth = new BiometricAuthService();
```

---

## Server & Infrastructure Security

### 1. Firewall Configuration (UFW)

```bash
#!/bin/bash
# Firewall setup script for Ubuntu server

# Enable UFW
sudo ufw --force enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (change port from default 22)
sudo ufw allow 2222/tcp comment 'SSH on custom port'

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Allow PostgreSQL only from application server
sudo ufw allow from 10.0.1.0/24 to any port 5432 comment 'PostgreSQL'

# Allow Redis only from application server
sudo ufw allow from 10.0.1.0/24 to any port 6379 comment 'Redis'

# Rate limiting for SSH
sudo ufw limit 2222/tcp comment 'SSH rate limiting'

# Enable logging
sudo ufw logging on

# Reload firewall
sudo ufw reload

# Show status
sudo ufw status verbose
```

### 2. Nginx Security Configuration

```nginx
# /etc/nginx/nginx.conf
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off; # Hide Nginx version

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate Limiting Zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # Request Size Limits
    client_body_buffer_size 10K;
    client_header_buffer_size 1k;
    client_max_body_size 8m;
    large_client_header_buffers 2 1k;

    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log warn;

    # Include server blocks
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

### 3. API Server Configuration

```nginx
# /etc/nginx/sites-available/api.ai-imutis.com
server {
    listen 80;
    server_name api.ai-imutis.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.ai-imutis.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/api.ai-imutis.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.ai-imutis.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API Rate Limiting
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;

        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Authentication endpoints with stricter limits
    location /api/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;

        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Block common attack patterns
    location ~* (\.(git|svn|htaccess|htpasswd)|composer\.json|package\.json|\.env) {
        deny all;
        return 404;
    }

    # Logging
    access_log /var/log/nginx/api-access.log;
    error_log /var/log/nginx/api-error.log;
}
```

### 4. Fail2Ban Configuration

```ini
# /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = security@ai-imutis.com
sender = fail2ban@ai-imutis.com
action = %(action_mwl)s

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 5

[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 60
bantime = 3600

[api-auth]
enabled = true
port = http,https
filter = api-auth
logpath = /var/log/nginx/api-error.log
maxretry = 5
bantime = 7200
```

### 5. DDoS Protection with ModSecurity

```bash
# Install ModSecurity
sudo apt-get install libapache2-mod-security2

# Enable OWASP Core Rule Set
cd /etc/modsecurity/
sudo git clone https://github.com/coreruleset/coreruleset.git
cd coreruleset
sudo mv crs-setup.conf.example crs-setup.conf

# Configure ModSecurity
sudo nano /etc/modsecurity/modsecurity.conf

# Key settings:
SecRuleEngine On
SecRequestBodyAccess On
SecRequestBodyLimit 13107200
SecRequestBodyNoFilesLimit 131072
SecResponseBodyAccess On
SecResponseBodyMimeType text/plain text/html text/xml
SecResponseBodyLimit 524288
SecAuditEngine RelevantOnly
SecAuditLogRelevantStatus "^(?:5|4(?!04))"
```

---

## Database Security

### 1. PostgreSQL Security Configuration

```sql
-- Create read-only user for application
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'strong_password_here';
GRANT CONNECT ON DATABASE ai_imutis TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

-- Create read-write user for application
CREATE ROLE app_readwrite WITH LOGIN PASSWORD 'strong_password_here';
GRANT CONNECT ON DATABASE ai_imutis TO app_readwrite;
GRANT USAGE ON SCHEMA public TO app_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;

-- Revoke public schema permissions
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Enable row-level security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_sessions ENABLE ROW LEVEL SECURITY;

-- Row-level security policy (users can only see their own data)
CREATE POLICY user_isolation_policy ON users
    FOR ALL
    TO app_readwrite
    USING (id = current_setting('app.current_user_id')::UUID);

CREATE POLICY booking_isolation_policy ON bookings
    FOR ALL
    TO app_readwrite
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- Audit logging
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    user_id UUID,
    old_data JSONB,
    new_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address INET
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, user_id, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.user_id, row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, user_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.user_id, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, user_id, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, OLD.user_id, row_to_json(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply audit trigger to sensitive tables
CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER bookings_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON bookings
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

### 2. Database Connection Security

```python
# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import ssl

class SecureDatabaseConnection:
    """Secure database connection configuration."""
    
    @staticmethod
    def get_engine():
        # SSL/TLS connection
        ssl_args = {
            'sslmode': 'require',
            'sslrootcert': '/path/to/ca-certificate.crt',
            'sslcert': '/path/to/client-certificate.crt',
            'sslkey': '/path/to/client-key.key',
        }
        
        connection_string = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        
        engine = create_engine(
            connection_string,
            connect_args=ssl_args,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False,          # Disable SQL query logging in production
        )
        
        return engine
```

---

## Network Security

### 1. VPC & Network Segmentation

```bash
# AWS VPC configuration example
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ai-imutis-vpc}]'

# Create subnets
# Public subnet for load balancers
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# Private subnet for application servers
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1a

# Private subnet for database
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.3.0/24 --availability-zone us-east-1a

# Security groups
# Application server security group
aws ec2 create-security-group --group-name app-servers --description "Application servers" --vpc-id vpc-xxxxx

# Allow HTTPS from load balancer only
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 8000 --source-group sg-lb-xxxxx

# Database security group
aws ec2 create-security-group --group-name database --description "PostgreSQL database" --vpc-id vpc-xxxxx

# Allow PostgreSQL from app servers only
aws ec2 authorize-security-group-ingress --group-id sg-db-xxxxx --protocol tcp --port 5432 --source-group sg-app-xxxxx
```

### 2. WAF Rules

```python
# AWS WAF rules configuration
waf_rules = {
    "rate_limiting": {
        "name": "RateLimitRule",
        "priority": 1,
        "action": "BLOCK",
        "rule": {
            "RateBasedStatement": {
                "Limit": 2000,
                "AggregateKeyType": "IP"
            }
        }
    },
    "geo_blocking": {
        "name": "GeoBlockRule",
        "priority": 2,
        "action": "BLOCK",
        "rule": {
            "GeoMatchStatement": {
                "CountryCodes": ["CN", "RU", "KP"]  # Block specific countries
            }
        }
    },
    "sql_injection": {
        "name": "SQLInjectionRule",
        "priority": 3,
        "action": "BLOCK",
        "rule": {
            "ManagedRuleGroupStatement": {
                "VendorName": "AWS",
                "Name": "AWSManagedRulesSQLiRuleSet"
            }
        }
    },
    "xss_protection": {
        "name": "XSSProtectionRule",
        "priority": 4,
        "action": "BLOCK",
        "rule": {
            "ManagedRuleGroupStatement": {
                "VendorName": "AWS",
                "Name": "AWSManagedRulesKnownBadInputsRuleSet"
            }
        }
    }
}
```

---

## Monitoring & Incident Response

### 1. Security Monitoring

```python
# monitoring/security_monitor.py
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class SecurityMonitor:
    """Real-time security monitoring and alerting."""
    
    def __init__(self):
        self.alert_thresholds = {
            "failed_auth_attempts": 10,
            "rate_limit_violations": 50,
            "sql_injection_attempts": 1,
            "xss_attempts": 1,
            "suspicious_ips": []
        }
    
    async def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict,
        ip_address: str
    ):
        """Log security events for analysis."""
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,  # low, medium, high, critical
            "details": details,
            "ip_address": ip_address,
        }
        
        logger.warning(f"SECURITY EVENT: {event}")
        
        # Send to SIEM system
        await self.send_to_siem(event)
        
        # Check if immediate action needed
        if severity in ["high", "critical"]:
            await self.trigger_alert(event)
    
    async def send_to_siem(self, event: Dict):
        """Send event to Security Information and Event Management system."""
        # Integration with Splunk, ELK, or other SIEM
        pass
    
    async def trigger_alert(self, event: Dict):
        """Trigger security alert to operations team."""
        # Send email, Slack, PagerDuty notification
        pass

security_monitor = SecurityMonitor()

# Usage in middleware
@app.middleware("http")
async def security_monitoring_middleware(request: Request, call_next):
    """Monitor and log security events."""
    
    start_time = datetime.utcnow()
    
    try:
        response = await call_next(request)
        
        # Log suspicious patterns
        if response.status_code == 429:  # Rate limited
            await security_monitor.log_security_event(
                event_type="rate_limit_violation",
                severity="medium",
                details={"endpoint": request.url.path},
                ip_address=request.client.host
            )
        
        return response
        
    except Exception as e:
        # Log security exceptions
        await security_monitor.log_security_event(
            event_type="exception",
            severity="high",
            details={"error": str(e), "endpoint": request.url.path},
            ip_address=request.client.host
        )
        raise
```

### 2. Incident Response Checklist

```markdown
# Security Incident Response Plan

## Phase 1: Detection & Analysis (0-15 minutes)
- [ ] Confirm security incident
- [ ] Categorize severity (P1: Critical, P2: High, P3: Medium, P4: Low)
- [ ] Document initial findings
- [ ] Notify security team
- [ ] Start incident log

## Phase 2: Containment (15-60 minutes)
- [ ] Isolate affected systems
- [ ] Block malicious IPs
- [ ] Revoke compromised credentials
- [ ] Enable additional logging
- [ ] Preserve evidence

## Phase 3: Eradication (1-24 hours)
- [ ] Remove malware/backdoors
- [ ] Patch vulnerabilities
- [ ] Reset all affected credentials
- [ ] Update firewall rules
- [ ] Deploy security fixes

## Phase 4: Recovery (24-72 hours)
- [ ] Restore services from clean backups
- [ ] Monitor for reinfection
- [ ] Verify system integrity
- [ ] Test all security controls
- [ ] Document lessons learned

## Phase 5: Post-Incident (1-2 weeks)
- [ ] Complete incident report
- [ ] Update security policies
- [ ] Conduct team debrief
- [ ] Implement preventive measures
- [ ] Notify affected users (if required by law)
```

---

## Compliance & Privacy

### 1. GDPR Compliance

```python
# compliance/gdpr.py
from datetime import datetime, timedelta
from typing import Dict

class GDPRCompliance:
    """GDPR compliance utilities."""
    
    @staticmethod
    async def anonymize_user_data(user_id: str):
        """Anonymize user data per GDPR right to be forgotten."""
        
        # Anonymize personal information
        await db.execute("""
            UPDATE users 
            SET 
                email = 'deleted-' || id || '@anonymized.local',
                phone_number = NULL,
                display_name = 'Deleted User',
                profile_photo = NULL,
                date_of_birth = NULL,
                address = NULL
            WHERE id = :user_id
        """, {"user_id": user_id})
        
        # Anonymize IP addresses (keep for 90 days per policy)
        await db.execute("""
            UPDATE device_sessions 
            SET device_ip = '0.0.0.0'
            WHERE user_id = :user_id 
            AND created_at < NOW() - INTERVAL '90 days'
        """, {"user_id": user_id})
        
        logger.info(f"User {user_id} data anonymized per GDPR")
    
    @staticmethod
    async def export_user_data(user_id: str) -> Dict:
        """Export all user data per GDPR right to data portability."""
        
        user_data = {
            "personal_info": await db.query(User).filter(User.id == user_id).first(),
            "bookings": await db.query(Booking).filter(Booking.user_id == user_id).all(),
            "device_sessions": await db.query(DeviceSession).filter(DeviceSession.user_id == user_id).all(),
            "locations": await db.query(UserLocation).filter(UserLocation.user_id == user_id).all(),
            "preferences": await db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first(),
            "export_date": datetime.utcnow().isoformat()
        }
        
        return user_data
    
    @staticmethod
    async def schedule_data_retention_cleanup():
        """Automatically delete old data per retention policy."""
        
        # Delete device sessions older than 30 days
        await db.execute("""
            DELETE FROM device_sessions 
            WHERE last_activity < NOW() - INTERVAL '30 days'
        """)
        
        # Anonymize IP addresses older than 90 days
        await db.execute("""
            UPDATE user_locations 
            SET device_ip = '0.0.0.0'
            WHERE timestamp < NOW() - INTERVAL '90 days'
        """)
        
        logger.info("Data retention cleanup completed")
```

### 2. PCI-DSS Compliance (Payment Security)

```python
# compliance/pci_dss.py
class PCIDSSCompliance:
    """PCI-DSS compliance for payment handling."""
    
    @staticmethod
    def mask_card_number(card_number: str) -> str:
        """Mask credit card number, show only last 4 digits."""
        if len(card_number) < 4:
            return "****"
        return "****" + card_number[-4:]
    
    @staticmethod
    def validate_cvv(cvv: str) -> bool:
        """Validate CVV format (never store CVV)."""
        return len(cvv) in [3, 4] and cvv.isdigit()
    
    @staticmethod
    async def tokenize_payment_method(card_details: Dict) -> str:
        """
        Tokenize payment method (use payment gateway's tokenization).
        Never store full card details in database.
        """
        # Use Stripe, PayPal, or local payment gateway tokenization
        token = await payment_gateway.create_token(card_details)
        return token
    
    @staticmethod
    async def log_payment_transaction(transaction_data: Dict):
        """Log payment transactions for audit (PCI-DSS requirement)."""
        
        # Remove sensitive data before logging
        safe_data = {
            "transaction_id": transaction_data["transaction_id"],
            "amount": transaction_data["amount"],
            "currency": transaction_data["currency"],
            "status": transaction_data["status"],
            "timestamp": datetime.utcnow().isoformat(),
            # Never log: full card number, CVV, PIN
        }
        
        await db.execute("""
            INSERT INTO payment_audit_log (data, timestamp)
            VALUES (:data, NOW())
        """, {"data": json.dumps(safe_data)})
```

---

## Security Checklist

### Pre-Deployment Security Audit

- [ ] **Authentication & Authorization**
  - [ ] Firebase token verification implemented
  - [ ] Role-based access control (RBAC) configured
  - [ ] Session management with device tracking
  - [ ] Biometric authentication for mobile (optional)

- [ ] **Input Validation**
  - [ ] All user inputs validated and sanitized
  - [ ] SQL injection protection (parameterized queries)
  - [ ] XSS protection (HTML sanitization)
  - [ ] File upload validation
  - [ ] Path traversal protection

- [ ] **Rate Limiting & DDoS**
  - [ ] Rate limiting per endpoint implemented
  - [ ] IP-based throttling configured
  - [ ] WAF rules enabled
  - [ ] CloudFlare/CDN DDoS protection active

- [ ] **Network Security**
  - [ ] HTTPS/TLS enforced (A+ rating)
  - [ ] Certificate pinning in mobile app
  - [ ] CORS properly configured
  - [ ] Security headers configured
  - [ ] Firewall rules implemented

- [ ] **Database Security**
  - [ ] Row-level security enabled
  - [ ] Principle of least privilege
  - [ ] Audit logging enabled
  - [ ] Encrypted at rest
  - [ ] SSL/TLS connections

- [ ] **Mobile Security**
  - [ ] Secure storage for tokens
  - [ ] Certificate validation
  - [ ] Jailbreak/root detection
  - [ ] Code obfuscation
  - [ ] No sensitive data in logs

- [ ] **Monitoring & Logging**
  - [ ] Security event logging
  - [ ] Real-time alerting
  - [ ] SIEM integration
  - [ ] Incident response plan documented

- [ ] **Compliance**
  - [ ] GDPR compliance (EU users)
  - [ ] Data retention policies
  - [ ] Privacy policy updated
  - [ ] Terms of service reviewed

---

**Last Updated:** December 26, 2025  
**Next Review:** March 26, 2026  
**Maintained By:** AI-IMUTIS Security Team
