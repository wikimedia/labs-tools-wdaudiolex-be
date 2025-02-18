
from app.errors.custom_errors import NotFoundError

def handle_error(error):
    if isinstance(error, NotFoundError):
        return {'error': str(error)}, 404
    return {'error': 'Internal Server Error'}, 500

