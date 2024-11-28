from utils import print_elapsed_time, getElapsedTime, extract_quoted_sentences
import time
from datetime import datetime
import json
import singleArticleAnalyzer
import struct
import sys
from typing import Union
import traceback

from os import listdir, mkdir
from os.path import isfile, join, basename, normpath

from model.person import Person

MAGIC_BYTE = b'\xaa'


models = ["gemma-2-9b-it-Q6_K.gguf"]
value_temperature = 0.1
value_repeat_penalty = 1
value_top_p = 0.90
value_top_k = 80

step = 5

repetitions = 10

indexReached = -1

evalPaths = ['/opt/ki/ki/evaluation-files/assisted-tagged/', '/opt/ki/ki/evaluation-files/assisted-tagged-v2-checked/', '/opt/ki/ki/evaluation-files/hand-tagged/']

specialIds = None
compareResult = False
if len(sys.argv) > 1:
    specialIds = sys.argv[1:]
    if 'compare' in specialIds:
        specialIds.remove('compare')
        compareResult = True
    
hand_tagged_files_with_jsons = []
for evalPath in evalPaths:
    hand_tagged_files_with_jsons = hand_tagged_files_with_jsons + [join(evalPath, f) for f in listdir(evalPath) if isfile(join(evalPath, f))]

print(hand_tagged_files_with_jsons)
print(specialIds)

if specialIds is not None and len(specialIds) >  0:
    usingPaths = []
    for path in hand_tagged_files_with_jsons:
        for specialId in specialIds:
            if path.endswith(specialId):
                usingPaths.append(path)
    hand_tagged_files_with_jsons = usingPaths

articles = []
evaluationSummaries = []
notExpectedKeys = ['indirectQuotes', 'birthday', 'alternativeNames', 'isMain']

for file in sorted(hand_tagged_files_with_jsons):
    if file.endswith('json') or file.endswith('csv_jina') or file.endswith('csv_fasttext'):
        continue
    articles.append(file)
    
print(articles)

def readFile(path) -> Union[tuple[int, bytes, bytes, bytes], None]:
    file = open(path, 'rb')
    articleIdBytes = file.read(8)
    if (len(articleIdBytes) == 0):
        return None
    articleId: int = struct.unpack(">Q", articleIdBytes)[0]

    titleSizeBytes = file.read(4)
    titleSize: int = struct.unpack(">I", titleSizeBytes)[0]
    title = file.read(titleSize)

    magicByte = file.read(1)
    if (magicByte != MAGIC_BYTE):
        return None

    summarySizeBytes = file.read(4)
    summarySize: int = struct.unpack(">I", summarySizeBytes)[0]
    summary = file.read(summarySize)

    magicByte = file.read(1)
    if (magicByte != MAGIC_BYTE):
        return None

    fileSizeBytes = file.read(8)
    fileSize: int = struct.unpack(">Q", fileSizeBytes)[0]
    text = file.read(fileSize)
    return articleId, title, summary, text


def addToCombinedStatistics(combineArticleInfo, combinedStatistics, evaluationSummary, articleId, elapsedTime):
    statistics = evaluationSummary['statistics']
    
    
    combineArticleInfo[articleId] = {}
    if len(evaluationSummary['persons']['missing_names']) > 0 or len(evaluationSummary['persons']['additional_names']) > 0  or len(evaluationSummary['persons']['case_missmatches']) > 0:
        combineArticleInfo[articleId] = {'names': {}}
        if len(evaluationSummary['persons']['missing_names']) > 0:
            combineArticleInfo[articleId]['names']['missing_names'] = evaluationSummary['persons']['missing_names']
        if len(evaluationSummary['persons']['additional_names']) > 0:
            combineArticleInfo[articleId]['names']['additional_names'] = evaluationSummary['persons']['additional_names']
        if len(evaluationSummary['persons']['case_missmatches']) > 0:
            combineArticleInfo[articleId]['names']['case_missmatches'] = evaluationSummary['persons']['case_missmatches']
    else:
        combineArticleInfo[articleId] = {
                "names" : "PERFECT"
        }
    
    for key in statistics:
        issueCount = 0
        if 'success' in statistics[key].keys():
            for innerKey in statistics[key].keys():
                combinedStatistics[key][innerKey] += statistics[key][innerKey]
            
        
            for innerKey in statistics[key].keys():
                if innerKey in list(['error', 'case_missmatches', 'missing', 'additional']) and statistics[key][innerKey] > 0:
                    issueCount += 1
                
        else:
            for secondKey in statistics[key]:
                for innerKey in statistics[key][secondKey].keys():
                    if innerKey in ['error', 'case_missmatches', 'missing', 'additional']:
                        issueCount += statistics[key][secondKey][innerKey]
                    combinedStatistics[key][secondKey][innerKey] += statistics[key][secondKey][innerKey]
        
        if issueCount == 0:
            combineArticleInfo[articleId][key] = "PERFECT"
        else:
            combineArticleInfo[articleId][key] = f"{statistics[key]}"
    
    allPerfect = True
    for articleKey in combineArticleInfo[articleId]:
        allPerfect = combineArticleInfo[articleId][articleKey] == "PERFECT"
        if not allPerfect:
            break
    
    if allPerfect:
        combineArticleInfo[articleId] = "PERFECT in " + elapsedTime 
    else:
        combineArticleInfo[articleId]['time'] = elapsedTime 
        
    
            
