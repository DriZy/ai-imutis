# Mobile App Repository Setup Guide

**Created from:** AI-IMUTIS Project Documentation  
**Date:** December 26, 2025  
**For:** Setting up independent mobile app development repository

---

## Quick Start

This guide helps you set up a new repository for mobile app development using the AI-IMUTIS mobile specification.

### 1. Initialize New Repository

```bash
# Create new directory
mkdir ai-imutis-mobile-app
cd ai-imutis-mobile-app

# Initialize Git
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create initial structure
mkdir -p src/{screens,components,services,store,hooks,utils,types,styles,i18n,assets}
mkdir -p __tests__/{screens,components,services,hooks}
mkdir -p docs
```

### 2. Initialize React Native + Expo Project

```bash
# Option A: Using Expo CLI (Recommended)
npx create-expo-app ai-imutis --template

# Option B: Using TypeScript template
npx create-expo-app ai-imutis --template --typescript

# Navigate to project
cd ai-imutis

# Install additional dependencies
npm install \
  @react-navigation/native @react-navigation/bottom-tabs @react-navigation/stack \
  react-native-screens react-native-safe-area-context \
  @reduxjs/toolkit react-redux \
  axios \
  firebase \
  react-native-maps \
  expo-location \
  expo-device \
  expo-notifications \
  @react-native-async-storage/async-storage \
  react-native-device-info \
  react-native-gesture-handler \
  i18next react-i18next \
  @testing-library/react-native \
  jest

# Dev dependencies
npm install --save-dev \
  @types/react-native \
  @types/jest \
  typescript \
  eslint \
  prettier \
  @react-native-community/eslint-config
```

### 3. Project Configuration Files

#### `.env.example`
```bash
# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
REACT_APP_FIREBASE_PROJECT_ID=your_firebase_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
REACT_APP_FIREBASE_APP_ID=your_firebase_app_id

# API Configuration
REACT_APP_API_URL=https://api.ai-imutis.com
REACT_APP_API_TIMEOUT=15000

# App Configuration
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
```

#### `app.json` (Expo Configuration)
```json
{
  "expo": {
    "name": "AI-IMUTIS",
    "slug": "ai-imutis",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": ["**/*"],
    "ios": {
      "supportsTabletMode": true,
      "bundleIdentifier": "com.aiimutis.mobile",
      "buildNumber": "1",
      "infoPlist": {
        "NSLocationWhenInUseUsageDescription": "This app needs your location for travel search and tracking.",
        "NSCameraUsageDescription": "Camera access is needed for document verification.",
        "NSPhotoLibraryUsageDescription": "Photo library access is needed for profile pictures."
      }
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.aiimutis.mobile",
      "versionCode": 1,
      "permissions": [
        "INTERNET",
        "ACCESS_COARSE_LOCATION",
        "ACCESS_FINE_LOCATION",
        "CAMERA",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE"
      ]
    },
    "web": {
      "favicon": "./assets/favicon.png"
    },
    "plugins": [
      ["expo-camera"],
      ["expo-location"],
      ["expo-device"],
      ["expo-notifications"]
    ],
    "updates": {
      "enabled": true,
      "checkAutomatically": "ON_APP_START",
      "fallbackToCacheTimeout": 30000
    }
  }
}
```

