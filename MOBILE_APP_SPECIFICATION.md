# AI-IMUTIS Mobile Application Specification

**Version:** 1.0  
**Date:** December 26, 2025  
**Platform:** iOS and Android  
**Framework:** React Native with Expo  
**Target Markets:** Cameroon (with future expansion potential)

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Features & Requirements](#features--requirements)
5. [UI/UX Guidelines](#uiux-guidelines)
6. [Authentication & Security](#authentication--security)
7. [Device IP Tracking](#device-ip-tracking)
8. [API Integration](#api-integration)
9. [Performance Requirements](#performance-requirements)
10. [Development Setup](#development-setup)
11. [Testing Strategy](#testing-strategy)
12. [Deployment](#deployment)

---

## Overview

The AI-IMUTIS mobile application is a cross-platform solution for inter-urban mobility booking and urban tourism information in Cameroon. The app leverages AI-powered departure window predictions and real-time traffic updates to enhance user experience.

### Key Objectives

- **Mobility:** Enable users to search, book, and track inter-urban travel with AI-driven departure predictions
- **Tourism:** Provide comprehensive city-based tourism information with location-based recommendations
- **Real-Time:** Display real-time traffic and departure information via WebSocket connections
- **Accessibility:** Support offline functionality for essential features
- **Analytics:** Track user behavior and location patterns with proper device IP identification

### Target Users

- **Primary:** Inter-urban travelers in Cameroon (ages 18-65)
- **Secondary:** Tourists exploring Cameroon's attractions
- **Tertiary:** Drivers and transport operators (future phase)

---

## Technology Stack

### Core Framework

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Framework** | React Native | 0.73+ | Cross-platform iOS/Android with single codebase |
| **Build System** | Expo | 50.0+ | Simplified development, OTA updates, managed build service |
| **Language** | JavaScript/TypeScript | ES2021 | Type safety with TypeScript, modern async/await |
| **State Management** | Redux Toolkit | 1.9+ | Predictable state management, DevTools integration |
| **Navigation** | React Navigation | 6.x+ | Native stack navigation for iOS/Android |
| **HTTP Client** | Axios | 1.6+ | Promise-based, interceptor support for auth tokens |
| **Local Storage** | AsyncStorage | 1.21+ | Persistent key-value storage for caching |
| **Maps** | react-native-maps | 1.8+ | Native maps integration (Google Maps on Android, Apple Maps on iOS) |
| **Geolocation** | expo-location | 16.x+ | GPS and device location access |
| **Authentication** | Firebase Auth | 9.x+ | Email, phone OTP, social sign-in |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | | Real-time notifications and alerts |
| **Analytics** | Firebase Analytics | | User behavior tracking |
| **Testing** | Jest + React Native Testing Library | | Unit and component testing |
| **Code Quality** | ESLint + Prettier | | Consistent code style |

### Native Modules

```json
{
  "expo": {
    "plugins": [
      ["expo-camera", {}],
      ["expo-location", {}],
      ["expo-device", {}],
      ["expo-notifications", {}]
    ]
  }
}
```

---

## Architecture

### Application Structure

```
mobile-app/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Map/
│   │   ├── SearchBar/
│   │   ├── TravelCard/
│   │   ├── AttractionCard/
│   │   └── common/
│   ├── screens/             # Screen components (pages)
│   │   ├── Auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   └── OTPScreen.tsx
│   │   ├── Travel/
│   │   │   ├── SearchScreen.tsx
│   │   │   ├── TravelDetailsScreen.tsx
│   │   │   ├── BookingScreen.tsx
│   │   │   └── BookingHistoryScreen.tsx
│   │   ├── Tourism/
│   │   │   ├── CitiesScreen.tsx
│   │   │   ├── AttractionsScreen.tsx
│   │   │   └── AttractionDetailScreen.tsx
│   │   ├── Profile/
│   │   │   ├── ProfileScreen.tsx
│   │   │   └── SettingsScreen.tsx
│   │   ├── Root/
│   │   │   ├── SplashScreen.tsx
│   │   │   ├── NavigationContainer.tsx
│   │   │   └── BottomTabNavigator.tsx
│   │   └── Notifications/
│   │       └── NotificationsScreen.tsx
│   ├── store/               # Redux store configuration
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── travelSlice.ts
│   │   │   ├── tourismSlice.ts
│   │   │   ├── notificationSlice.ts
│   │   │   └── locationSlice.ts
│   │   └── store.ts
│   ├── services/            # API and external services
│   │   ├── api/
│   │   │   ├── travelAPI.ts
│   │   │   ├── tourismAPI.ts
│   │   │   ├── authAPI.ts
│   │   │   ├── userAPI.ts
│   │   │   └── notificationAPI.ts
│   │   ├── firebase/
│   │   │   ├── firebaseConfig.ts
│   │   │   ├── authService.ts
│   │   │   └── messagingService.ts
│   │   ├── location/
│   │   │   ├── locationService.ts
│   │   │   └── deviceInfoService.ts
│   │   └── storage/
│   │       └── storageService.ts
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useLocation.ts
│   │   ├── useApi.ts
│   │   └── useOfflineMode.ts
│   ├── utils/               # Utility functions
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   ├── dateTime.ts
│   │   └── constants.ts
│   ├── styles/              # Global styles and themes
│   │   ├── theme.ts
│   │   ├── colors.ts
│   │   └── typography.ts
│   ├── types/               # TypeScript type definitions
│   │   ├── auth.ts
│   │   ├── travel.ts
│   │   ├── tourism.ts
│   │   ├── user.ts
│   │   └── index.ts
│   ├── i18n/                # Internationalization
│   │   ├── en.json
│   │   ├── fr.json
│   │   └── i18n.ts
│   ├── assets/              # Images, fonts, icons
│   │   ├── images/
│   │   ├── fonts/
│   │   └── icons/
│   └── App.tsx              # Root component
├── __tests__/               # Test files
│   ├── components/
│   ├── screens/
│   ├── services/
│   └── hooks/
├── .env.example
├── app.json
├── package.json
├── tsconfig.json
├── jest.config.js
└── README.md
```

---

## Features & Requirements

### 1. Authentication & Account Management

#### Features
- Email/password registration and login
- Phone number OTP verification
- Google Sign-In integration
- Apple Sign-In integration (iOS only)
- Biometric authentication (Face ID/Touch ID)
- Password reset and account recovery
- Account deletion with data cleanup
- Session management (view/revoke active devices)

#### Requirements
```typescript
// Authentication interfaces
interface AuthCredentials {
  email?: string;
  phoneNumber?: string;
  password: string;
}

interface OTPData {
  phoneNumber: string;
  verificationId: string;
  code: string;
}

interface User {
  uid: string;
  email?: string;
  phoneNumber?: string;
  displayName: string;
  photoURL?: string;
  preferredLanguage: 'en' | 'fr';
  notificationsEnabled: boolean;
  createdAt: Date;
  lastLogin: Date;
}

interface DeviceSession {
  sessionId: string;
  deviceType: 'iPhone' | 'Android';
  deviceOS: string;
  deviceIP: string;
  lastActivity: Date;
  isActive: boolean;
}
```

#### UI Components
- **LoginScreen:** Email/phone input, password field, social auth buttons
- **RegisterScreen:** Multi-step registration with email verification
- **OTPScreen:** Phone OTP input with auto-detection
- **BiometricSetup:** Enable/disable biometric auth prompt
- **SessionManager:** View and revoke active device sessions

---

### 2. Travel/Mobility Module

#### Features
- Search inter-urban travel routes (origin-destination, date, number of passengers)
- View available trips with real-time departure window estimations
- AI-powered departure time recommendations
- Real-time traffic updates via WebSocket
- Trip booking with multiple payment options
- Booking history and trip tracking
- Download e-tickets
- Driver communication (future phase)

#### Requirements
```typescript
interface SearchQuery {
  origin: City;
  destination: City;
  departureDate: Date;
  passengers: number;
  returnDate?: Date;
}

interface Trip {
  id: string;
  route: Route;
  departureTime: Date;
  estimatedArrivalTime: Date;
  depturePrediction: DeparturePrediction;
  vehicleType: 'minibus' | 'bus' | 'taxi';
  totalSeats: number;
  availableSeats: number;
  pricePerSeat: number;
  driverName: string;
  vehicleRegistration: string;
  currentTraffic?: TrafficUpdate;
}

interface DeparturePrediction {
  estimatedDepartureTime: Date;
  confidence: number; // 0-1
  factors: {
    trafficConditions: string;
    passengerLoadStatus: string;
    timeOfDay: string;
  };
}

interface Booking {
  id: string;
  userId: string;
  trip: Trip;
  passengers: Passenger[];
  bookingDate: Date;
  totalPrice: number;
  status: 'confirmed' | 'pending' | 'cancelled' | 'completed';
  eTicketUrl?: string;
  paymentMethod: 'card' | 'momo' | 'orange_money';
  paymentStatus: 'completed' | 'pending' | 'failed';
}
```

#### UI Components
- **SearchScreen:** Interactive origin-destination selector with date picker
- **TravelResultsScreen:** List of available trips with filtering/sorting
- **TravelDetailsScreen:** Detailed trip info, map visualization, reviews
- **BookingScreen:** Multi-step booking process with passenger info collection
- **BookingConfirmationScreen:** Confirmation with e-ticket download
- **BookingHistoryScreen:** List of past/upcoming bookings with tracking
- **TripTrackingScreen:** Real-time location map and ETA updates

#### Real-Time Features
```typescript
// WebSocket connection for real-time updates
interface RealTimeUpdate {
  tripId: string;
  currentLocation: {
    latitude: number;
    longitude: number;
  };
  currentSpeed: number;
  estimatedArrival: Date;
  trafficStatus: 'light' | 'moderate' | 'heavy';
  departureWindowUpdate: {
    estimatedTime: Date;
    confidence: number;
  };
}
```

---

### 3. Tourism Information Module

#### Features
- Browse cities and attractions
- View detailed attraction information with images and reviews
- Location-based attraction recommendations
- Search attractions by category (restaurants, hotels, museums, etc.)
- View attractions on map
- Save favorite attractions
- Access tourism guides and tips
- Estimated travel times between attractions

#### Requirements
```typescript
interface City {
  id: string;
  name: string;
  region: string;
  description: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  imageUrl: string;
  bestTimeToVisit: string;
}

interface Attraction {
  id: string;
  cityId: string;
  name: string;
  category: 'restaurant' | 'hotel' | 'museum' | 'nature' | 'cultural' | 'shopping';
  description: string;
  imageUrls: string[];
  coordinates: {
    latitude: number;
    longitude: number;
  };
  rating: number; // 1-5
  reviews: Review[];
  openingHours: {
    monday: TimeRange;
    tuesday: TimeRange;
    // ... other days
  };
  contactInfo: {
    phone?: string;
    email?: string;
    website?: string;
  };
  estimatedCost?: number;
  guidedTourAvailable: boolean;
}

interface Review {
  id: string;
  userId: string;
  rating: number;
  comment: string;
  date: Date;
  images?: string[];
}

interface SavedAttraction {
  userId: string;
  attractionId: string;
  savedDate: Date;
  notes?: string;
}
```

#### UI Components
- **CitiesScreen:** Grid/list of cities with images and quick info
- **CityDetailsScreen:** Detailed city info with attractions map
- **AttractionsScreen:** Filterable/searchable list of attractions
- **AttractionDetailScreen:** Full details with images, reviews, booking options
- **MapViewScreen:** Map with attractions, directions, and filters
- **SavedAttractionsScreen:** User's bookmarked attractions
- **ReviewsScreen:** Attraction reviews with photos

---

### 4. Location & Device Tracking

#### Features
- GPS location tracking (with user permission)
- Device IP tracking for session management
- Location history visualization
- Location-based recommendations
- Automatic location update on app foreground/background
- Device session management (view active sessions, revoke devices)

#### Requirements
```typescript
interface DeviceInfo {
  id: string;
  type: 'iPhone' | 'iPad' | 'Android Phone' | 'Android Tablet';
  model: string;
  os: string;
  osVersion: string;
  appVersion: string;
  fingerprint: string;
}

interface LocationData {
  userId: string;
  deviceIP: string;
  latitude: number;
  longitude: number;
  accuracy: number; // meters
  timestamp: Date;
  activityType: 'traveling' | 'browsing' | 'idle';
}

interface SessionTracking {
  sessionId: string;
  userId: string;
  deviceIP: string;
  deviceInfo: DeviceInfo;
  loginTime: Date;
  lastActivity: Date;
  logoutTime?: Date;
  ipRotationDetected: boolean;
}
```

#### UI Components
- **SessionManagerScreen:** View active sessions per device, revoke sessions
- **LocationSettingsScreen:** Control GPS and IP tracking permissions
- **ActivityHistoryScreen:** Timeline of user activity and location history

---

### 5. User Profile & Settings

#### Features
- User profile information (name, phone, email, photo)
- Preferences (language, notifications, privacy settings)
- Payment method management
- Address book for frequent destinations
- User preferences (notification frequency, data usage, etc.)
- Help and support
- App information and version

#### Requirements
```typescript
interface UserProfile {
  uid: string;
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  profilePhoto?: string;
  dateOfBirth?: Date;
  gender?: 'male' | 'female' | 'other';
}

interface UserPreferences {
  userId: string;
  language: 'en' | 'fr';
  currency: 'XAF' | 'USD';
  pushNotificationsEnabled: boolean;
  locationTrackingEnabled: boolean;
  deviceIPTrackingEnabled: boolean;
  dataUsageMode: 'low' | 'normal' | 'high';
  darkModeEnabled: boolean;
  autoRefreshLocation: boolean;
  locationUpdateInterval: number; // seconds
}

interface PaymentMethod {
  id: string;
  userId: string;
  type: 'card' | 'momo' | 'orange_money' | 'bank_transfer';
  last4?: string;
  expiryDate?: string;
  isDefault: boolean;
}

interface SavedAddress {
  id: string;
  userId: string;
  label: string; // 'Home', 'Work', 'Family', etc.
  coordinates: {
    latitude: number;
    longitude: number;
  };
  address: string;
}
```

#### UI Components
- **ProfileScreen:** Display and edit user info
- **SettingsScreen:** App preferences and configurations
- **PaymentMethodsScreen:** Manage payment options
- **SavedAddressesScreen:** Manage frequent destinations
- **NotificationPreferencesScreen:** Control notification types
- **PrivacySettingsScreen:** Control data tracking and sharing
- **HelpScreen:** FAQ, contact support, report issues

---

### 6. Notifications & Real-Time Updates

#### Features
- Push notifications for booking confirmations
- Real-time departure time updates
- Traffic alerts for booked trips
- Attraction recommendations
- Payment confirmations
- System notifications

#### Implementation
```typescript
interface Notification {
  id: string;
  userId: string;
  type: 'booking' | 'departure' | 'traffic' | 'recommendation' | 'payment' | 'system';
  title: string;
  body: string;
  data?: Record<string, string>;
  timestamp: Date;
  isRead: boolean;
  actionUrl?: string;
}

// Firebase Cloud Messaging setup
async function subscribeToDepartureTopic(tripId: string) {
  const messaging = getMessaging();
  await messaging.subscribeToTopic(`trip_${tripId}`);
}

// WebSocket for real-time updates
interface WebSocketMessage {
  type: 'traffic_update' | 'departure_update' | 'notification';
  payload: Record<string, any>;
}
```

---

### 7. Offline Mode

#### Features
- Cached trip search results
- Downloaded attraction information
- Offline map data for major cities
- Saved booking details
- Offline reading of previously viewed content
- Queue actions (bookings, reviews) for sync when online

#### Implementation
```typescript
interface CacheConfig {
  strategies: {
    tripSearch: 'cache-first' | 'network-first';
    attractions: 'cache-first';
    maps: 'cache-first';
    userProfile: 'network-first';
  };
  expirationTime: {
    tripSearch: 3600000; // 1 hour
    attractions: 86400000; // 1 day
    userProfile: 3600000; // 1 hour
  };
  maxCacheSize: 50 * 1024 * 1024; // 50MB
}

interface QueuedAction {
  id: string;
  type: 'booking' | 'review' | 'preference_update';
  payload: any;
  createdAt: Date;
  retryCount: number;
}
```

---

## UI/UX Guidelines

### Design System

#### Color Palette
```typescript
const colors = {
  primary: '#2563EB',      // Blue
  secondary: '#F97316',    // Orange
  success: '#10B981',      // Green
  warning: '#F59E0B',      // Amber
  error: '#EF4444',        // Red
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  background: '#FFFFFF',
  surface: '#F9FAFB',
  text: '#111827',
  textSecondary: '#6B7280',
  border: '#E5E7EB',
};
```

#### Typography
```typescript
const typography = {
  heading1: {
    fontSize: 32,
    fontWeight: '700',
    lineHeight: 40,
  },
  heading2: {
    fontSize: 28,
    fontWeight: '700',
    lineHeight: 36,
  },
  heading3: {
    fontSize: 24,
    fontWeight: '600',
    lineHeight: 32,
  },
  body: {
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: '500',
    lineHeight: 16,
  },
};
```

#### Spacing System
```typescript
const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  '2xl': 32,
  '3xl': 48,
};
```

### Navigation

#### Bottom Tab Navigator (Main App)
```
┌─────────────────────────┐
│        Header           │
├─────────────────────────┤
│                         │
│    Main Content Area    │
│                         │
├─────────────────────────┤
│ Search │Travel│Tourism │
│        │Booking │Profile
└─────────────────────────┘
```

**Tabs:**
1. **Search** - Trip search and discovery
2. **Travel** - Active bookings and trip tracking
3. **Tourism** - City and attraction browsing
4. **Profile** - User account and settings

#### Screen Hierarchy

**Auth Flow:**
```
SplashScreen → LoginScreen → OTPScreen → MainApp
                ↓
            RegisterScreen
```

**Travel Flow:**
```
SearchScreen → TravelResultsScreen → TravelDetailsScreen → BookingScreen
    ↓
BookingHistoryScreen → TripDetailsScreen
```

**Tourism Flow:**
```
CitiesScreen → CityDetailsScreen → AttractionsScreen → AttractionDetailScreen
```

### Accessibility

- **Minimum touch target:** 48x48 dp
- **Text contrast ratio:** 4.5:1 for normal text, 3:1 for large text
- **Font scaling:** Support system font size scaling
- **VoiceOver/TalkBack:** Full support for screen readers
- **Haptic feedback:** Subtle vibrations for important actions
- **High contrast mode:** Automatic adaptation

---

## Authentication & Security

### Firebase Authentication

```typescript
import { initializeApp } from 'firebase/app';
import { 
  initializeAuth,
  getReactNativePersistence,
} from 'firebase/auth';
import AsyncStorage from '@react-native-async-storage/async-storage';

const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);

export const auth = initializeAuth(app, {
  persistence: getReactNativePersistence(AsyncStorage),
});
```

### Security Best Practices

1. **Token Management:**
   - Store Firebase ID tokens securely in AsyncStorage
   - Refresh tokens automatically on app foreground
   - Clear tokens on logout
   - Set token expiry monitoring

2. **Data Encryption:**
   - Use HTTPS/TLS for all API communications
   - Encrypt sensitive data at rest (AsyncStorage)
   - Use secure storage for API keys

3. **Request Validation:**
   - Validate all user inputs before sending to API
   - Use TypeScript for type safety
   - Implement certificate pinning for HTTPS

4. **API Security:**
   - Include Firebase token in Authorization header
   - Include device IP header for tracking
   - Implement request signing for sensitive operations
   - Validate server SSL certificates

```typescript
// API Interceptor for auth and security headers
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

apiClient.interceptors.request.use(async (config) => {
  const firebaseToken = await auth.currentUser?.getIdToken();
  const deviceInfo = await getDeviceInfo();

  config.headers.Authorization = `Bearer ${firebaseToken}`;
  config.headers['X-Device-Fingerprint'] = deviceInfo.fingerprint;
  config.headers['X-Device-IP'] = deviceInfo.currentIP;
  config.headers['X-App-Version'] = APP_VERSION;

  return config;
});
```

---

## Device IP Tracking

### Overview

Device IP tracking provides:
- Session management (view/revoke active devices)
- Location-based analytics
- Fraud detection (IP rotation monitoring)
- User activity auditing

### Implementation

#### Getting Device IP

```typescript
// services/deviceInfoService.ts
import * as Network from 'expo-network';
import { getUniqueId, getModel, getSystemVersion } from 'react-native-device-info';
import { Platform } from 'react-native';

export interface DeviceInfo {
  id: string;
  type: Platform.OS === 'ios' ? 'iPhone' : 'Android';
  model: string;
  os: Platform.OS;
  osVersion: string;
  fingerprint: string;
  currentIP?: string;
}

export async function getDeviceInfo(): Promise<DeviceInfo> {
  try {
    const ipAddress = await Network.getIpAddressAsync();
    
    return {
      id: getUniqueId(),
      type: Platform.OS === 'ios' ? 'iPhone' : 'Android',
      model: getModel(),
      os: Platform.OS,
      osVersion: getSystemVersion(),
      fingerprint: `${getModel()}-${getSystemVersion()}-${getUniqueId()}`,
      currentIP: ipAddress,
    };
  } catch (error) {
    console.error('Error getting device info:', error);
    return {
      id: getUniqueId(),
      type: Platform.OS === 'ios' ? 'iPhone' : 'Android',
      model: getModel(),
      os: Platform.OS,
      osVersion: getSystemVersion(),
      fingerprint: `${getModel()}-${getSystemVersion()}-${getUniqueId()}`,
    };
  }
}
```

#### Location Tracking with IP

```typescript
// hooks/useLocationTracking.ts
import { useEffect } from 'react';
import * as Location from 'expo-location';
import { useAppDispatch } from '../store/store';
import { updateLocation } from '../store/slices/locationSlice';
import { travelAPI } from '../services/api/travelAPI';
import { getDeviceInfo } from '../services/location/deviceInfoService';

export function useLocationTracking() {
  const dispatch = useAppDispatch();
  const { user } = useAuth();

  useEffect(() => {
    if (!user) return;

    const startTracking = async () => {
      // Request permission
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.log('Permission to access location was denied');
        return;
      }

      // Watch position with 10-second interval, 100-meter threshold
      const subscription = await Location.watchPositionAsync(
        {
          accuracy: Location.LocationAccuracy.Balanced,
          timeInterval: 10000,
          distanceInterval: 100,
        },
        async (location) => {
          const deviceInfo = await getDeviceInfo();

          const locationData = {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            accuracy_meters: location.coords.accuracy,
            device_ip: deviceInfo.currentIP,
            activity_type: 'traveling',
          };

          // Update local state
          dispatch(updateLocation(locationData));

          // Send to backend
          try {
            await travelAPI.trackLocation(locationData);
          } catch (error) {
            console.error('Error tracking location:', error);
            // Queue for sync when online
          }
        }
      );

      return () => subscription.remove();
    };

    startTracking();
  }, [user, dispatch]);
}
```

#### Session Management UI

```typescript
// screens/Profile/SessionManagerScreen.tsx
import React, { useEffect, useState } from 'react';
import {
  View,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Text,
} from 'react-native';
import { userAPI } from '../../services/api/userAPI';
import { DeviceSession } from '../../types/user';

export function SessionManagerScreen() {
  const [sessions, setSessions] = useState<DeviceSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await userAPI.getSessions();
      setSessions(response.sessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await userAPI.revokeSession(sessionId);
      setSessions(sessions.filter(s => s.sessionId !== sessionId));
    } catch (error) {
      console.error('Error revoking session:', error);
    }
  };

  const renderSession = ({ item }: { item: DeviceSession }) => (
    <View style={styles.sessionCard}>
      <View style={styles.sessionInfo}>
        <Text style={styles.deviceType}>{item.deviceType}</Text>
        <Text style={styles.deviceOS}>{item.deviceOS}</Text>
        <Text style={styles.deviceIP}>{item.deviceIP}</Text>
        <Text style={styles.lastActivity}>
          Last active: {new Date(item.lastActivity).toLocaleString()}
        </Text>
      </View>
      <TouchableOpacity
        style={styles.revokeButton}
        onPress={() => handleRevokeSession(item.sessionId)}
      >
        <Text style={styles.revokeText}>Revoke</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={sessions}
        renderItem={renderSession}
        keyExtractor={item => item.sessionId}
        onRefresh={loadSessions}
        refreshing={loading}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  sessionCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    marginHorizontal: 12,
    marginVertical: 6,
    backgroundColor: 'white',
    borderRadius: 8,
  },
  sessionInfo: {
    flex: 1,
  },
  deviceType: {
    fontSize: 16,
    fontWeight: '600',
  },
  deviceOS: {
    fontSize: 14,
    color: '#666',
  },
  deviceIP: {
    fontSize: 12,
    color: '#999',
    fontFamily: 'monospace',
  },
  lastActivity: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  revokeButton: {
    backgroundColor: '#EF4444',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  revokeText: {
    color: 'white',
    fontWeight: '600',
  },
});
```

---

## API Integration

### API Base Configuration

```typescript
// services/api/config.ts
import axios from 'axios';
import { auth } from '../../services/firebase/firebaseConfig';
import { getDeviceInfo } from '../location/deviceInfoService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.ai-imutis.com';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(async (config) => {
  try {
    // Add Firebase token
    const currentUser = auth.currentUser;
    if (currentUser) {
      const token = await currentUser.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add device info
    const deviceInfo = await getDeviceInfo();
    config.headers['X-Device-Fingerprint'] = deviceInfo.fingerprint;
    config.headers['X-Device-IP'] = deviceInfo.currentIP;
    config.headers['X-App-Version'] = process.env.REACT_APP_VERSION;

    return config;
  } catch (error) {
    console.error('Error in request interceptor:', error);
    return config;
  }
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      await auth.signOut();
      // Navigate to login screen
    }
    return Promise.reject(error);
  }
);

export { apiClient, API_BASE_URL };
```

### Key API Service Modules

#### Travel API
```typescript
// services/api/travelAPI.ts
export const travelAPI = {
  async searchTrips(query: SearchQuery) {
    const response = await apiClient.get('/api/travels', {
      params: query,
    });
    return response.data;
  },

  async getTripDetails(tripId: string) {
    const response = await apiClient.get(`/api/travels/${tripId}`);
    return response.data;
  },

  async bookTrip(bookingData: BookingRequest) {
    const response = await apiClient.post('/api/travels/book', bookingData);
    return response.data;
  },

  async getBookingHistory() {
    const response = await apiClient.get('/api/travels/bookings');
    return response.data;
  },

  async trackLocation(locationData: LocationData) {
    const response = await apiClient.post('/api/users/locations/track', locationData);
    return response.data;
  },
};
```

#### User API
```typescript
// services/api/userAPI.ts
export const userAPI = {
  async getProfile() {
    const response = await apiClient.get('/api/users/profile');
    return response.data;
  },

  async updateProfile(profile: Partial<UserProfile>) {
    const response = await apiClient.put('/api/users/profile', profile);
    return response.data;
  },

  async getSessions() {
    const response = await apiClient.get('/api/users/sessions');
    return response.data;
  },

  async revokeSession(sessionId: string) {
    const response = await apiClient.delete(`/api/users/sessions/${sessionId}`);
    return response.data;
  },

  async updatePreferences(preferences: Partial<UserPreferences>) {
    const response = await apiClient.put('/api/users/preferences', preferences);
    return response.data;
  },
};
```

---

## Performance Requirements

### Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **App Startup Time** | <2 seconds | From launch to main screen |
| **Search Response** | <1 second | API response time |
| **Screen Navigation** | <300ms | Transition animation |
| **Trip Details Load** | <800ms | All data loaded including map |
| **Map Render** | <500ms | Initial map + markers |
| **Location Update** | Every 10 seconds | GPS accuracy within 20m |
| **Offline Mode Activation** | <1 second | Auto-switch on connectivity loss |
| **API Retry Success** | >95% | Network resilience |
| **Memory Usage** | <150MB | Average RAM consumption |
| **Battery Impact** | <5% per hour | With background location tracking |

### Performance Optimization Strategies

1. **Code Splitting:** Lazy load screens not in primary navigation
2. **Image Optimization:** Use `Image.resolveAssetSource` for caching
3. **List Virtualization:** FlatList with `maxToRenderPerBatch`
4. **State Management:** Redux Toolkit for efficient state updates
5. **API Caching:** Axios cache adapter for frequent requests
6. **Bundle Size:** Target <5MB for initial bundle

---

## Development Setup

### Prerequisites

```bash
# Check versions
node --version  # v18.0.0+
npm --version   # v9.0.0+
git --version

# macOS/Windows/Linux
# Install Xcode (macOS) or Android Studio
```

### Installation

```bash
# Clone repository
git clone https://github.com/ai-imutis/mobile-app.git
cd mobile-app

# Install dependencies
npm install

# Install Expo CLI
npm install -g expo-cli

# Setup environment
cp .env.example .env
# Edit .env with your Firebase and API credentials
```

### Running the App

```bash
# Start Expo development server
npm start

# Run on iOS simulator (macOS only)
npm run ios

# Run on Android emulator
npm run android

# Run on physical device
# Scan QR code with Expo Go app

# Run web version
npm run web
```

### Development Tools

```bash
# Linting and formatting
npm run lint
npm run format

# Run tests
npm test
npm test -- --coverage

# Build for production
npm run build:ios
npm run build:android
eas build --platform ios
eas build --platform android

# Preview production build
eas build --platform ios --profile preview
```

---

## Testing Strategy

### Unit Tests

```typescript
// __tests__/services/locationService.test.ts
import { getDeviceInfo } from '../../services/location/deviceInfoService';

describe('Device Info Service', () => {
  test('should return device info object', async () => {
    const deviceInfo = await getDeviceInfo();
    
    expect(deviceInfo).toHaveProperty('id');
    expect(deviceInfo).toHaveProperty('type');
    expect(deviceInfo).toHaveProperty('os');
    expect(deviceInfo.fingerprint).toMatch(/^.+-$/);
  });

  test('should get device IP address', async () => {
    const deviceInfo = await getDeviceInfo();
    
    expect(deviceInfo.currentIP).toMatch(/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/);
  });
});
```

### Component Tests

```typescript
// __tests__/screens/SessionManagerScreen.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { SessionManagerScreen } from '../../screens/Profile/SessionManagerScreen';

describe('SessionManagerScreen', () => {
  test('should display sessions list', async () => {
    const mockSessions = [
      {
        sessionId: '1',
        deviceType: 'iPhone',
        deviceOS: 'iOS 17.2',
        deviceIP: '192.168.1.1',
        lastActivity: new Date().toISOString(),
        isActive: true,
      },
    ];

    render(<SessionManagerScreen />);
    
    expect(screen.getByText('iPhone')).toBeTruthy();
    expect(screen.getByText('iOS 17.2')).toBeTruthy();
  });
});
```

### Integration Tests

```bash
# Run end-to-end tests with Detox
npm run e2e

# Test authentication flow
npm run e2e -- --testNamePattern="Authentication"

# Test travel booking flow
npm run e2e -- --testNamePattern="Booking"
```

### Test Coverage

Target **>80% code coverage** with focus on:
- Authentication flows
- API integration
- Location tracking
- Offline mode
- Error handling

---

## Deployment

### Release Process

#### iOS Release
```bash
# Build for iOS
eas build --platform ios --auto-submit

# Or manual build and submit
eas build --platform ios
# Wait for build completion
eas submit --platform ios
```

#### Android Release
```bash
# Build for Android
eas build --platform android --auto-submit

# Or manual build and submit
eas build --platform android
# Wait for build completion
eas submit --platform android
```

### App Store Requirements

**iOS (Apple App Store):**
- Privacy policy
- Usage description for permissions (location, camera, contacts)
- App signing certificate
- Screenshots and app description
- Contact email and support URL

**Android (Google Play Store):**
- Privacy policy
- Permissions justification
- Google Play Developer account
- Screenshots and app description
- Content rating questionnaire

### Version Management

```json
{
  "expo": {
    "version": "1.0.0",
    "runtimeVersion": "1.0.0",
    "updates": {
      "enabled": true,
      "checkAutomatically": "ON_APP_START",
      "fallbackToCacheTimeout": 30000,
      "url": "https://updates.expo.dev/project-id"
    }
  }
}
```

### Over-the-Air (OTA) Updates

```bash
# Build and publish update
eas update --branch production --message "Bug fixes and improvements"

# Monitor updates
eas update --list

# Rollback if needed
eas update --branch production --rollback
```

---

## Monitoring & Analytics

### Firebase Analytics Events

```typescript
// Track major user actions
import { logEvent } from 'firebase/analytics';
import { analytics } from '../../services/firebase/firebaseConfig';

// User events
logEvent(analytics, 'user_signup', { method: 'email' });
logEvent(analytics, 'user_login', { method: 'phone_otp' });

// Travel events
logEvent(analytics, 'search_trips', {
  origin: 'Douala',
  destination: 'Yaoundé',
  passengers: 2,
});

logEvent(analytics, 'trip_booked', {
  tripId: 'trip-123',
  totalPrice: 50000,
  paymentMethod: 'momo',
});

// Tourism events
logEvent(analytics, 'attraction_viewed', {
  cityId: 'city-123',
  attractionId: 'attr-456',
  category: 'restaurant',
});
```

### Crash Reporting

```typescript
import { crashlytics } from '@react-native-firebase/crashlytics';

// Log non-fatal errors
try {
  someRiskyOperation();
} catch (error) {
  crashlytics().recordError(error);
}

// Set user context
crashlytics().setUserId(userId);
crashlytics().setAttribute('device_ip', deviceIP);
```

---

## Support & Maintenance

### Common Issues

**Issue:** "Device IP not being captured"
- **Solution:** Check X-Forwarded-For header in API requests
- **Debug:** Enable request logging with `axios-debug`

**Issue:** "Location tracking not working"
- **Solution:** Request foreground location permissions
- **Debug:** Check location service in device settings

**Issue:** "App crashes on Android"
- **Solution:** Update android-gradle-plugin in gradle.properties
- **Debug:** Check Android Studio logcat

### Documentation

- **Developer Docs:** `/docs/MOBILE_DEV_GUIDE.md`
- **API Reference:** `https://api.ai-imutis.com/docs`
- **Troubleshooting:** `/docs/TROUBLESHOOTING.md`
- **Changelog:** `/CHANGELOG.md`

---

## References

- [React Native Documentation](https://reactnative.dev)
- [Expo Documentation](https://docs.expo.dev)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [React Navigation](https://reactnavigation.org)
- [Redux Toolkit](https://redux-toolkit.js.org)

---

**Status:** Production Ready  
**Last Updated:** December 26, 2025  
**Maintained By:** AI-IMUTIS Mobile Team
