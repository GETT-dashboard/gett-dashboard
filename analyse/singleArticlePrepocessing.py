import preprocessing.nerStanza
# import preprocessing.nerSpacy
import preprocessing.manualOperations
from preprocessing.coreference import annotatedTextWithMarkers
from preprocessing.manualOperations import TEXT_PART_SEPERATOR
import re
import fileLogger
logger = fileLogger.FileLogger(__name__)

from model.person import Person

re_brackets = re.compile(r'(\[.*?\])')

def personentitiesRelatedToText(text, personEntities):
    relatedPersonEntities = []
    for person in personEntities:
        personParts = person.split(" ")
        if text in personParts:
            relatedPersonEntities.append(person)
    
    return relatedPersonEntities

# typeofNER can be one of "stanza", "spacy"
def analyzeArticle(title, intro, text, typeOfNER = 'stanza'):

    fullText = title + TEXT_PART_SEPERATOR + intro + TEXT_PART_SEPERATOR + text
    
    usedPossibleEntities = []
    if typeOfNER == 'stanza':
        usedPossibleEntities = preprocessing.nerStanza.guessPersons(fullText)
    # if typeOfNER == 'spacy':
    #     usedPossibleEntities = preprocessing.nerSpacy.guessPersons(fullText)
    
    annotatedTextResult = annotatedTextWithMarkers(fullText)
    
    return {
        "persons": usedPossibleEntities,
        "annotatedText": annotatedTextResult
    }

def assignDescribingSentences(text, persons: list[Person], isInterview: False):
    sentences = preprocessing.manualOperations.splitIntoSentences(text, isInterview)
    
    logger.finfo(sentences)
    
    sentencesPerPerson = dict()
    regexPerPerson = dict()
    
    
    collectedLastnames = []
    collectedFirstnames = []
    for person in persons:
        if person.lastname != None:
            collectedLastnames.append(person.lastname)
        if person.firstname != None:
            collectedFirstnames.append(person.firstname)
    
    for person in persons:
        sentencesPerPerson[person.name] = []
        if collectedLastnames.count(person.lastname) > 1:
            regexPerPerson[person.name] = re.compile('\\b('+ person.name +'s?)\\b')
        else:
            if person.isLastNameKnown() and person.isFirstNameKnown() != None:
                regexPerPerson[person.name] = re.compile('\\b('+ person.name +'s?|'+ person.lastname +'s?|'+ person.firstname +'s?)\\b')
            elif person.isLastNameKnown():
                regexPerPerson[person.name] = re.compile('\\b('+ person.name +'s?|'+ person.lastname +'s?)\\b')
            elif person.isFirstNameKnown():
                regexPerPerson[person.name] = re.compile('\\b('+ person.name +'s?|'+ person.firstname +'s?)\\b')
            elif person.isNickmameKnown():
                regexPerPerson[person.name] = re.compile('\\b(' + person.name + 's?|'+ person.nickname + 's?)\\b')
            else:
                regexPerPerson[person.name] = re.compile('\\b(' + person.name + 's?)\\b')
                
                
        # sentencesPerPerson[person] = []
        # regexPerPerson[person] = re.compile(r'(\[' + person +  '\]|'+ person +')')
    
    
    for person in persons:
        regex = regexPerPerson[person.name]
        logger.finfo(regex)
        for sentence in sentences:
            if regex.findall(sentence):
                sentencesPerPerson[person.name].append(re_brackets.sub(lambda a : "", sentence))
    
    return sentencesPerPerson
    
    
# text = "Damit hielt er[Hildebrand Veckinchusen] die Fassade des Erfolgs eine Weile aufrecht: 1418 kaufte er[Hildebrand Veckinchusen] sich in der Lübecker Königsstraße – eine der besten Adressen der Stadt – ein repräsentatives Haus."
# testRegex = re.compile('\[' + "Hildebrand Veckinchusen" +  '\]')
# logger.finfo(testRegex.findall(text))