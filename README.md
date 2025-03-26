# Blockchain-Based Voting System with Biometric Authentication

A secure and transparent voting system that uses blockchain technology for vote storage and biometric authentication (face and fingerprint) for voter verification.

## Technology Stack

### Backend
- Python 3.10
- Flask (Web Framework)
- JWT (Authentication)
- Blockchain Implementation (Custom)
- Basic Image Processing (No AI/ML currently)

### Frontend
- React.js
- Material-UI
- WebRTC (for camera access)
- Axios (HTTP client)

## Features Implemented

### Authentication
- JWT-based authentication system
- Secure login endpoint
- Token-based API access

### Voter Verification
- Automated face verification in demo mode
- Automated fingerprint verification in demo mode
- Voter ID validation
- Multi-step verification process
- Camera integration for face capture
- Demo mode for testing and development

### Blockchain Integration
- Custom blockchain implementation
- Block creation and mining
- Vote recording in blockchain
- Genesis block creation
- Chain validation

### Security Features
- Biometric data encryption
- Secure token management
- Blockchain immutability
- Vote deduplication

## Current Issues

1. **Blockchain Service**
   - Nonce initialization issue in Block class
   - Pending transactions handling needs improvement
   - Chain validation optimization required

2. **Fingerprint Service**
   - Scanner connection status management
   - Error handling for disconnected scanner
   - Simulated fingerprint data integration

3. **Frontend**
   - React warnings in VoterVerification component
   - Video ref cleanup in useEffect
   - Unused state variables
   - ESLint warnings for unused variables

4. **API Endpoints**
   - Some 404 errors for certain routes
   - Authentication token handling improvements needed
   - Error response standardization required

## Demo Mode Features

1. **Automated Verification**
   - Face verification automatically succeeds
   - Fingerprint verification automatically succeeds
   - Voter ID verification automatically succeeds
   - Camera integration for face capture
   - Simulated biometric data handling

2. **Testing Capabilities**
   - Quick verification process
   - No actual biometric verification required
   - Easy testing of voting flow
   - Blockchain transaction testing

## Pending Tasks

1. **AI/ML Integration**
   - [ ] Implement face recognition using TensorFlow/PyTorch
   - [ ] Add fingerprint recognition model
   - [ ] Set up model training pipeline
   - [ ] Implement model versioning
   - [ ] Add model performance monitoring

2. **Backend Improvements**
   - [ ] Fix Block class nonce initialization
   - [ ] Implement proper error handling for biometric services
   - [ ] Add data persistence for blockchain
   - [ ] Implement proper logging system
   - [ ] Add rate limiting for API endpoints

3. **Frontend Enhancements**
   - [ ] Fix React warnings in VoterVerification component
   - [ ] Improve error handling and user feedback
   - [ ] Add loading states for all operations
   - [ ] Implement proper form validation
   - [ ] Add responsive design improvements

4. **Security Enhancements**
   - [ ] Implement proper session management
   - [ ] Add request validation middleware
   - [ ] Implement rate limiting
   - [ ] Add input sanitization
   - [ ] Implement proper error logging

5. **Testing**
   - [ ] Add unit tests for blockchain service
   - [ ] Add integration tests for API endpoints
   - [ ] Add frontend component tests
   - [ ] Implement end-to-end testing
   - [ ] Add performance testing

## Setup Instructions

1. Clone the repository
2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
4. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```
5. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

## API Endpoints

### Authentication
- POST `/login` - User login
- GET `/scanner/status` - Get fingerprint scanner status

### Verification
- POST `/verify/voter-id` - Verify voter ID
- POST `/verify/face` - Verify face biometric
- POST `/verify/fingerprint` - Verify fingerprint

### Voting
- POST `/vote` - Cast vote
- GET `/blockchain` - View blockchain data

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

