import articleProcessing
import random
import fileLogger
logger = fileLogger.FileLogger(__name__)

topicRecogitionSchema = {
    "type": "object",
    "properties": {
        "themen": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "minItems": 1,
            "maxItems": 5,
            "uniqueItems": True
        },
        "required": ["themen"]
    }
}

def extractTopics(title, intro, article, model="Meta-Llama-3-8B-Instruct-V2.Q8_0.gguf", temperature = 0.2, repeat_penalty = 1, top_p = 0.95, top_k = 80):

    personRecognitionPrompt = """Du bist ein deutscher Text Assistent.
    Dir wird ein Artikel zum lesen übergeben.
    Der Artikel besteht aus Titel, Intro und Text. Diese werden mit "Titel:", "Intro:" und "Text:" eingeleitet.
    Deine Aufgabe ist es den gesamten Artikel zu lesen und dann bis zu 5 Themen aufzulisten, von denen der Text handelt.
    Die Themen sollen allgemein gehalten sein, um den Inhalt in Kategorien einsortieren zu können.
    Nenne nie mehr als 5 Themen. Versuche mindestens 1 Thema zu nennen.
"""

    personRecognitionMessage = f"""
Titel: {title}

Intro: {intro}

Text: {article}

Fragen:
Welches Thema oder Themen sind Inhalt des Artikels?

Antworte mit einem JSON. Nutze das Feld "themen" für die erkannten Themen.

    """

# Beachte, dass ein Nachname für mehrere Personen verwendet werden kann wenn verwandte Personen im Text vorkommen.

    
    resultPromptTopic = articleProcessing.sendChatPrompt(systemprompt=personRecognitionPrompt, userprompt=personRecognitionMessage, temperature=temperature, repeat_penalty=repeat_penalty, top_p=top_p, top_k=top_k, responseType="json_object", response_schema=topicRecogitionSchema, promptDescription="NameRecognitionPrompt", model=model);

    if resultPromptTopic == None or ('themen' not in resultPromptTopic):
        resultTopicList = list()
    elif 'themen' in resultPromptTopic:
        resultTopicList = list(resultPromptTopic.get('themen'))


    return resultTopicList