def printCurrentStatisticsValues(combineArticleInfo, combinedStatistics, fullSummaryFileHandle = None, articleSummaryFileHandle= None):
    # print(json.dumps(combineArticleInfo, sort_keys=True, indent=2, ensure_ascii=False))
    # print(json.dumps(combinedStatistics, sort_keys=True, indent=2, ensure_ascii=False))
    
    if fullSummaryFileHandle is not None:
        print(json.dumps(combinedStatistics, indent=2, sort_keys=True, ensure_ascii=False), file=fullSummaryFileHandle)
    if articleSummaryFileHandle is not None:
        print(json.dumps(combineArticleInfo, indent=2, sort_keys=True, ensure_ascii=False), file=articleSummaryFileHandle)
            

def addToEvaluationSummay(evaluationSummaryStatistics, differences, person: Person, fileHandle = None):
    
    if fileHandle is not None:
        print(person, file=fileHandle)
        print(json.dumps(differences, indent=2, sort_keys=True, ensure_ascii=False), file=fileHandle)
    # print(json.dumps(differences, indent=2, sort_keys=True, ensure_ascii=False))
    keys = [] if differences == False else differences.keys()
    for key in ['sex', 'age', 'inTitle', 'inIntro' ,'quotedInTitle', 'quotedInIntro',]:
        keyIsInDifferences = key in keys
        if not keyIsInDifferences:
            evaluationSummaryStatistics[key]['success'] += 1
        else:
            evaluationSummaryStatistics[key]['error'] += 1
    
    if 'occurences' in  keys:
        key = 'occurences'
        occurenceIssues = differences[key]
        occurenceIssuesKeys = occurenceIssues.keys()
        for occurence_key in evaluationSummaryStatistics[key]:
                evaluationSummaryStatistics[key][occurence_key]['success'] += (1 if occurence_key in occurenceIssuesKeys else 0)
                evaluationSummaryStatistics[key][occurence_key]['error'] += (1 if occurence_key not in occurenceIssuesKeys else 0)
    else:
        for occurence_key in evaluationSummaryStatistics['occurences']:
            evaluationSummaryStatistics['occurences'][occurence_key]['success'] += 1
    
    evaluateTextElementKey(evaluationSummaryStatistics, differences, person, keys, 'descriptiveTexts')
    evaluateTextElementKey(evaluationSummaryStatistics, differences, person, keys, 'directQuotes')
    evaluateTextElementKey(evaluationSummaryStatistics, differences, person, keys, 'occupations')
    
     
    # if 'occupations' in keys:
    #     key = 'occupations'
    #     occupationsIssues = differences[key]
    #     missingTextsCount = 0 if 'missingTextsCount' not in occupationsIssues.keys() else occupationsIssues['missingTextsCount']
    #     additionalTextsCount = 0 if 'additionalTextsCount' not in occupationsIssues.keys() else occupationsIssues['additionalTextsCount']
    #     evaluationSummaryStatistics[key]['additional'] += additionalTextsCount
    #     evaluationSummaryStatistics[key]['missing'] += missingTextsCount
    #     evaluationSummaryStatistics[key]['success'] += (len(person.occupations) - additionalTextsCount)
        
    # else:
    #     evaluationSummaryStatistics['occupations']['success'] += len(person.occupations)

def evaluateTextElementKey(evaluationSummaryStatistics, differences, person, keys, checkKey):
    
    
    personElements = person.occupations if checkKey == 'occupations' else person.descriptiveTexts if checkKey == 'descriptiveTexts' else person.directQuotes if checkKey == 'directQuotes' else []
        
    if checkKey in keys:
        
        
        key = checkKey
        textElementsIssues = differences[key]
        missingTextsCount = 0 if 'missingTextsCount' not in textElementsIssues.keys() else textElementsIssues['missingTextsCount']
        additionalTextsCount = 0 if 'additionalTextsCount' not in textElementsIssues.keys() else textElementsIssues['additionalTextsCount']
        evaluationSummaryStatistics[key]['additional'] += additionalTextsCount
        evaluationSummaryStatistics[key]['missing'] += missingTextsCount
        evaluationSummaryStatistics[key]['success'] += (len(personElements) - additionalTextsCount)
        
    else:
        evaluationSummaryStatistics[checkKey]['success'] += len(personElements)
                
