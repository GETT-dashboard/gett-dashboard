import stanza
from .personUtils import reduceFoundNames
import logging
logging.disable(logging.CRITICAL)

import fileLogger
logger = fileLogger.FileLogger(__name__)

nlp_stanza = None
# nlp_stanza_en = None

processors = "tokenize,ner,lemma,mwt,pos,depparse"


def guessPersons(fullText):
    global nlp_stanza, nlp_stanza_en,processors
    if nlp_stanza is None:
        initStanzaNlp()
    
    stanza_doc = nlp_stanza(fullText)

    possiblePersonEntities_stanza = []
    locationEntities_stanza = []
    organisationEntities_stanza = []
    # possiblePersonEntities_stanza_en = []

    for sent in stanza_doc.sentences:
         for ent in sent.ents:
            if ent.type == 'PER':
                possiblePersonEntities_stanza.append(ent.text)
            elif ent.type == 'LOC':
                locationEntities_stanza.append(ent.text)
            elif ent.type == 'ORG':
                organisationEntities_stanza.append(ent.text)
        
    possiblePersonEntities_stanza = reduceFoundNames(possiblePersonEntities_stanza)
    
    for locationEntity in locationEntities_stanza:
        if locationEntity in possiblePersonEntities_stanza:
            possiblePersonEntities_stanza.remove(locationEntity)
    
    for organizationEntity in organisationEntities_stanza:
        if organizationEntity in possiblePersonEntities_stanza:
            possiblePersonEntities_stanza.remove(organizationEntity)
    
    usedPossibleEntities = possiblePersonEntities_stanza
    
    logger.finfo(usedPossibleEntities)
    return usedPossibleEntities

def splitIntoSentences(text):
    global nlp_stanza
    if nlp_stanza is None:
        initStanzaNlp()
        
    sentences = []
    partsSplit = text.split(" ; ")
    for part in partsSplit:
        doc = nlp_stanza(part)
        for i, sentence in enumerate(doc.sentences):
            sentences.append(sentence.text)
        
    return sentences

def identifySubjectAndObjectInSentence(text):
    global nlp_stanza
    if nlp_stanza is None:
        initStanzaNlp()
    
    sentenceDoc = nlp_stanza(text)
    
    result = {
        "subjects": [],
        "objects": [],
        "verbs": []
    }
    
    for sentence in sentenceDoc.sentences:
        for word in sentence.words:
            if word.deprel == "nsubj":
                result['subjects'].append(word.text)
            if word.deprel == "obj":
                result['objects'].append(word.text)
            if word.deprel == "iobj":
                result['objects'].append(word.text)
            if word.upos == "VERB":
                result['verbs'].append(word.text)
    
    return result
    

def initStanzaNlp():
    global nlp_stanza
    stanza.download(lang='de', processors=processors, logging_level='FATAL')
    nlp_stanza = stanza.Pipeline(lang='de', processors=processors, logging_level='FATAL')

# logger.finfo(identifySubjectAndObjectInSentence("Lambrecht hat ihren Gästen viel zu erzählen."))
