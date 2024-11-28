from testData import texts, expectedResults
import articleProcessing
import statistics
import sys
import json

modelIds = [ "Meta-Llama-3-8B-Instruct.Q8_0.gguf"]

manualSystemPrompt = "Du bist ein deutscher Text Assistent. Deine Aufgabe ist es den folgenden Text zu lesen und dann Fragen zu diesem Text zu beantworten. Antworte ausschließlich mit Textstellen und Zitaten aus dem Text."

prompts = [
    "Welche Namen von Personen werden im Text genannt? Nenne auch Namen von Interview Partnern!"
]

top_kValues = [20, 40, 80] #20, 50, 60, 70,90, 100
top_pValues = [0.8, 0.95, 0.97] #0.6, 0.7, 0.9, 0.97
min_pValues = [0.03, 0.05, 0.1] #0.07, 0.09, 0.11, 0.12
temperatureValues = [0, 0.1, 0.2]
repeatPenaltyValues = [ 0.9,1.1, 1.3]# 0.7, 0.8,1, 1.2, 

namesRecogitionSchemas = [
    {
        "schema": {
            "type": "object",
            "properties": {
                "namen": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "resultKey": "namen"
    }
]

class ModelTest:
    """An instance of a model test. Contains model name to load and range of params to test."""

    def __init__(self,
                 modelId,
                 systemPrompt, # systemprompt
                 userPromptWrapper, # lambda to wrap article and userprompt if needed
                 paramCombinations # list of combinations to test
                 ):
        self.modelId = modelId
        self.systemPrompt = systemPrompt
        self.userPromptWrapper = userPromptWrapper
        self.paramCombinations = paramCombinations
        
        self.results = []
        
    def description(self, combination):
        return f"Testing: {self.modelId} Prompt: {combination.prompt}"
        
    def runTests(self):
        for combination in self.paramCombinations:
            
            accuracies = []
            falsePositives = []
            
            for x, article in enumerate(texts):
            
                result = articleProcessing.sendChatPrompt(self.systemPrompt,
                                                self.userPromptWrapper(article, combination.prompt),
                                                combination.temperature,
                                                combination.repeatPenalty,
                                                combination.top_p,
                                                combination.min_p,
                                                combination.top_k,
                                                "json_object",
                                                combination.schemaStructure["schema"],
                                                self.description(combination),
                                                model=self.modelId)
                if result == 'ERROR':
                    accuracies.append(-1)
                    falsePositives.append(None)
                    print("failed to generate result")
                    continue

                    
                print(result)
                resultSet = set(result.get(combination.schemaStructure["resultKey"]))
                
                accuracies.append(round(len(expectedResults[x] & resultSet) / len(expectedResults[x]), 2))
                falsePositives.append(len(resultSet - expectedResults[x]))
                
                
            self.results.append({
                "combination": combination.description(),
                "meanAccuracy": statistics.fmean(accuracies),
                "accuracies": accuracies,
                "falsePositives": falsePositives
            })
        
        # self.results.sort(key = "meanAccuracy")

    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
        

class ArticleTest:
    """An sinlge test case to use in model tests. Contains the article text, and the ideal result."""

    def __init__(self,
                 text, # article text string
                 perfectNames):
        self.text = text
        self.perfectNames = perfectNames
    
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)

        
class ParamCombination:
    def __init__(self, prompt, temperature, repeatPenalty ,top_k, top_p, min_p, schemaStructure):
        self.prompt = prompt
        self.temperature = temperature
        self.repeatPenalty = repeatPenalty
        self.top_k = top_k
        self.top_p = top_p
        self.min_p = min_p
        self.schemaStructure = schemaStructure
    
    def description(self):
         return f"{self.prompt};{self.temperature};{self.repeatPenalty};{self.top_k};{self.top_p};{self.min_p};{self.schemaStructure['resultKey']};"
    
        
def generateCombinations():
    combinations = []
    for prompt in prompts:
        for topK in top_kValues:
        # for topP in top_pValues:
        #         for minP in min_pValues:
        #             for topK in top_kValues:
                        for temp in temperatureValues:
        #                     for repPen in repeatPenaltyValues:
                                for schemaStructure in namesRecogitionSchemas:
                                    combinations.append(ParamCombination(prompt=prompt, temperature = temp, repeatPenalty= 1.1, top_p = 0.95, min_p = 0.05, top_k = topK, schemaStructure=schemaStructure))
    return combinations

def generateTestModels(combinations):
    modelTests = []
    for modelId in modelIds:
        systemPromp = manualSystemPrompt
        userPromptWrapper = lambda article, prompt: f"Text: {article} \n\n {prompt}"
        
        modelTests.append(ModelTest(modelId=modelId, systemPrompt=systemPromp, userPromptWrapper=userPromptWrapper, paramCombinations=combinations))
            
    return modelTests


def main() -> int:
    combinations = generateCombinations()
    modelTests = generateTestModels(combinations=combinations)
    modelTestResults = []
    for modelTest in modelTests:
        modelTest.runTests()
        
        modelTestResults.append({
            "modelId": modelTest.modelId,
            "sortedResults": modelTest.results 
        })
    
    for results in modelTestResults:
        print(f"Results for Model Id: {results['modelId']}")
        for combinationResult in results["sortedResults"]:
            print(f"MeanAccuracy: {combinationResult['meanAccuracy']}; Accuracies: {combinationResult['accuracies']}; False Positives: {combinationResult['falsePositives']}, Combination: {combinationResult['combination']}")
    
    print(json.dumps(modelTestResults))
    #TODO save result as csv?

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
        
    