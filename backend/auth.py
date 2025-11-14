"""
auth.py - Authentication & Authorization
Handles JWT tokens and user authentication
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

class AuthError(Exception):
    """Custom authentication error."""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def generate_token(user_id, email, role, expires_in_hours=JWT_EXPIRATION_HOURS):
    """
    Generate a JWT token for a user.
    
    Args:
        user_id: Unique user identifier
        email: User email
        role: User role (student, professor, etc.)
        expires_in_hours: Token expiration time in hours
    
    Returns:
        JWT token string
    """
    try:
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        raise AuthError(f"Token generation failed: {str(e)}", 500)

def verify_token(token):
    """
    Verify a JWT token and return the payload.
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload dictionary
    
    Raises:
        AuthError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError('Token has expired', 401)
    except jwt.InvalidTokenError:
        raise AuthError('Invalid token', 401)
    except Exception as e:
        raise AuthError(f"Token verification failed: {str(e)}", 401)

def extract_token_from_header(request):
    """
    Extract JWT token from Authorization header.
    
    Expected format: Authorization: Bearer <token>
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise AuthError('Missing Authorization header', 401)
    
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise AuthError('Invalid Authorization header format', 401)
    
    return parts[1]

def token_required(f):
    """
    Decorator to require valid JWT token for protected routes.
    
    Usage:
        @app.route('/api/protected', methods=['GET'])
        @token_required
        def protected_route():
            current_user = request.current_user
            return jsonify({'user': current_user})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = extract_token_from_header(request)
            payload = verify_token(token)
            request.current_user = payload
        except AuthError as e:
            return jsonify({
                'status': 'error',
                'message': e.error
            }), e.status_code
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'Authentication failed'
            }), 500
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*roles):
    """
    Decorator to require specific roles for protected routes.
    
    Usage:
        @app.route('/api/admin', methods=['GET'])
        @token_required
        @role_required('admin')
        def admin_route():
            return jsonify({'message': 'Admin access'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({
                    'status': 'error',
                    'message': 'User not authenticated'
                }), 401
            
            user_role = request.current_user.get('role')
            
            if user_role not in roles:
                return jsonify({
                    'status': 'error',
                    'message': f'Insufficient permissions. Required roles: {", ".join(roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

def get_current_user():
    """Get the current authenticated user from request context."""
    return getattr(request, 'current_user', None)
