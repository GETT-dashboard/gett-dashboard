import articleProcessing
import random
import fileLogger
logger = fileLogger.FileLogger(__name__)

namesRecogitionSchema = {
    "type": "object",
    "properties": {
        "namen": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "interviewPartners": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}

def extractNames(title, intro, article, temperature = 0.2, repeat_penalty = 1, top_p = 0.95, top_k = 80):

    personRecognitionPrompt = """Du bist ein deutscher Text Assistent.
    Dir wird ein Artikel zum lesen übergeben.
    Der Artikel besteht aus Titel, Intro und Text. Diese werden mit "Titel:", "Intro:" und "Text:" eingeleitet.
    Deine Aufgabe ist es den gesamten Artikel zu lesen und dann Fragen zu diesem Artikel zu beantworten.
    Antworte ausschließlich mit Textstellen und Zitaten aus dem Text.
"""

    personRecognitionMessage = f"""
Titel: {title}

Intro: {intro}

Text: {article}

Fragen:
Welche Namen von Personen werden im Text genannt?
Antworte nur mit Personen, die mindestens mit Vorname oder mit Nachname erwähnt werden. Zähle keine Personen auf die anonym sind.

Antworte mit einem JSON. Nutze das Feld "namen" für die Namen. Werden keine personen genannt setze eine leere Liste für "namen".

    """

# Beachte, dass ein Nachname für mehrere Personen verwendet werden kann wenn verwandte Personen im Text vorkommen.

    
    logger.finfo("extractNames before sendChatPrompt")
    resultPromptPersons = articleProcessing.sendChatPrompt(systemprompt=personRecognitionPrompt, userprompt=personRecognitionMessage, temperature=temperature, repeat_penalty=repeat_penalty, top_p=top_p, top_k=top_k, responseType="json_object", response_schema=namesRecogitionSchema, promptDescription="NameRecognitionPrompt", model="Meta-Llama-3-8B-Instruct-V2.Q8_0.gguf");

    logger.finfo("extractNames after sendChatPrompt")
    if resultPromptPersons == None or (('namen' not in resultPromptPersons) and ('interviewPartners' not in resultPromptPersons)):
        resultNameSet = set()
    elif 'namen' not in resultPromptPersons:
        resultNameSet = set(resultPromptPersons.get('interviewPartners'))
    elif 'interviewPartners' not in resultPromptPersons:
        resultNameSet = set(resultPromptPersons.get('namen'))
    else:
        resultNameSet = set(resultPromptPersons.get('namen')) | set(resultPromptPersons.get('interviewPartners'))


    return resultNameSet