def runForEachArtile(combineArticleInfo, combinedStatistics, runresultsPath, model,temperature,repeat_penalty,top_p,top_k):
    for articlepath in articles:
        
        print("Filepath")
        print(articlepath)
        try:
                # if skip>0:
            #     skip = skip-1
            #     continue

            
            articleUnion = readFile(articlepath)
            articleId = articleUnion[0]
            title = str(articleUnion[1], 'utf-8')
            intro = str(articleUnion[2], 'utf-8')
            text = str(articleUnion[3], 'utf-8')

            if compareResult:
                with open(articlepath + ".json") as f:
                    handTaggedResult = json.load(f)
                
            
            # articleProcessing.start_server('Meta-Llama-3-8B-Instruct-V2.Q8_0.gguf')
            timeAtStart = time.time()
            resultDataSet = singleArticleAnalyzer.processArticleWithParameters(title, intro, text,
                                                                    model=model,
                                                                    temperature = temperature,
                                                                    repeat_penalty = repeat_penalty,
                                                                    top_p = top_p,
                                                                    top_k = top_k)
            # print(resultDataSet)
            resultDataSetDic = {}
            for resultPerson in resultDataSet['persons']:
                resultDataSetDic[resultPerson['name']] = resultPerson
                

            # print("Analysed result")
            # print(json.dumps(resultDataSetDic, indent=2, sort_keys=True, ensure_ascii=False))
            
            if not compareResult:
                return
            
            lastPart = basename(normpath(articlepath))
            resultFile = runresultsPath + "/" +  lastPart
            with open(resultFile + ".txt", "+w") as resultFileHandle:
                
                print(json.dumps(resultDataSetDic, indent=2, sort_keys=True, ensure_ascii=False), file=resultFileHandle)

                expectedPersons = handTaggedResult['persons']
                expectedPersonsNames = []
                for expectedPerson in expectedPersons:
                    expectedPersonsNames.append(expectedPerson['name'])
                    
                evaluationSummary = {}
                evaluationSummary['statistics'] = {
                    # "isMain" : {
                    #     "success": 0,
                    #     "error": 0
                    # },
                    "age" : {
                        "success": 0,
                        "error": 0
                    },
                    "sex" : {
                        "success": 0,
                        "error": 0
                    },
                    "descriptiveTexts" : {
                        "success": 0,
                        "missing": 0,
                        "additional": 0
                    },
                    "directQuotes" : {
                        "success": 0,
                        "missing": 0,
                        "additional": 0
                    },
                    "quotedInTitle" : {
                        "success": 0,
                        "error": 0
                    },
                    "quotedInIntro" : {
                        "success": 0,
                        "error": 0
                    },
                    "inTitle" : {
                        "success": 0,
                        "error": 0
                    },
                    "inIntro" : {
                        "success": 0,
                        "error": 0
                    },
                    "occurences": {
                        "total" : {
                            "success": 0,
                            "error": 0
                        },
                        "firstNameOnly" : {
                            "success": 0,
                            "error": 0
                        },
                        "lastNameOnly" : {
                            "success": 0,
                            "error": 0
                        },
                        "fullName" : {
                            "success": 0,
                            "error": 0
                        }
                    },
                    "occupations": {
                        "success": 0,
                        "missing": 0,
                        "additional": 0,
                    },
                    "persons": {
                        "success": 0,
                        "missing": 0,
                        "additional": 0,
                        "case_missmatches": 0
                    }
                }
                evaluationSummary['persons'] = {}
                evaluationSummary['persons']['missing_names'] = []
                evaluationSummary['persons']['additional_names'] = []
                evaluationSummary['persons']['case_missmatches'] = []
                
                for foundPerson in resultDataSet['persons']:
                    if foundPerson['name'] not in expectedPersonsNames:
                        foundMissCased = False
                        foundNameUpper = foundPerson['name'].upper()
                        for expectedName in expectedPersonsNames:
                            expectedNameUPPER = expectedName.upper()
                            if foundNameUpper == expectedNameUPPER:
                                foundMissCased = True
                                break
                        if foundMissCased:
                            evaluationSummary['persons']['case_missmatches'].append(foundPerson['name'])
                        else:
                            evaluationSummary['persons']['additional_names'].append(foundPerson['name'])
                
                correctlyFoundCount = 0
                
                for person in expectedPersons:
                    
                    perfectPerson = Person.fromPerfectResult(person)
                    
                    # print("searching for " + person['name'])
                    analysisPerson = None
                    if person['name'] not in resultDataSetDic.keys():
                        searchNameUpper = person['name'].upper()
                        for resultPersonName in resultDataSetDic.keys():
                            if resultPersonName.upper() == searchNameUpper:
                                analysisPerson = resultDataSetDic[resultPersonName]
                                break
                        if analysisPerson is None:
                            evaluationSummary['persons']['missing_names'].append(person['name'])
                            continue
                    else:
                        analysisPerson = resultDataSetDic[person['name']]
                    
                    foundPerson = Person.fromPerfectResult(analysisPerson)  
                    
                    differences = perfectPerson.differencesOrFalse(foundPerson)
                    if differences == None:
                        print(f"DIFFERENCES CLASS ERROR")
                    elif differences == False:
                        print(f"NO DIFFERENCES for {foundPerson.name}")
                    
                    correctlyFoundCount +=1
                    print("found " + str(foundPerson))
                    
                    addToEvaluationSummay(evaluationSummary['statistics'],differences, foundPerson, resultFileHandle)
                
                evaluationSummary['statistics']['persons']['success'] = correctlyFoundCount
                evaluationSummary['statistics']['persons']['missing'] = len(expectedPersons) - correctlyFoundCount
                evaluationSummary['statistics']['persons']['additional'] = len(evaluationSummary['persons']['additional_names'])
                evaluationSummary['statistics']['persons']['case_missmatches'] = len(evaluationSummary['persons']['case_missmatches'])
                
                elapsedTime = getElapsedTime(timeAtStart)
                print_elapsed_time(timeAtStart)
                print("EVALUATION OF " + str(articleId))
                addToCombinedStatistics(combineArticleInfo, combinedStatistics, evaluationSummary, str(articlepath), elapsedTime)
        except Exception as e:
            # printing stack trace 
            traceback.print_exc() 
            
