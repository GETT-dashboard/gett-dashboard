import prompts.personRecognition
import prompts.pronounReplacement
import prompts.multipleNamesResolver
import prompts.occupationRecognition
import quotes.direct_quotes
import fileLogger
import re
import singleArticlePrepocessing
import prompts.topicRecognition

from model.person import Occurence, Person


logger = fileLogger.FileLogger(__name__)

def countMatchingInText(regex, text):
    if regex is None:
        return 0
    match = regex.findall(text)
    if match:
        return len(match)
    return 0

def processArticleWithParameters(title, intro, article, model=None, temperature = None, repeat_penalty = None, top_p = None, top_k = None):
    
    # first step: generate list of possible persons in article
    logger.finfo("processArticle method before extractNames")
    
    preprocessingInfo = singleArticlePrepocessing.analyzeArticle(title, intro, article)
    
    # second step: complete persond data from article
    jsonResultFormatted = {}
    jsonResultFormatted['persons'] = []
    
    justNames = []
    resultPersonSet = set()
    if len(preprocessingInfo["persons"]) > 0:
        # set of Person objects
        resultPersonSet = prompts.personRecognition.completePerson(title, intro, article, preprocessingInfo["persons"], model = model, temperature = temperature, repeat_penalty = repeat_penalty, top_p = top_p, top_k = top_k)

        logger.finfo("raw result: ")
        logger.finfo(resultPersonSet)
        
        fulltext = title + " " + intro + " " + article
        
        lastNames = [person.lastname for person in resultPersonSet if 'unbekannt' != person.lastname]
        namesWithSameLastnames: dict[str: list[Person]] = dict()
        personsWithFormerNames: set[list[Person]] = set()
        
        for person in resultPersonSet:
            
            justNames.append(person.name)
            
            regexFirstnameOnly = person.firstnameRegex()
            regexLastnameOnly = person.lastnameRegex()
            regexFullname = person.fullnameRegex()
            regexNickname = person.nicknameRegex()
            
            isLastnamePresentAtLeastTwice = lastNames.count(person.lastname) > 1
            
            #if the lastname is used twice, we only count the fullname in title and intro
            partialNameCountInTitle = 0 if isLastnamePresentAtLeastTwice else ((0 if not person.isFirstNameKnown() else countMatchingInText(regexFirstnameOnly, title)) +
                                            (0 if not person.isLastNameKnown() else countMatchingInText(regexLastnameOnly, title)))
            
            partialNameCountInIntro = 0 if isLastnamePresentAtLeastTwice else ((0 if not person.isFirstNameKnown() else countMatchingInText(regexFirstnameOnly, intro)) +
                                            (0 if not person.isLastNameKnown() else countMatchingInText(regexLastnameOnly, intro)))
            
            inTitle = True if (partialNameCountInTitle + (0 if not person.isNickmameKnown() else countMatchingInText(regexNickname, title))
                                                + countMatchingInText(regexFullname, title) > 0) else False
            inIntro = True if (partialNameCountInIntro + (0 if not person.isNickmameKnown() else countMatchingInText(regexNickname, intro))
                                                + countMatchingInText(regexFullname, intro) > 0) else False
            
            
            if isLastnamePresentAtLeastTwice:
                namesWithSameLastnames[person.lastname] = [person] if person.lastname not in namesWithSameLastnames.keys() else (namesWithSameLastnames[person.lastname] + [person])
            
            if len(person.alternative_names) > 0:
                personsWithFormerNames.add(person)
            
            firstNameOnlyCount = 0 if regexFirstnameOnly is None else countMatchingInText(regexFirstnameOnly, fulltext)
            lastNameOnlyCount = 0 if regexLastnameOnly is None else countMatchingInText(regexLastnameOnly, fulltext)
            fullNameCount= 0 if regexFullname is None else countMatchingInText(regexFullname, fulltext)
            nicknameCount= 0 if regexNickname is None else countMatchingInText(regexNickname, fulltext)
            
            person.setOccurence(Occurence(firstNameOnlyCount, lastNameOnlyCount, fullNameCount, nicknameCount, inTitle, inIntro))
            
    
    if len(resultPersonSet) > 0:
        # : {
        #         isInterview: isInterview,
        #         result: result
        #     }  
        directQuoteResultObject = quotes.direct_quotes.send_direct_quotes_request_v2(title=title, summary=intro, text=article, names=justNames, model=model)
        directQuoteResult = directQuoteResultObject['result']
        isInterview = directQuoteResultObject['isInterview']
        
        directQuoteResultsMap = dict()
        for directQuoteResult in directQuoteResult:
            directQuoteResultsMap[directQuoteResult['name']] = directQuoteResult
        
        
        for person in resultPersonSet:
            if person.name in directQuoteResultsMap.keys():
                directQuoteResult = directQuoteResultsMap[person.name]
                person.updateWithDirectQuotesResults(directQuoteResult['directQuotes'], directQuoteResult['quotedInTitle'], directQuoteResult['quotedInIntro'])
        
        # logger.finfo(directQuoteResult)             
        
        personsWithSex = []
        personNamesOnly = []
        for person in resultPersonSet:
            personsWithSex.append(person.name + " - " + person.sex)
            personNamesOnly.append(person.name)
        
        # logger.finfo(preprocessingInfo['annotatedText'])
        # return
        
        replacementResult = prompts.pronounReplacement.replacePronouns(preprocessingInfo['annotatedText']['text'], personNamesOnly, personsWithSex, preprocessingInfo['annotatedText']['counter'], model = model)
        
        # logger.finfo(replacementResult)
        
        replacedText = preprocessingInfo['annotatedText']['text']
        for referenceIndex in range(preprocessingInfo['annotatedText']['counter'], 0, -1):
            # logger.finfo(str(referenceIndex) + "=" + replacementResult['referenzen'][str(referenceIndex)])
            # logger.finfo(replacementResult['referenzen'][str(referenceIndex)]['ref_type'])
            # logger.finfo(replacementResult['referenzen'][str(referenceIndex)]['ref_persons'])
            replacementText = ""
            if len(replacementResult['referenzen'][str(referenceIndex)]['ref_persons']) > 1:
                replacementText = ";".join(replacementResult['referenzen'][str(referenceIndex)]['ref_persons'])
            if len(replacementResult['referenzen'][str(referenceIndex)]['ref_persons']) == 1:
                replacementText = replacementResult['referenzen'][str(referenceIndex)]['ref_persons'][0]
            replacedText = replacedText.replace("=?"+str(referenceIndex), replacementText)
            
        # logger.finfo(replacedText)
            
        splitIntoSentences = singleArticlePrepocessing.assignDescribingSentences(replacedText, resultPersonSet, isInterview)
        # logger.finfo(splitIntoSentences)
        for person in resultPersonSet:
            
            # logger.finfo("")
            # logger.finfo("")
            # logger.finfo(person.name)
            
            # logger.finfo(splitIntoSentences[person.name])
            occupations = prompts.occupationRecognition.extractOccupations(title=title, intro=intro, article=article, personName=person.name, model=model)
            logger.finfo("occupations: " + str(occupations))
            logger.finfo("")
            # occupations = [occ for occ in occupations if (re.search(rf'\b{occ}\b',fulltext) is not None) ]
            person.setOccupations(list(set(occupations)))
            person.setDescriptiveTexts(splitIntoSentences[person.name])
            
        for lastnameKey in namesWithSameLastnames.keys():
            sameLastnames: list[Person] = namesWithSameLastnames[lastnameKey]
            sameLastnames.sort(key=lambda person: person.occurence.fullnameCount, reverse=True)
            for sameLastnamePerson in sameLastnames[1:]:
                sameLastnamePerson.occurence.lastnameCount = 0
        
            
        if len(personsWithFormerNames) > 0:
            
            # check to make sure all persons with names that clash are present in the personsWithFormerNames list
            missingPersonsWithAltNames = []
            for person in personsWithFormerNames:
                altNames = person.alternative_names
                for altName in altNames:
                    # if altname is bit present alraedy we need to add him to personsWithFormerNames
                    if len([x for x in personsWithFormerNames if x.name == altName]) < 1:
                        for resultPerson in resultPersonSet:
                            if resultPerson.name == altName:
                                missingPersonsWithAltNames.append(resultPerson)
                                resultPerson.alternative_names.append(person.name)
            
            for x in missingPersonsWithAltNames:
                personsWithFormerNames.add(x)
                    
            namesSortedByKeys = dict()
            for person in personsWithFormerNames:
                key = ", ".join(person.combinedNameAndFormerNames())
                namesSortedByKeys[key] = (namesSortedByKeys[key] + [person]) if key in namesSortedByKeys.keys() else [person]
            
            for key in namesSortedByKeys:
                if len(namesSortedByKeys[key]) > 1:
                    orderOfNames = prompts.multipleNamesResolver.solveMultiplePersonsWithOverlappingNames(title, intro, article, namesSortedByKeys[key][0].combinedNameAndFormerNames(), model=model)
                    logger.finfo("Order of names:")
                    logger.finfo(orderOfNames)
                    lastKnownName = orderOfNames[-1]
                    
                    lastKnownPerson = None
                    
                    for person in namesSortedByKeys[key]:
                        if person.name != lastKnownName:
                            person.markAsFormerNameOfOtherPerson()
                        else:
                            lastKnownPerson = person
                    
                    if lastKnownPerson != None:
                        for person in namesSortedByKeys[key]:
                            if person.markedAsFormerNameOfOtherPerson:
                                lastKnownPerson.mergeWithDataFrom(person)
                

    removePersons = []
    for person in resultPersonSet:
        if person.occurence.total() < 1 or person.markedAsFormerNameOfOtherPerson:
            removePersons.append(person)
    
    # logger.finfo(resultPersonSet)
    # logger.finfo(removePersons)
    
    for removePerson in removePersons:
        resultPersonSet.remove(removePerson)
    
    for person in resultPersonSet:
        jsonResultFormatted['persons'].append(person.toFormattedObject())
        
    
    return jsonResultFormatted