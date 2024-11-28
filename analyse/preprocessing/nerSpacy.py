import spacy
import translate.translator as translator
from .personUtils import reduceFoundNames, replaceENSpellingWithGermanIfPresent

nlp_en = None
nlp = None

import fileLogger
logger = fileLogger.FileLogger(__name__)

def guessPersons(fullText):
    
    
    global nlp, nlp_en
    
    
    if nlp is None:
        nlp = spacy.load("de_core_news_lg")
    if nlp_en is None:
        nlp_en = spacy.load("en_core_web_trf")
    
    doc_en = nlp_en(translator.translate(fullText))
    doc = nlp(fullText)
    
    possiblePersonEntities = []
    possiblePersonEntities_en = []
    
    for ent in doc_en.ents:
        # print((ent.text, ent.label_))
        if ent.label_=='PERSON':
            possiblePersonEntities_en.append(ent.text)
    
    
    
    for ent in doc.ents:
        # print((ent.text, ent.label_))
        if ent.label_=='PER':
            possiblePersonEntities.append(ent.text)
            
    
    possiblePersonEntities = reduceFoundNames(possiblePersonEntities)
    possiblePersonEntities_en = reduceFoundNames(possiblePersonEntities_en)
    usedPossibleEntities = replaceENSpellingWithGermanIfPresent(possiblePersonEntities_en, possiblePersonEntities)
    
    return usedPossibleEntities


def splitIntoSentences(text):
    global nlp
    if nlp is None:
        initSpacyNLP()
        
    sentences = []
    partsSplit = text.split(" ; ")
    for part in partsSplit:
        doc = nlp(part)
        for i, sentence in enumerate(doc.sents):
            sentences.append(sentence.text)
        
    return sentences


def initSpacyNLP():
    global nlp, nlp_en
    nlp = spacy.load("de_core_news_lg")
    nlp_en = spacy.load("en_core_web_trf")