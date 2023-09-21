"""
Gets word definitions from wordsapi.com
"""

from dataclasses import dataclass
from typing import Optional

import requests

@dataclass
class Definition:
    
    definition: str
    example: str

@dataclass
class WordMeaning:
    
    partOfSpeech: str
    defininions: list[Definition]
    
@dataclass
class Word:
    
    phonetic: str
    meanings: list[WordMeaning]
    phoneticAudioUrl: Optional[str]

def getDefinitions(word: str) -> Optional[Word]:
    """
    Performs call to words api and gets definitions for given word.
    
    Returns: list of WordsApiDefinition objects if request was successfull, else None.
    """
    answer = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    
    if answer.status_code != 200:
        return None
    
    answerJSON = answer.json()[0]
    #print(answerJSON)
    
    meanings = []
    for meaning in answerJSON["meanings"]:
        
        partOfSpeech = meaning['partOfSpeech']
        
        definitions = []
        for definition in meaning["definitions"]:
            
            definitions.append(
                Definition(
                    definition.get("definition", ""), 
                    definition.get("example", "")
                )
            )
            
        meanings.append(WordMeaning(partOfSpeech, definitions))
            
        
    phonetics = answerJSON.get("phonetics", False)
    
    phoneticUrl = ""
    
    if phonetics:
        
        for phonetic in phonetics:
            
            audio = phonetic.get("audio", "")
            
            if audio != "":
                
                phoneticUrl = audio
                break
        
    return Word(
        answerJSON.get("phonetic", "Нет транскрипции в базе данных"),
        meanings,
        phoneticUrl
    )