from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationError(APIError):
    """Exception for validation errors."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(APIError):
    """Exception for authentication errors."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(APIError):
    """Exception for authorization errors."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)

class NotFoundError(APIError):
    """Exception for not found errors."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=404, payload=payload)

class ConflictError(APIError):
    """Exception for conflict errors."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=409, payload=payload)

def handle_error(error):
    """Handle different types of errors and return appropriate response."""
    if isinstance(error, APIError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    if isinstance(error, HTTPException):
        response = jsonify({
            'message': error.description,
            'status': 'error'
        })
        response.status_code = error.code
        return response
    
    # Handle unexpected errors
    response = jsonify({
        'message': 'An unexpected error occurred',
        'status': 'error',
        'error': str(error)
    })
    response.status_code = 500
    return response 