import articleProcessing
import random
from model.person import Person


def generatePersonOccupations(title, intro, article, nameOfPerson, temperature = 0.1, repeat_penalty = 1, top_p = 0.90, top_k = 80) -> list[str]:
    
    nameOfPerson
    
    
    multipleNamesSystemPromp = """
Du bist ein deutscher Text und Personen Analyse Assistent.
Deine Aufgabe ist es, alle Beschreibungen einer Person aus einem Text zu extrahieren.
Du erhältst den Namen einer Person.
Mit Hilfe des Textes listest du alle Beschreibungen die für diese Person im Text genannt werden.
Nenne die Beschreibung so genau wie möglich.
Beziehe dich ausschließlich auf Beschreibungen aus dem Text.

Berücksichtige dabei folgende Aspekte:
Berfuliche Positionen
Ämter
Familiäre Beziehungen
Rollen

"""

    multipleNamesMessage = f"""
Artikeltext:  
#BEGIN------------------#
Titel: {title}

Intro: {intro}

Text: {article}
#END------------------#


Wer ist {nameOfPerson}?

"""

    multipleNamesSchema = {
        "type": "object",
        "properties": {
            "beschreibungen": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["beschreibungen"]
    }

    result = articleProcessing.sendChatPrompt( systemprompt=multipleNamesSystemPromp,
                                                            userprompt=multipleNamesMessage,
                                                            temperature=temperature,
                                                            repeat_penalty=repeat_penalty,
                                                            top_p=top_p,
                                                            top_k=top_k,
                                                            responseType="json_object",
                                                            response_schema=multipleNamesSchema,
                                                            model="Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
                                                            promptDescription="MultipleNamesOrderPrompt");
    
    return result['beschreibungen']