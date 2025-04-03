import requests
from typing import Dict, List

def get_supported_languages() -> Dict[str, str]:
    """
    Fetches and converts language codes to their corresponding labels.
    
    Returns:
        Dict[str, str]: A dictionary mapping language codes to their labels
    """
    # Wikimedia supported languages API endpoint
    url = "https://commons.wikimedia.org/w/api.php"
    
    params = {
        "action": "query",
        "meta": "languageinfo",
        "liprop": "name|autonym",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        languages = {}
        if "query" in data and "languageinfo" in data["query"]:
            for code, info in data["query"]["languageinfo"].items():
                # Use autonym (native name) if available, otherwise use English name
                label = info.get("autonym") or info.get("name", code)
                languages[code] = label
                
        return languages
    except requests.RequestException as e:
        # Log the error and return an empty dict
        print(f"Error fetching language codes: {str(e)}")
        return {}

def get_language_label(code: str) -> str:
    """
    Gets the label for a specific language code.
    
    Args:
        code (str): The language code to look up
        
    Returns:
        str: The language label or the code itself if not found
    """
    languages = get_supported_languages()
    return languages.get(code, code) 