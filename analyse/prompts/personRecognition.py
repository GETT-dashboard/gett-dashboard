import articleProcessing
import random
from model.person import Person 
import fileLogger
logger = fileLogger.FileLogger(__name__)

def completePerson(title, intro, article, persons, model, temperature = 0.1, repeat_penalty = 1, top_p = 0.90, top_k = 80) -> set[Person]: 
    
    
    if temperature is None:
        temperature = 0.1

    if repeat_penalty is None:
        repeat_penalty = 1
        
    if top_p is None:
        top_p = 0.90
        
    if top_k is None:
        top_k = 80
    
    logger.finfo(f"completePerson with temperature: {temperature}; repeat_penalty: {repeat_penalty}; top_p: {top_p}; top_k: {top_k}")

    personInfoString = ""
    
    for name in persons:
        personInfoString += "- "
        personInfoString += name
        personInfoString += "\n"
                
        
    
    logger.finfo("personInfoString: ")
    logger.finfo(personInfoString)


    personRecognitionPrompt = """
Du bist ein deutscher Text Analyse Assistent.
Deine Aufgabe ist es, spezifische Details über Personen, die in einem deutschen Textartikel erwähnt werden, zu extrahieren.
Der Text ist in drei Abschnitte gegliedert: Titel, Einleitung und Artikel.
Für jede aufgeführte Person gib die folgenden Details an, sofern sie in einem der Abschnitte erwähnt werden:

- Vorname
- Nachname
- Spitzname
- Akademischer Titel
- Adels- oder Rangtitel
- Biologisches Geschlecht
- Alter
- Alternative oder frühere Namen (falls zutreffend auch Künstlernamen)

Stelle sicher, dass die Ausgabe als JSON-Objekt mit der angegebenen Struktur formatiert ist. Wenn ein Detail im Artikel nicht erwähnt wird, verwende "unbekannt" für dieses Detail. Überprüfe, dass jede Person aus der bereitgestellten Liste entweder in der Ausgabe mit extrahierten Details enthalten ist oder als "nicht erwähnt" markiert wird.

### Format
```json
{
  "personen": [
    {
      "name": "Personenname",
      "details": {
        "vorname": "Extrahierter Vorname",
        "nachname": "Extrahierter Nachname",
        "spitzname": "Extrahierter Spitzname",
        "akademischer_titel": "Extrahierter Akademischer Titel",
        "adels_oder_rangtitel": "Extrahierter Adels- oder Rangtitel",
        "biologisches_geschlecht": "Extrahiertes Biologisches Geschlecht",
        "alter": "Extrahiertes Alter",
        "alternative_namen": ["Alternativer Name 1", "Alternativer Name 2"]
      }
    }
  ]
}
```

Anweisungen
1. Extrahiere die Details streng basierend auf den expliziten Erwähnungen im Text, ohne über das hinauszugehen, was direkt angegeben wird.
2. Überprüfe, dass jede Person aus der Liste entweder in der Ausgabe mit extrahierten Details enthalten ist oder als "nicht erwähnt" markiert wird.
3. Die Liste kann unvollständig sein. Ergänze zusätzliche Personen in der Ausgabe hinzu, falls diese in der Liste fehlen.
4. Normalisiere Namen, indem du Possessivformen, die auf "s" enden, entfernst. In diesem Fall wird in der Liste der Namen eine Auswahl zwischen zwei Versionen des Namens enthält. Wähle die korrekte Schreibweise des Namen der Person!
5. Wenn im Artikel alternative Namen für eine Person erwähnt werden, füge diese im Feld "alternative_namen" ein.
6. Das biologische Geschlecht sollte aus dem Text abgeleitet werden, wenn es explizit erwähnt wird oder direkt aus Titeln oder dem Kontext (z.B. "Herr", "Frau") abgeleitet werden kann.
7. Das Alter einer Person sollte aus dem Text abgeleitet werden, wenn es explizit erwähnt wird.
8. Achte darauf das Jahreszahlen kein Hinweis auf das Alter sind!


Beispiel 1
Artikeltext:

#BEGIN------------------#
Titel: Berühmte Persönlichkeiten im Fokus
Einleitung: Dr. Hans Müller und seine Kollegin Anna Schmidt haben bahnbrechende Entdeckungen gemacht.
Artikel: Dr. Hans Müller, ein renommierter Wissenschaftler, ist 45 Jahre alt. Er ist in seinen engen Kreisen auch als Hansy bekannt. Anna Schmidt, seine Kollegin, arbeitet seit Jahren mit ihm zusammen. Graf von Friedrich, berühmt für seine Werke, wurde ebenfalls erwähnt. Peter Schmids Forschungsergebnisse haben international Anerkennung gefunden. Hans Müller, der früher als Hans Meyer bekannt war, wurde auch erwähnt. Maria Magdalena Mustermann und Michael wurden als Berater der Forschungsarbeit im Grußwort erwähnt.
#END------------------#

Liste der Personen:

- Hans Müller
- Anna Schmidt
- Graf von Friedrich
- Peter Schmid
- Hans Meyer
- Maria Magdalena Mustermann
- Peter Lustig

Beispiel Ausgabe

{
  "personen": [
    {
      "name": "Hans Müller",
      "details": {
        "nicht_erwähnt": false,
        "vorname": "Hans",
        "nachname": "Müller",
        "spitzname": "Hansy",
        "akademischer_titel": "Dr.",
        "adels_oder_rangtitel": "unbekannt",
        "biologisches_geschlecht": "männlich",
        "alter": 45,
        "alternative_namen": ["Hans Meyer"]
      }
    },
    {
      "name": "Anna Schmidt",
      "details": {
        "nicht_erwähnt": false,
        "vorname": "Anna",
        "nachname": "Schmidt",
        "spitzname": "unbekannt",
        "akademischer_titel": "unbekannt",
        "adels_oder_rangtitel": "unbekannt",
        "biologisches_geschlecht": "weiblich",
        "alter": "unbekannt",
        "alternative_namen": []
      }
    },
    {
      "name": "Graf von Friedrich",
      "details": {
        "nicht_erwähnt": false,
        "vorname": "unbekannt",
        "nachname": "von Friedrich",
        "spitzname": "unbekannt",
        "akademischer_titel": "unbekannt",
        "adels_oder_rangtitel": "Graf",
        "biologisches_geschlecht": "männlich",
        "alter": "unbekannt",
        "alternative_namen": []
      }
    },
    {
      "name": "Peter Schmid",
      "details": {
        "nicht_erwähnt": false,
        "vorname": "Peter",
        "nachname": "Schmid",
        "spitzname": "unbekannt",
        "akademischer_titel": "unbekannt",
        "adels_oder_rangtitel": "unbekannt",
        "biologisches_geschlecht": "männlich",
        "alter": "unbekannt",
        "alternative_namen": []
      }
    },
    {
      "name": "Maria Magdalena Mustermann",
      "details": {
        "nicht_erwähnt": false,
        "vorname": "Maria Magdalena",
        "nachname": "Mustermann",
        "spitzname": "unbekannt",
        "akademischer_titel": "unbekannt",
        "adels_oder_rangtitel": "unbekannt",
        "biologisches_geschlecht": "weiblich",
        "alter": "unbekannt",
        "alternative_namen": []
      }
    },
    {
      "name": "Peter Lustig",
      "details": {
        "nicht_erwähnt": true,
        "vorname": "Peter",
        "nachname": "Lustig",
        "spitzname": "unbekannt",
        "akademischer_titel": "unbekannt",
        "adels_oder_rangtitel": "unbekannt",
        "biologisches_geschlecht": "männlich",
        "alter": "unbekannt",
        "alternative_namen": []
      }
    },
    {
      "name": "Michael",
      "details": {
        "nicht_erwähnt": false,
        "vorname": "Michael",
        "nachname": "unbekannt",
        "spitzname": "unbekannt",
        "akademischer_titel": "unbekannt",
        "adels_oder_rangtitel": "unbekannt",
        "biologisches_geschlecht": "männlich",
        "alter": "unbekannt",
        "alternative_namen": []
      }
    }
  ]
}


Beispiel 2
Artikeltext:

#BEGIN------------------#
Titel: Erstes Buch direkt ein Hit
Einleitung: "Graue Fronten" setzen sich direkt an die Spitzer der Bestsellerlisten.
Artikel: Manchmal schaffen es bestimmte Texte direkt Massen zu faszinieren. Marik Hogils Neuerscheinung "Graue Fronten" ist ein solches Buch. Mit spielerischen Elementen über die Erfahrungen seines Lebens begeistern Jung und Alt.
#END------------------#

Liste der Personen:

- Marik Hogils

Gewünschte Ausgabe

{
  "personen": [
    {
      "name": "Marik Hogil",
      "details": {
        "nicht_erwähnt": false,
        "vorname": "Marik",
        "nachname": "Hogil",
        "spitzname": "ubekannt",
        "akademischer_titel": "unbekannt",
        "adels_oder_rangtitel": "unbekannt",
        "biologisches_geschlecht": "männlich",
        "alter": -1,
        "alternative_namen": []
      }
    }
  ]
}

"""


