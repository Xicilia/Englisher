import random
from typing import TextIO

class WordManager:
    """
    Basic class that can save words into list and gave access to them.
    """
    def __init__(self):
        
        self._words = []
        
    def addWord(self, word: str) -> bool:
        """
        Adds word into list.
        
        :param word: adding word
        Returns: True if word was added, else False.
        """
        
        #avoid duplicates
        if self.inList(word): return False
        
        self._words.append(word)
        
    def inList(self, word: str) -> bool:
        
        """
        Checks that given word is in list.
        
        :param word: checking word.
        Returns: True if word in list, else False.
        """
        
        return word in self._words
    
    def getRandom(self) -> str:
        """
        Gives random word from list.
        """
        
        return random.choice(self._words)
    
    def setWordList(self, wordList: list[str]):
        """
        sets word list. 
        """
        
        self._words = wordList
        
    @staticmethod
    def _getFromReadable(file: TextIO):
        """
        Reads all words from given readable file and returns WordManager object from it.
        """
        
        words = []
        #avoid checking word existance 
        for line in file:
            words.append(line.replace("\n", ""))
            
        newManager = WordManager()
        newManager.setWordList(words)
        return newManager
        
        
def parseWordsFromTextFile(filename: str) -> WordManager:
    """
    Parses given file and returns WordManager with words from this file.
    """
    
    with open(filename, "r") as wordsFile:
        
        return WordManager._getFromReadable(wordsFile)