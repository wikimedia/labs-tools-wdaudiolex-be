import json

def get_lexeme_forms(json_string):
    """
    Processes a JSON string representing lexemes, extracts their forms, and organizes them based on the WikibaseLexeme data model.

    Args:
        json_string (str): A string containing JSON data for lexemes.

    Returns:
        dict: A dictionary where keys are lexeme IDs, and values contain form information including:
            - Form ID
            - Representations (text and language code)
            - Grammatical features
            - Associated statements
    """
    try:
        # Load the JSON string into a Python dictionary
        lexeme_data = json.loads(json_string)
        
        if not isinstance(lexeme_data, dict):
            raise ValueError("Invalid JSON format. Expected a dictionary.")
        
        lexeme_forms = {}
        
        for lex_id, lex_info in lexeme_data.items():
            forms = lex_info.get("forms", [])
            form_details = []
            
            for form in forms:
                form_id = form.get("id")  # LID-F# format
                representations = form.get("representations", {})  # Dictionary of {lang_code: text}
                grammatical_features = form.get("grammaticalFeatures", [])  # List of Wikidata item references
                statements = form.get("statements", {})  # Additional metadata
                
                form_details.append({
                    "form_id": form_id,
                    "representations": representations,
                    "grammatical_features": grammatical_features,
                    "statements": statements
                })
            
            lexeme_forms[lex_id] = form_details
        
        return lexeme_forms
    
    except json.JSONDecodeError:
        print("Error: Invalid JSON string.")
        return None
