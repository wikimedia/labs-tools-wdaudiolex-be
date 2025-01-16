
from app.repositories import pronunciation_repository

def add_pronunciation(lexeme_id, pronunciation_url, variety=None):
    # Logic to add pronunciation to a lexeme
    pronunciation_repository.add_pronunciation(lexeme_id, pronunciation_url, variety)
    return {'message': 'Pronunciation added successfully.'}

