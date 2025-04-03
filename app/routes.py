from flask import Blueprint, render_template, current_app, jsonify, request
from app.utils.language_utils import get_supported_languages
from app.utils.lexeme_utils import search_lexemes

"""
Routes Module

This module defines the API routes for the WDAudioLEx application.
It handles both web page rendering and API endpoints for language and lexeme operations.
"""

# Create the main blueprint for all routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """
    Home page route handler.
    
    This route serves the main application page and provides debugging information
    about available templates. It's primarily used for development and testing purposes.
    
    Returns:
        Rendered HTML template with the following context:
            - title: The page title
        
    Note:
        The template listing is for development purposes and should be removed
        in production.
    """
    # Debug: List all available templates
    print(current_app.jinja_env.list_templates())

    # Render the main page
    return render_template('index.html', title="Welcome to WDAudioLEx")

@main_bp.route('/api/languages', methods=['GET'])
def get_languages():
    """
    Get all supported language codes and their labels.
    
    This endpoint fetches the list of all supported languages from Wikimedia Commons
    and returns them in a JSON format with language codes as keys and their labels as values.
    
    ---
    responses:
        200:
            description: Successfully retrieved language codes and labels
            content:
                application/json:
                    schema:
                        type: object
                        additionalProperties:
                            type: string
                        example:
                            en: "English"
                            fr: "Français"
                            de: "Deutsch"
    """
    languages = get_supported_languages()
    return jsonify(languages)


@main_bp.route('/api/search-lexemes', methods=['GET'])
def search_lexemes_route():
    """
    API endpoint for searching lexemes in Wikidata.
    
    This endpoint accepts a word parameter and returns matching lexemes from Wikidata.
    The search is case-insensitive and ignores punctuation.
    
    Query Parameters:
        word (str): The word to search for in Wikidata
        
    Returns:
        JSON response containing:
            - Success (200): Array of matching lexemes with properties:
                {
                    "id": "L123",
                    "lemma": "example",
                    "language": "English"
                }
            - Error (400): Error message if word parameter is missing:
                {
                    "error": "Word parameter is required"
                }
                
    Example:
        GET /api/search-lexemes?word=hello
        Response:
            [
                {
                    "id": "L123",
                    "lemma": "hello",
                    "language": "English"
                }
            ]
    """
    # Get the search word from query parameters
    word = request.args.get('word')
    
    # Validate input
    if not word:
        return jsonify({"error": "Word parameter is required"}), 400
        
    # Search for matching lexemes
    results = search_lexemes(word)
    return jsonify(results)
