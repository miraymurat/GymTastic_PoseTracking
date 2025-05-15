# GymTastic Backend

This is the backend API for the GymTastic mobile application, built with Flask. The application provides real-time exercise form detection and validation using pose detection technology. This backend serves the GymTastic mobile app, providing APIs for user authentication and real-time form analysis.

## Mobile App Integration

The backend is designed to work seamlessly with the GymTastic mobile app, providing:
- RESTful APIs for mobile app features
- Real-time exercise form analysis using device camera
- Secure user authentication
- Efficient data synchronization

## Features

- 🔐 User Authentication (Email/Password)
- 🎯 Real-time Exercise Form Detection
- 👥 User Profile Management
- 📱 Mobile-optimized API responses
- 📸 Camera integration for form analysis

## Tech Stack

- **Backend Framework**: Flask
- **Authentication**: JWT Tokens
- **Pose Detection**: MediaPipe
- **Testing**: Pytest
- **Mobile Integration**: RESTful APIs

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git
- Mobile development environment (for testing mobile integration)

## Setup



Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
FLASK_APP=app.main:create_app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

## Running the Server

Start the development server:
```bash
# Development
flask run --host=0.0.0.0 --port=8000

# Production
gunicorn "app.main:create_app()" --bind 0.0.0.0:8000
```

The API will be available at `http://localhost:8000`

## Mobile App Integration

### API Base URL
For development:
```
http://localhost:8000
```

For production:
```
https://api.gymtastic.com
```

### Mobile App Requirements
- Android 6.0+ or iOS 13.0+
- Camera access for form detection
- Internet connection for API communication

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user details
- `POST /api/auth/refresh-token` - Refresh access token

### Pose Detection
- `POST /api/pose/analyze` - Analyze exercise form
- `POST /api/pose/feedback` - Get form feedback
- `POST /api/pose/calibrate` - Calibrate pose detection

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=app tests/
```

## Project Structure

```
backend/
├── app/
│   ├── routes/         # API endpoints
│   │   ├── auth.py
│   │   ├── pose_detection.py
│   │   └── user.py
│   ├── models/         # Database models
│   │   ├── base.py
│   │   ├── user.py
│   │   └── pose_detection.py
│   ├── utils/          # Utility functions
│   │   ├── auth.py
│   │   └── error_handler.py
│   └── main.py         # Application entry point
├── tests/              # Test files
│   ├── test_auth.py
│   └── test_pose_detection.py
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



