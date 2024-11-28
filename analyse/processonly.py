import prompts.humanVerifier
import prompts.namesRecognition
import prompts.personRecognition
# "Name of the person who said a quote":"Direct or indirect quote"

import json

def processArticle(article):
    try:
        
        # tokenCount = articleProcessing.approximateTokenCount(article)

        # if tokenCount > 4000:
        #     # print(f"tokenCount was greater than 4000; (value: {tokenCount}); skipping article for now")
        #     return json.dumps({})
        #     #   else:
        #     # print(f"tokenCount: {tokenCount}")

        # first step: generate list of possible persons in article
        resultNameSet = prompts.namesRecognition.extractNames(article)
        # second step: complete persond data from article
        jsonResultFormatted = {}
        if len(resultNameSet) > 0:
            resultPersonSet = prompts.personRecognition.completePerson(article, resultNameSet)


            for person in resultPersonSet:
            
                if 'persons' not in jsonResultFormatted.keys():
                    jsonResultFormatted['persons'] = []
                
                jsonResultFormatted['persons'].append(
                    {
                        'name': person['name'],
                        'sex': 'female' if person['geschlecht'] == 'Frau' else 'male' if person['geschlecht'] == 'Mann' else 'unknown',
                        'age': None if person['alter'] == 'unbekannt' else int(person['alter']),
                        'occupation': ';'.join(person['rollen'])
                    }
                )  if 'name' in person else None

        return json.dumps(jsonResultFormatted)
    
    except Exception as e:
        return json.dumps({"error": str(e)})