# Instructions:
# 1. Verify that no person from list of persons is missing in the output.
# 2. Extract details strictly based on explicit mentions in the text, ensuring no inference beyond what is directly stated.
# 3. Ensure the output contains only the information present in the provided article text. Do not infer any details not explicitly mentioned in the text.
# 4. Double-check that each person from the list is either included in the output with extracted details or confirmed as not mentioned in the article.
# 5. Normalize names by removing possessive forms ending in "s".
# 6. If the article mentions former names for a person, include these in the "former_names" field.
# 7. The biological sex should be inferred from the text if it is explicitly mentioned or can be inferred directly from titles or context (e.g., "Herr", "Frau").

    personRecognitionMessage = f"""

Artikeltext:  
#BEGIN------------------#
Titel: {title}

Intro: {intro}

Text: {article}
#END------------------#


Liste der Personen:
{personInfoString}


"""

    agesAsStrings = list(range(0, 130))
    agesAsStrings = list(map(str, agesAsStrings))
    agesAsStrings.insert(0, "unbekannt")
    random.shuffle(agesAsStrings)

    sexesAsStrings = ["weiblich", "männlich", "unbekannt"]
    nobleTitles = ["Kaiser","Kaiserin", "König", "Königin",
                   "Erzherzog", "Erzherzogin", "Großherzog", "Großherzogin",
                   "Herzog","Herzogin", "Großfürst","Großfürstin",
                   "Kurfürst","Kurfürstin", "Fürst", "Fürstin",
                   "Souverän Baron", "Souverän Baroness",
                   "Markgraf", "Markgräfin", "Graf", "Gräfin",
                   "Pfalzgraf", "Pfalzgräfin", "Reichsgraf", "Reichsgräfin",
                   "Altgraf", "Altgräfin", "Burggraf", "Burggräfin",
                   "Landgraf", "Landgräfin", "Raugraf", "Raugräfin",
                   "Rheingraf", "Rheingräfin", "Waldgraf", "Waldgräfin",
                   "Wildgraf", "Wildgräfin", "Freiherr", "Baron",
                   "Freifrau", "Baronin", "Freiin", "Baronesse" , "Ritter",
                   "Edler", "Edle", "Herr von", "Junker", "Frau von", "Fräulein von",
                   "unbekannt"]
    
    academicDegrees = ["Professor", "Doktor", "Professorin", "Doktorin", "unbekannt"]
    random.shuffle(sexesAsStrings)
    random.shuffle(academicDegrees)
    random.shuffle(nobleTitles)
    personRecogitionSchema = {
        "type": "object",
        "properties": {
            "persons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "title": "Person",
                    "description": "Eine mit Namen genannte Person im Text",
                    "properties": {
                        "name": {
                            "type": "string",
                        },
                        "details": {
                            "type": "object",
                            "properties":{
                                "nicht_erwähnt": {
                                    "type": "boolean",
                                    "title": "Aussage ob die Person im Text vorkommt oder nicht",
                                },
                                "adels_oder_rangtitel": {
                                    "type": "enum",
                                    "title": "Adelstitel der Person",
                                    "description": "Der Adelstitel Person im Text",
                                    "enum": nobleTitles
                                },
                                "akademischer_titel": {
                                    "type": "enum",
                                    "title": "Akademische Titel der Person",
                                    "description": "Der Akademische Titel im Text",
                                    "enum": academicDegrees
                                },
                                "nachname": {
                                    "type": "string",
                                    "title": "Nachname der Person",
                                    "description": "Der Nachname Person im Text",
                                },
                                "vorname": {
                                    "type": "string",
                                    "title": "Vorname der Person",
                                    "description": "Der Vorname Person im Text",
                                },
                                "spitzname": {
                                    "type": "string",
                                    "title": "Spitzname der Person",
                                    "description": "Der Spitzname Person im Text",
                                },
                                "alternative_namen": {
                                    "type": "array",
                                    "title": "Frühere Namen der Person",
                                    "items": {
                                      "type": "string"
                                    }
                                },
                                "biologisches_geschlecht": {
                                    "type": "string",
                                    "title": "Geschlecht der Person",
                                    "description": "Das Geschlecht der Person im Text",
                                    "enum": sexesAsStrings,
                                    "required": 1
                                },
                                "alter": {
                                    "type": "string",
                                    "title": "Alter der Person",
                                    "description": "Das Alter der Pesron im Text oder 'unbekannt'",
                                    "enum": agesAsStrings,
                                    "required": 1
                                },
                            },
                            "required": ["adels_oder_rangtitel", "akademischer_titel", "vorname", "nachname", "spitzname", "alter", "biologisches_geschlecht", "nicht_erwähnt"]
                        }
                    },
                    "required": ["name", "details"]
                }
            }
        },
        "required": ["persons"]
    }
    resultPromptPersons = articleProcessing.sendChatPrompt( systemprompt=personRecognitionPrompt,
                                                            userprompt=personRecognitionMessage,
                                                            temperature=temperature,
                                                            repeat_penalty=repeat_penalty,
                                                            top_p=top_p,
                                                            top_k=top_k,
                                                            responseType="json_object",
                                                            response_schema=personRecogitionSchema,
                                                            model=model,
                                                            promptDescription="PersonRecognitionPrompt");

    resultPersonSet = resultPromptPersons.get("persons")

    resultPersons = set()
    
    for resultpersonJson in resultPersonSet:
        if resultpersonJson['details']['nicht_erwähnt'] == False:
          resultPersons.add(Person.fromLLMResult(resultpersonJson))
    
    return resultPersons