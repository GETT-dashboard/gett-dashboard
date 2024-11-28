import articleProcessing
import random

nameCategorizationSchema = {
    "type": "object",
    "properties": {
        "humanNames": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "otherWords": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}

def filterLeoHumanNames(setOfNames, inText, temperature = 0.1, repeat_penalty = 1, top_p = 0.9, top_k = 40):

    humanNameCheckPrompt = f""" Aus dem Quelltext sollen folgende Namen kategorisiert werden in Namen und andere Wörter. Andere Wörte sind Pronomen oder Gruppen von Menschen oder neutrale Begriffe.
Ein Name kann nur entweder ein Name oder ein anderes Wort sein. Echte Namen setzen sich oft auf aus Vor- und Nachname zusammen. 
Beachte das Familiennamen von mehreren Personen getragen werden können.
Kategorisiere immer alle übergebenen Namen!
Gebe immer die vollen Namen zurück.

Liste von Namen:
{setOfNames}
"""

    resultPromptPersons = articleProcessing.sendChatPrompt(articleProcessing.leoSystemPrompt(), articleProcessing.wrapInLeoPrompt(humanNameCheckPrompt, inText), temperature, repeat_penalty, top_p, top_k, "json_object", nameCategorizationSchema, "HumanNameFilterPrompt")
    
    print(resultPromptPersons)
    resultNameSet = set(resultPromptPersons.get('humanNames'))

    # print(resultNameSet)
    return resultNameSet

def filterHumanNames(setOfNames, inText, temperature = 0.1, repeat_penalty = 1, top_p = 0.9, top_k = 40):

    prefilterSetOfNames = []
    if len(setOfNames) < 1:
        return setOfNames
    for inputName in setOfNames:
        inputFound = False
        for namePart in inputName.split(' '):
            if namePart in str(inText):
                prefilterSetOfNames.append(inputName)
                inputFound = True
                break
            if inputFound:
                break


    humanNameCheckInstruction = "Du bist ein Bewerter von Namen für Menschen. Entscheide ob ein Mensch diesen Namen tragen kann oder nicht. Zur Bestimmung eines Namens wird zusätzliche der Text übergeben aus dem die Namen stammen sollen."
    humanNameCheckPrompt = f"""
Folgende Namen sollen kategorisiert werden in menschliche Eigenname und andere Wörter. Andere Wörte sind Pronomen oder Gruppen von Menschen oder neutrale Begriffe.
Ein Name kann nur entweder ein Name oder ein anderes Wort sein. Echte Namen setzen sich oft auf aus Vor- und Nachname zusammen. 
Beachte das Familiennamen von mehreren Personen getragen werden können.
Kategorisiere immer alle übergebenen Namen!
Gebe immer die vollen Namen zurück.

Liste von Namen:
{prefilterSetOfNames}

Quelltext:
{inText}
    """

    resultPromptPersons = articleProcessing.sendChatPrompt(humanNameCheckInstruction, humanNameCheckPrompt, temperature, repeat_penalty, top_p, top_k, "json_object", nameCategorizationSchema, "HumanNameFilterPrompt")
    return set(resultPromptPersons.get('humanNames'))