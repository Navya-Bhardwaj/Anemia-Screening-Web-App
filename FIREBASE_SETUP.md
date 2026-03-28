# Firebase Setup Guide

## 🔧 Firebase Configuration

### ✅ **Your Project is Already Configured!**

**Project Details:**
- **Project ID**: `anemia-screening-tool`
- **Auth Domain**: `anemia-screening-tool.firebaseapp.com`
- **Storage Bucket**: `anemia-screening-tool.firebasestorage.app`
- **Sender ID**: `601289680510`
- **App ID**: `1:601289680510:web:d78df440919c456d0a5a2f`
- **Measurement ID**: `G-MHLZNE5XCY`

### 📋 **Next Steps**

#### 1. Download Service Account Key
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `anemia-screening-tool`
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Download the JSON file
6. Replace the placeholder `serviceAccountKey.json` with the real one

#### 2. Enable Authentication Methods
1. Go to Authentication → Sign-in method
2. Enable **Email/Password** and **Google** providers
3. Add `localhost` to authorized domains for development

#### 3. Setup Firestore Database
1. Go to Firestore Database
2. Create a new database in test mode
3. Create these collections:
   - `users` (for user profiles and screening history)
   - `screenings` (for individual screening records)

#### 4. Setup Security Rules
1. Go to Firestore Database → Rules
2. Replace existing rules with one of these options:

**Option 1: Simple Rules (Recommended for start)**
- Copy contents from `firestore_simple.rules`
- Covers basic user data protection

**Option 2: Advanced Rules (Full features)**
- Copy contents from `firestore.rules` 
- Includes doctor consultations, chat, analytics

3. Click "Publish" to apply rules

#### 5. Enable Authentication Methods
Update the `firebaseConfig` object in `login_enhanced.html` with your project credentials:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};
```

### 6. Security Rules
Add these Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own documents
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Users can create screening records for themselves
    match /screenings/{screeningId} {
      allow create: if request.auth != null && 
        request.auth.uid == resource.data.userId;
      allow read: if request.auth != null && 
        request.auth.uid == resource.data.userId;
    }
  }
}
```

## 🚀 Features Available

### Authentication
- ✅ Email/Password authentication
- ✅ Google OAuth integration
- ✅ User registration
- ✅ Session management
- ✅ Protected routes

### Database Integration
- ✅ User profile storage
- ✅ Screening history tracking
- ✅ Progress analytics
- ✅ Data persistence

### ML Screening
- ✅ Advanced feature extraction
- ✅ Multi-factor risk assessment
- ✅ Confidence scoring
- ✅ Detailed analysis reports

## 📱 Usage

1. **Without Firebase**: App works with session-based storage
2. **With Firebase**: Full authentication and database features
3. **ML Features**: Always available with enhanced analysis

## 🔒 Security Notes

- Never commit `serviceAccountKey.json` to version control
- Use environment variables for production secrets
- Enable App Check for additional security
- Regularly update Firebase security rules
