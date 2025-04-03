"""
Lexeme Utilities Module

This module provides functionality for searching and processing lexemes from Wikidata.
It includes functions for word sanitization and SPARQL-based lexeme search operations.
"""

import requests
from typing import List, Dict
import re
from urllib.parse import quote

def sanitize_word(word: str) -> str:
    """
    Sanitize the input word by removing punctuation and normalizing case.
    
    This function prepares words for consistent searching by:
    1. Removing all punctuation characters
    2. Converting to lowercase
    3. Stripping whitespace
    
    Args:
        word (str): The word to sanitize
        
    Returns:
        str: Sanitized word ready for searching
        
    Example:
        >>> sanitize_word("Hello·World!")
        'helloworld'
    """
    # Remove all non-word characters (except spaces) and convert to lowercase
    return re.sub(r'[^\w\s]', '', word).lower().strip()

def search_lexemes(word: str) -> List[Dict]:
    """
    Search for lexemes in Wikidata matching the given word.
    
    This function performs a SPARQL query to Wikidata to find lexemes that match
    the given word. The search is case-insensitive and ignores punctuation.
    
    The SPARQL query:
    1. Finds all LexicalEntry items
    2. Matches their written representation with the search word
    3. Retrieves language information
    4. Returns lexeme ID, lemma, and language label
    
    Args:
        word (str): The word to search for in Wikidata
        
    Returns:
        List[Dict]: List of dictionaries containing matching lexemes with properties:
            - id: The Wikidata lexeme ID (e.g., "L123")
            - lemma: The word form of the lexeme
            - language: The language name in English
            
    Example:
        >>> search_lexemes("hello")
        [{"id": "L123", "lemma": "hello", "language": "English"}]
        
    Note:
        Returns an empty list if the API request fails or no matches are found
    """
    # Sanitize the input word for consistent searching
    sanitized_word = sanitize_word(word)
    
    # SPARQL query to find lexemes with their properties
    sparql_query = """
    SELECT DISTINCT ?lexeme ?lemma ?language ?languageLabel WHERE {
      # Find all LexicalEntry items
      ?lexeme a ontolex:LexicalEntry ;
              dct:language ?language ;
              ontolex:lemma ?lemma .
      
      # Get the written representation
      ?lemma ontolex:writtenRep ?writtenRep .
      
      # Match the written representation (case-insensitive)
      FILTER(LCASE(?writtenRep) = LCASE(?search_word))
      
      # Get language labels in English
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
      ?language rdfs:label ?languageLabel .
    }
    """
    
    # Wikidata SPARQL endpoint
    url = "https://query.wikidata.org/sparql"
    
    # Prepare request parameters
    params = {
        "query": sparql_query,
        "format": "json",
        "search_word": sanitized_word
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process and format the results
        results = []
        for item in data.get("results", {}).get("bindings", []):
            # Extract lexeme ID from the full URI
            lexeme_id = item["lexeme"]["value"].split("/")[-1]
            
            # Create a structured result
            lexeme = {
                "id": lexeme_id,
                "lemma": item["lemma"]["value"],
                "language": item["languageLabel"]["value"]
            }
            results.append(lexeme)
            
        return results
        
    except requests.RequestException as e:
        # Log the error and return empty results
        print(f"Error searching lexemes: {str(e)}")
        return [] 