def evaluateParams(temperature, repeat_penalty,  top_p, top_k):
    
    runTime = datetime.now().strftime("%Y-%m-%d-%H:%M")
    runresultsPath = "run-results" + "/" + runTime
    mkdir(runresultsPath) 

    global indexReached, compareResult
    
    for model in models:
        
        combineArticleInfo = {
        }
        combinedStatistics = {
            
            # "isMain" : {
            #     "success": 0,
            #     "error": 0
            # },
            "age" : {
                "success": 0,
                "error": 0
            },
            "sex" : {
                "success": 0,
                "error": 0
            },
            "quotedInTitle" : {
                "success": 0,
                "error": 0
            },
            "quotedInIntro" : {
                "success": 0,
                "error": 0
            },
            "inTitle" : {
                "success": 0,
                "error": 0
            },
            "inIntro" : {
                "success": 0,
                "error": 0
            },
            "descriptiveTexts" : {
                "success": 0,
                "missing": 0,
                "additional": 0
            },
            "occurences": {
                "total" : {
                    "success": 0,
                    "error": 0
                },
                "firstNameOnly" : {
                    "success": 0,
                    "error": 0
                },
                "lastNameOnly" : {
                    "success": 0,
                    "error": 0
                },
                "fullName" : {
                    "success": 0,
                    "error": 0
                }
            },
            "occupations": {
                "success": 0,
                "missing": 0,
                "additional": 0,
            },
            "directQuotes": {
                "success": 0,
                "missing": 0,
                "additional": 0,
            },
            "persons": {
                "success": 0,
                "missing": 0,
                "additional": 0,
                "case_missmatches": 0
            }
        }
        
        print(f"evaluation running for model={model} temperature={temperature}, repeat_penalty={repeat_penalty}, top_p={top_p}, top_k={top_k}")
        globalTimeAtStart = time.time()
        

        runresultsModelPath = runresultsPath + "/" + model
        mkdir(runresultsModelPath) 
        runForEachArtile(combineArticleInfo, combinedStatistics, runresultsModelPath, model, temperature, repeat_penalty, top_p, top_k)
        
        articleSummaryFile = runresultsModelPath + "/article-summary.json"
        fullSummaryFile = runresultsModelPath + "/full-summary.json"
        with open(articleSummaryFile, "+w") as articleSummaryFileHandle:
            with open(fullSummaryFile, "+w") as fullSummaryFileHandle:
                printCurrentStatisticsValues(combineArticleInfo, combinedStatistics, fullSummaryFileHandle, articleSummaryFileHandle);
                print("Full duration:", file=fullSummaryFileHandle)
                print_elapsed_time(globalTimeAtStart, file=fullSummaryFileHandle)
        print("Full duration:")
        print_elapsed_time(globalTimeAtStart)

# try:
evaluateParams(value_temperature, value_repeat_penalty, value_top_p, value_top_k)
# except Exception as e:
#     print(e)    

# for evaluationSummary in evaluationSummaries:


exit()

        
