
from app.repositories import lexeme_repository

def match_lexemes(pattern, category):
    # Logic for matching lexemes with audio files based on the pattern
    matched_lexemes = lexeme_repository.get_lexemes_by_category(category)
    return [lexeme for lexeme in matched_lexemes if pattern in lexeme.name]

