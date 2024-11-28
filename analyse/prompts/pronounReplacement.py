import articleProcessing
import random

def replacePronouns(annotatedText, listOfPersons, listOfPersonsWithSex, replacementCount, model, temperature = 0.1, repeat_penalty = 1, top_p = 0.90, top_k = 40):

    replacementSystemPrompt = """
You are a Text Analysis Assistant.
You will be given a text and a list of names to read.
Your task is to explain all pronouns, subjects, and objects in the text. The sections of text that need explanation are marked with "[=?x]".
For each value X, provide an explanation of who or what it refers to:

Use "VERB" for verbs.
Use "ORT" for locations.
Use "DING" for things.
Use "DINGE" for a group of things.
Use "GRUPPE" for groups.
Use "KEINE PERSON" for non-person entities, concepts, or ideas.
Use "ANONYME PERSON" for anonymous persons.
Use "PERSON" if it refers to a single person.
Multiple persons are indicated by the plural verb form in the sentence.
Save the explanation to ref_type.

Guidelines:
1. If the text is sein, it could also be the verb "sein". Mark it as a verb if the text is not used as a possesive pronoun.
2. For "Sie[=?x]" and "sie[=?x]", determine if it refers to one person, multiple persons, or things. Pay attention to the context to decide if it refers to a single female, a group, or a non-person entity. If it refers to one person, it must be female.
3. A person is rarely both the subject and object in the same sentence. If a pronoun is the subject or object, their name is likely not in the same sentence.
4. Pronouns can only refer to names mentioned earlier in the text unless the person is unknown or anonymous. If a person’s name appears for the first time at the end of a sentence, a prior pronoun in the same sentence does not refer to this person. Look for another person as the explanation for the pronoun.
5. Carefully consider verb forms and context to determine if a pronoun refers to a single person, a group, multiple things, or an entity. Check the surrounding sentences for additional clues about the subject or object.
6. Inside direct quotes, the speaker will mostly use the pronoun "ich" when referring to themselves. Therefore, "du," "er," or "sie" pronouns within direct quotes likely do not refer to the speaker.
7. Pronouns referring to non-person entities (things, groups, concepts) should be carefully assessed in context to ensure accurate identification.
8. For "GRUPPE" and "PERSON" try to specify which persons are referenced in "ref_persons". If no known person is reference leave "ref_persons" empty


Examples:
Example 1:

Text:
Peter Mustermann ist nicht zu unterschätzen. Er[=?1] und sein Bruder Thomas sind erfolgreiche Unternehmer.

Answer: 1 = PERSON (Peter Mustermann)

Example 2:

Text:
Maria Musterfrau spielt den besten Fußball und sie[=?2] ist außerdem eine begeisterte Tänzerin.

Answer: 2 = PERSON (Maria Musterfrau)

Example 3:

Text:
Max Müller wollte deshalb die gesamten Nudeln an den Handelsposten in Turin aufkaufen. So hätte er[=?25] ein Monopol – das würde ihm Unsummen einbringen. Er[=?26] schickte am 23. Januar seinen Freund Philipp aus Wien los. Es begann ein Wettlauf mit der Zeit, denn Philipp hatte nur wenig Vorsprung vor einem Mitbewerber mit demselben Auftrag. Am 1. Februar erreichte Philipp Turin. Er[=?27] war erschöpft.

Answer: 25 = PERSON (Max Müller), 26 = PERSON (Max Müller), 27 = PERSON (Philipp)

Explanation: 26 is also Max Müller because Philipp is already the object in this sentence, so he cannot be the subject as well. 27 refers to Philipp, as established in the preceding sentence.

Example 4:

Text:
Das neue Gesetz wurde verabschiedet, und es[=?3] soll die wirtschaftliche Lage verbessern.

Answer: 3 = KEINE PERSON

Explanation: 3 refers to "das neue Gesetz", which is a concept or idea, not a person.

Example 5:

Text:
Die Schüler gingen ins Museum. Sie[=?4] waren sehr interessiert an den Ausstellungen.

Answer: 4 = GRUPPE (unbekannte Personen)

Explanation: 4 refers to "die Schüler", which is a group of people.

Example 6:

Text:
Ein Fremder klopfte an die Tür. Er[=?5] wollte nach dem Weg fragen.

Answer: 5 = ANONYME PERSON

Explanation: 5 refers to "ein Fremder", who is an anonymous person.

Example 6:

Text:
Lisa und ihre Freunde kamen spät an. Sie[=?6] waren müde, aber glücklich.

Answer: 6 = GRUPPE (Lisa, unbekannte Personen)

Explanation: 6 refers to "Lisa und ihre Freunde", indicating multiple people.

Example 7:

Text:
Die Bücher standen auf dem Regal. Sie[=?7] waren alt und verstaubt.

Answer: 7 = DINGE

Explanation: 7 refers to "die Bücher", which are things.

Example 8:

Text:
"Ich bin sehr froh, dass du[=?8] gekommen bist," sagte Lisa.

Answer: 8 = ANONYME PERSON

Explanation: 8 refers to the person Lisa is speaking to, who is not herself.

Example 9:

Text:
"Ich habe sie[=?9] alle gestern gesehen," sagte Thomas.

Answer: 9 = GRUPPE (unbekannte Personen)

Explanation: 9 refers to a group of persons Thomas saw, which is not Thomas himself.

Example 10:

Text:
"Laura und Matthias heirateten im Sommer. Ihre Gäste waren entzückt. Danach begannen sie[=?10] ihre Reise durch Venezuela.

Answer: 10 = GRUPPE (= Laura und Matthias)

Explanation: 10 refers to a group of persons. They are Laura und Matthias


Example 11:
Text:
"Tanja und Robert waren bis nach Süd Afrika gekommen. Die Grenzer wollten dass sie[=?11] umkehren.

Answer: 11 = GRUPPE (= Tanja und Robert)

Explanation: 11 refers to a group of persons. They are  Tanja und Robert


Example 12:
Text:
"Max fragte sich: wie kann das sein[=?12]?.

Answer: 12 = VERB (= sein)

Explanation: 12 refers to the verb sein (=to be).

Example 13:
Text:
"Maria wusste wem sie[=?13] ihre[=?14] Fragen stellen musste.

Answer: 13 = PERSON (= Maria), 14 = PERSON (=Maria)

Explanation: 13 refers to Maria directly. 14 refers to possesiv Marias questions.




"""

    personEnum = []
    personEnum.append("VERB")
    personEnum.append("ORT")
    personEnum.append("DING")
    personEnum.append("GRUPPE")
    personEnum.append("KEINE PERSON")
    personEnum.append("ANONYME PERSON")
    personEnum.append("PERSON")
    random.shuffle(personEnum)
    
    listOfPersonsCopy = listOfPersons.copy()
    listOfPersonsCopy.append('unbekannt')
    random.shuffle(listOfPersonsCopy)
    
    replacementSchema = {
        "type": "object",
        "properties": {
            "referenzen": {
                "type": "object",
                "properties": {
                }
            }
        },
        "required": ["referenzen"]
    }
    allIndex = []
    for counter in range(1, replacementCount+1):
        allIndex.append(str(counter))
        replacementSchema['properties']['referenzen']['properties'][str(counter)] = {
            "type": "object",
            "properties": {
                "ref_type": {
                    "type": 'enum',
                    "enum": personEnum,
                },
                "ref_persons": {
                    "type": "array",
                    "items": {
                        "type": "enum",
                        "enum": listOfPersonsCopy
                    }
                },
            },
            "required": ["ref_type", "ref_persons"]
        }
    replacementSchema['properties']['referenzen']['required'] = allIndex
        
    # print("replacementSchema")
    # print(replacementSchema)

    textPrompt = f"""
Text:
{annotatedText}

Namen im Text:
{listOfPersonsWithSex}
"""

    resultReplacements = articleProcessing.sendChatPrompt(systemprompt=replacementSystemPrompt,
                                                            userprompt=textPrompt,
                                                            temperature=temperature,
                                                            repeat_penalty=repeat_penalty,
                                                            top_p=top_p,
                                                            top_k=top_k,
                                                            responseType="json_object",
                                                            response_schema=replacementSchema,
                                                            model=model,
                                                            promptDescription="PronounReferencePrompt");

    # print(resultReplacements)
    
    return resultReplacements