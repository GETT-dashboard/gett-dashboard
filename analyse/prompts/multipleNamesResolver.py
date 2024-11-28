import articleProcessing
import random
from model.person import Person

import fileLogger
logger = fileLogger.FileLogger(__name__)

def solveMultiplePersonsWithOverlappingNames(title, intro, article, namesOfSamePerson, model, temperature = 0.1, repeat_penalty = 1, top_p = 0.90, top_k = 80) -> list[str]:
    
    namesOfSamePerson = namesOfSamePerson.copy()
    random.shuffle(namesOfSamePerson)
    
    logger.finfo("aftershuffle")
    logger.finfo(namesOfSamePerson)
    
    
    multipleNamesSystemPromp = """
Du bist ein deutscher Text und Personen Analyse Assistent.
Deine Aufgabe ist es, zu entscheiden, welche Namen eine Person in welcher Reihenfolge in seinem Leben getragen hat.
Du erhältst eine Liste von Namen die die gleiche Person bezeichnen.
Mit Hilfe eines Textes sortierst du die Liste der Namen dieser Person in die Reihenfolge, in der die Person die Namen in seinem Leben getragen hat.

Berücksichtige dabei Lebensabschnitte von der Geburt bis zum Tod.
Beispiele für Namensänderungen sind:

Hochzeit
Religiöse Konvertierungen
Ergreifung eines Künstlernamen
"""

    multipleNamesMessage = f"""
Artikeltext:  
#BEGIN------------------#
Titel: {title}

Intro: {intro}

Text: {article}
#END------------------#


Liste der Namen einer Person:
{namesOfSamePerson}

"""

    multipleNamesSchema = {
        "type": "object",
        "properties": {
            "order_of_names": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["order_of_names"]
    }

    result = articleProcessing.sendChatPrompt( systemprompt=multipleNamesSystemPromp,
                                                            userprompt=multipleNamesMessage,
                                                            temperature=temperature,
                                                            repeat_penalty=repeat_penalty,
                                                            top_p=top_p,
                                                            top_k=top_k,
                                                            responseType="json_object",
                                                            response_schema=multipleNamesSchema,
                                                            model=model,
                                                            promptDescription="MultipleNamesOrderPrompt");
    
    return result['order_of_names']