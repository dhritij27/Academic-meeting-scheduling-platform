"""
validators.py - Input Validation & Sanitization
Provides validation utilities for API inputs
"""

import re
from datetime import datetime, date

class ValidationError(Exception):
    """Custom validation error."""
    def __init__(self, field, message):
        self.field = field
        self.message = message
    
    def to_dict(self):
        return {'field': self.field, 'message': self.message}

class Validator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError('email', 'Invalid email format')
        return email.lower().strip()
    
    @staticmethod
    def validate_name(name, min_length=2, max_length=100):
        """Validate name."""
        if not name or not isinstance(name, str):
            raise ValidationError('name', 'Name must be a string')
        
        name = name.strip()
        if len(name) < min_length:
            raise ValidationError('name', f'Name must be at least {min_length} characters')
        if len(name) > max_length:
            raise ValidationError('name', f'Name must not exceed {max_length} characters')
        
        return name
    
    @staticmethod
    def validate_role(role):
        """Validate user role."""
        valid_roles = ['student', 'professor', 'admin']
        if role not in valid_roles:
            raise ValidationError('role', f'Role must be one of: {", ".join(valid_roles)}')
        return role
    
    @staticmethod
    def validate_date(date_str):
        """Validate date format (YYYY-MM-DD) and ensure it's not in the past."""
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError('meeting_date', 'Date must be in YYYY-MM-DD format')
        
        if parsed_date < date.today():
            raise ValidationError('meeting_date', 'Date cannot be in the past')
        
        return parsed_date
    
    @staticmethod
    def validate_time(time_str):
        """Validate time format (HH:MM)."""
        try:
            datetime.strptime(time_str, '%H:%M')
        except ValueError:
            raise ValidationError('time', 'Time must be in HH:MM format')
        return time_str
    
    @staticmethod
    def validate_title(title, min_length=3, max_length=200):
        """Validate meeting title."""
        if not title or not isinstance(title, str):
            raise ValidationError('title', 'Title must be a string')
        
        title = title.strip()
        if len(title) < min_length:
            raise ValidationError('title', f'Title must be at least {min_length} characters')
        if len(title) > max_length:
            raise ValidationError('title', f'Title must not exceed {max_length} characters')
        
        return title
    
    @staticmethod
    def validate_description(description, max_length=1000):
        """Validate meeting description."""
        if description is None:
            return ''
        
        if not isinstance(description, str):
            raise ValidationError('description', 'Description must be a string')
        
        description = description.strip()
        if len(description) > max_length:
            raise ValidationError('description', f'Description must not exceed {max_length} characters')
        
        return description
    
    @staticmethod
    def validate_positive_integer(value, field_name):
        """Validate positive integer."""
        try:
            int_value = int(value)
            if int_value <= 0:
                raise ValueError
            return int_value
        except (ValueError, TypeError):
            raise ValidationError(field_name, f'{field_name} must be a positive integer')
    
    @staticmethod
    def validate_response(response):
        """Validate meeting response status."""
        valid_responses = ['accepted', 'declined', 'pending']
        if response not in valid_responses:
            raise ValidationError('response', f'Response must be one of: {", ".join(valid_responses)}')
        return response
    
    @staticmethod
    def validate_list_of_integers(items, field_name):
        """Validate a list of integers."""
        if not isinstance(items, list):
            raise ValidationError(field_name, f'{field_name} must be a list')
        
        try:
            return [int(item) for item in items if item]
        except (ValueError, TypeError):
            raise ValidationError(field_name, f'{field_name} must contain only integers')

def validate_meeting_creation(data):
    """Validate meeting creation request."""
    errors = []
    
    try:
        data['title'] = Validator.validate_title(data.get('title'))
    except ValidationError as e:
        errors.append(e.to_dict())
    
    try:
        data['description'] = Validator.validate_description(data.get('description', ''))
    except ValidationError as e:
        errors.append(e.to_dict())
    
    try:
        data['meeting_date'] = Validator.validate_date(data.get('meeting_date'))
    except ValidationError as e:
        errors.append(e.to_dict())
    
    try:
        data['slot_id'] = Validator.validate_positive_integer(data.get('slot_id'), 'slot_id')
    except ValidationError as e:
        errors.append(e.to_dict())
    
    try:
        data['created_by'] = Validator.validate_positive_integer(data.get('created_by'), 'created_by')
    except ValidationError as e:
        errors.append(e.to_dict())
    
    if 'room_id' in data and data['room_id']:
        try:
            data['room_id'] = Validator.validate_positive_integer(data.get('room_id'), 'room_id')
        except ValidationError as e:
            errors.append(e.to_dict())
    
    if 'participants' in data and data['participants']:
        try:
            data['participants'] = Validator.validate_list_of_integers(data.get('participants', []), 'participants')
        except ValidationError as e:
            errors.append(e.to_dict())
    
    return errors

def validate_user_creation(data):
    """Validate user creation request."""
    errors = []
    
    try:
        data['email'] = Validator.validate_email(data.get('email'))
    except ValidationError as e:
        errors.append(e.to_dict())
    
    try:
        data['name'] = Validator.validate_name(data.get('name'))
    except ValidationError as e:
        errors.append(e.to_dict())
    
    if 'role' in data:
        try:
            data['role'] = Validator.validate_role(data.get('role'))
        except ValidationError as e:
            errors.append(e.to_dict())
    
    return errors

def validate_participant_response(data):
    """Validate participant response request."""
    errors = []
    
    try:
        data['user_id'] = Validator.validate_positive_integer(data.get('user_id'), 'user_id')
    except ValidationError as e:
        errors.append(e.to_dict())
    
    try:
        data['response'] = Validator.validate_response(data.get('response'))
    except ValidationError as e:
        errors.append(e.to_dict())
    
    return errors