#### `tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@screens/*": ["src/screens/*"],
      "@services/*": ["src/services/*"],
      "@store/*": ["src/store/*"],
      "@hooks/*": ["src/hooks/*"],
      "@utils/*": ["src/utils/*"],
      "@types/*": ["src/types/*"],
      "@styles/*": ["src/styles/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### `.eslintrc.js`
```javascript
module.exports = {
  root: true,
  extends: ['@react-native-community', 'prettier'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-unused-vars': [
      'error',
      { argsIgnorePattern: '^_' },
    ],
    'react-native/no-unused-styles': 'warn',
    'react-native/no-inline-styles': 'warn',
  },
};
```

#### `.prettierrc.js`
```javascript
module.exports = {
  arrowParens: 'always',
  bracketSameLine: false,
  bracketSpacing: true,
  semi: true,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'es5',
  useTabs: false,
};
```

### 4. Core Application Files

#### `src/types/index.ts` (Type Definitions)
```typescript
// User types
export interface User {
  uid: string;
  email?: string;
  phoneNumber?: string;
  displayName: string;
  photoURL?: string;
  preferredLanguage: 'en' | 'fr';
  createdAt: Date;
}

export interface AuthCredentials {
  email?: string;
  phoneNumber?: string;
  password: string;
}

// Travel types
export interface Trip {
  id: string;
  origin: string;
  destination: string;
  departureTime: Date;
  availableSeats: number;
  pricePerSeat: number;
  driverName: string;
}

export interface Booking {
  id: string;
  userId: string;
  tripId: string;
  bookingDate: Date;
  totalPrice: number;
  status: 'confirmed' | 'pending' | 'cancelled';
}

// Tourism types
export interface City {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
}

export interface Attraction {
  id: string;
  cityId: string;
  name: string;
  category: string;
  description: string;
  rating: number;
}

// Device tracking
export interface DeviceSession {
  sessionId: string;
  deviceType: string;
  deviceOS: string;
  deviceIP: string;
  lastActivity: Date;
  isActive: boolean;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: Date;
}
```

#### `src/services/firebase/firebaseConfig.ts`
```typescript
import { initializeApp } from 'firebase/app';
import {
  initializeAuth,
  getReactNativePersistence,
} from 'firebase/auth';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getAnalytics } from 'firebase/analytics';
import { getMessaging } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);

export const auth = initializeAuth(app, {
  persistence: getReactNativePersistence(AsyncStorage),
});

export const analytics = getAnalytics(app);
export const messaging = getMessaging(app);

export default app;
```

#### `src/services/api/config.ts`
```typescript
import axios from 'axios';
import { auth } from '../firebase/firebaseConfig';
import { getDeviceInfo } from '../location/deviceInfoService';

const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'https://api.ai-imutis.com';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '15000'),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(async (config) => {
  try {
    const currentUser = auth.currentUser;
    if (currentUser) {
      const token = await currentUser.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }

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
      await auth.signOut();
    }
    return Promise.reject(error);
  }
);

export { apiClient, API_BASE_URL };
```

### 5. Package.json Scripts

```json
{
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "lint": "eslint src/**/*.{ts,tsx}",
    "lint:fix": "eslint src/**/*.{ts,tsx} --fix",
    "format": "prettier --write src/**/*.{ts,tsx,json}",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "type-check": "tsc --noEmit",
    "build:ios": "eas build --platform ios",
    "build:android": "eas build --platform android",
    "submit:ios": "eas submit --platform ios",
    "submit:android": "eas submit --platform android"
  }
}
```

### 6. Git Configuration

#### `.gitignore`
```
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp
.pnp.js

# Testing
coverage/
.nyc_output/

# Build
dist/
build/
*.jsbundle

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Expo
.expo/
.expo-shared/

# Mobile
# Xcode
ios/Pods/
ios/Podfile.lock
*.xcworkspace/

# Android
android/local.properties
android/.gradle/
android/app/debug/
android/app/release/

# OS
Thumbs.db
desktop.ini

# Logs
*.log
```

#### `.gitattributes`
```
* text=auto
*.js text eol=lf
*.json text eol=lf
*.ts text eol=lf
*.tsx text eol=lf
*.md text eol=lf
```

### 7. Documentation Structure

Create these documentation files in the new repository:

```
docs/
├── GETTING_STARTED.md
├── ARCHITECTURE.md
├── CODING_STANDARDS.md
├── TESTING.md
├── DEPLOYMENT.md
└── TROUBLESHOOTING.md
```

#### `docs/GETTING_STARTED.md`
```markdown
# Getting Started with AI-IMUTIS Mobile App

## Prerequisites
- Node.js v18+
- npm v9+ or yarn
- Xcode 14+ (for iOS)
- Android Studio (for Android)
- Expo CLI

## Installation

1. Clone the repository
2. Install dependencies: `npm install`
3. Create `.env` from `.env.example`
4. Configure Firebase credentials
5. Start development: `npm start`

## Folder Structure
[Reference MOBILE_APP_SPECIFICATION.md for full structure]
```

### 8. Initial Commits

```bash
# First commit
git add .
git commit -m "chore: initialize React Native + Expo project structure"

# Create branches
git checkout -b develop
git push origin develop

# Feature branches for development
git checkout -b feature/authentication
git checkout -b feature/travel-search
git checkout -b feature/tourism
git checkout -b feature/device-tracking
```

---

## Key References from AI-IMUTIS Documentation

When developing the mobile app, reference these sections:

1. **Technology Stack:** See MOBILE_APP_SPECIFICATION.md section 2
2. **Architecture:** See MOBILE_APP_SPECIFICATION.md section 3
3. **Features:** See MOBILE_APP_SPECIFICATION.md section 4
4. **API Integration:** See MOBILE_APP_SPECIFICATION.md section 8
5. **Device IP Tracking:** See DEVICE_IP_TRACKING.md section "Frontend Implementation"
6. **Authentication:** See IMPLEMENTATION_PROMPT.md section 1.5.1
7. **API Endpoints:** See ARCHITECTURE_REFERENCE.md API endpoints section

---

## Development Workflow

### Working on a Feature

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 2. Develop and test
npm run test:watch
npm run lint:fix

# 3. Commit changes
git add src/
git commit -m "feat: add my feature"

# 4. Push and create PR
git push origin feature/my-feature
# Create pull request on GitHub

# 5. After review and merge
git checkout develop
git pull origin develop
git branch -d feature/my-feature
```

### Code Quality

```bash
# Before committing
npm run type-check
npm run lint
npm run test

# Auto-format code
npm run format

# Check bundle size
npx expo-optimize
```

---

## Key Commands Reference

```bash
# Development
npm start              # Start Expo development server
npm run ios            # Run on iOS simulator
npm run android        # Run on Android emulator

# Code Quality
npm run lint           # Check code style
npm run lint:fix       # Auto-fix linting issues
npm run format         # Format with Prettier
npm run type-check     # Check TypeScript

# Testing
npm test               # Run tests
npm run test:watch     # Watch mode
npm run test:coverage  # Generate coverage

# Building
npm run build:ios      # Build for iOS App Store
npm run build:android  # Build for Google Play Store
```

---

## Next Steps

1. ✅ Set up repository with this guide
2. 📖 Read MOBILE_APP_SPECIFICATION.md completely
3. 🔐 Configure Firebase Authentication
4. 🌍 Set up API endpoints
5. 🗺️ Integrate Google Maps
6. 📍 Implement location tracking
7. 📱 Build authentication screens
8. 🔍 Build travel search screens
9. 🎫 Build booking flow
10. 🧪 Write comprehensive tests
11. 🚀 Deploy to beta testers
12. 📦 Release to App Stores

---

**Last Updated:** December 26, 2025  
**Based on:** AI-IMUTIS Project Documentation v1.0
