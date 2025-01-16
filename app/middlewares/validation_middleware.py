
from flask import request

def validate_request_data(required_fields):
    data = request.get_json()
    for field in required_fields:
        if field not in data:
            return {'error': f'Missing required field: {field}'}, 400
    return None

