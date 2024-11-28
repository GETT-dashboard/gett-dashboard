import re

class TextElement():
    text: str
    def __init__(self, text):
        self.text = text
        
    @classmethod
    def fromJsonTextElement(cls, jsonElement):
        return cls(jsonElement['text'])
    
    def __repr__(self):
        return "TextElement(%s)" % (self.text)
    def __eq__(self, other):
        if isinstance(other, TextElement):
            return (self.text == other.text)
        else:
            return False
    def __ne__(self, other):
        return (not self.__eq__(other))
    def __hash__(self):
        return hash(self.__repr__())

class Occurence():
    inTitle: bool
    inIntro: bool
    firstnameCount: int
    lastnameCount: int
    fullnameCount: int
    nicknameCount: int
    def __init__(self, firstnameCount, lastnameCount, fullnameCount, nicknameCount, inTitle, inIntro)-> None:
        self.inTitle = inTitle
        self.inIntro = inIntro
        self.firstnameCount = firstnameCount
        self.lastnameCount = lastnameCount
        self.fullnameCount = fullnameCount
        self.nicknameCount = nicknameCount

    def total(self):
        return self.firstnameCount + self.lastnameCount + self.fullnameCount + self.nicknameCount

    def mergeWithDataFrom(self, otherOccurence):
        if isinstance(otherOccurence, Occurence):
            self.inTitle = self.inTitle or otherOccurence.inTitle
            self.inIntro = self.inIntro or otherOccurence.inIntro
            self.firstnameCount = self.firstnameCount + otherOccurence.firstnameCount
            self.lastnameCount = self.lastnameCount + otherOccurence.lastnameCount
            self.fullnameCount = self.fullnameCount + otherOccurence.fullnameCount
            self.nicknameCount = self.nicknameCount + otherOccurence.nicknameCount

    def differencesOrFalse(self, other) -> dict | bool:
        if isinstance(other, Occurence):
            differences = dict()
            
            if self.inIntro != other.inIntro:
                differences['inIntro'] = f"{self.inIntro} != {other.inIntro}"
            if self.inTitle != other.inTitle:
                differences['inTitle'] = f"{self.inTitle} != {other.inTitle}"
                
            if self.firstnameCount != other.firstnameCount:
                differences['firstnameCount'] = f"{self.firstnameCount} != {other.firstnameCount}"
            if self.lastnameCount != other.lastnameCount:
                differences['lastnameCount'] = f"{self.lastnameCount} != {other.lastnameCount}"
            if self.fullnameCount != other.fullnameCount:
                differences['fullnameCount'] = f"{self.fullnameCount} != {other.fullnameCount}"
            if self.nicknameCount != other.nicknameCount:
                differences['nicknameCount'] = f"{self.nicknameCount} != {other.nicknameCount}"
            
            if len(differences.keys()) == 0:
                return False
            else:
                return differences
            
        else:
            return None

class Person:
    
    name: str
    firstname: str
    lastname: str
    nickname: str
    alternative_names: list[str]
    academic_title: str
    nobility_title_or_rank: str
    age: str
    sex: str
    occurence: Occurence
    markedAsFormerNameOfOtherPerson: bool
    descriptiveTexts: list[TextElement]
    occupations: list[TextElement]
    directQuotes: list[TextElement]
    quotedInTitle: bool
    quotedInIntro: bool
    def __init__(self, name: str,
        firstname: str,
        lastname: str,
        nickname: str,
        alternative_names: list[str],
        academic_title: str,
        nobility_title_or_rank: str,
        age: int,
        sex: str,
        occurence: Occurence = None,
        markedAsFormerNameOfOtherPerson: bool = False,
        descriptiveTexts: list[TextElement] = None,
        occupations: list[TextElement] = None,
        directQuotes: list[TextElement] = None,
        quotedInTitle: bool = None,
        quotedInIntro: bool = None) -> None:
            self.name = name
            self.firstname = firstname
            self.lastname = lastname
            self.nickname = nickname
            self.alternative_names = alternative_names
            self.academic_title = academic_title
            self.nobility_title_or_rank = nobility_title_or_rank
            self.age = age
            self.sex = sex
            self.occurence = occurence
            self.markedAsFormerNameOfOtherPerson = markedAsFormerNameOfOtherPerson
            self.descriptiveTexts = [] if (descriptiveTexts is None or len(descriptiveTexts) < 1) else descriptiveTexts
            self.occupations = [] if (occupations is None or len(occupations) < 1) else occupations
            self.directQuotes = [] if (directQuotes is None or len(directQuotes) < 1) else directQuotes
            self.quotedInTitle = quotedInTitle
            self.quotedInIntro = quotedInIntro
    
    @classmethod
    def fromLLMResult(cls, jsonResult):
        analysisAge = jsonResult['details']['alter']
        analysisSex = jsonResult['details']['biologisches_geschlecht']
        alternative_names = jsonResult['details']['alternative_namen']
        alternative_names = [aName for aName in alternative_names if (aName != jsonResult['name'] + "s" and aName  + "s" != jsonResult['name'])]
        
        return cls(name = jsonResult['name'],
            firstname = jsonResult['details']['vorname'],
            lastname = jsonResult['details']['nachname'],
            nickname = jsonResult['details']['spitzname'],
            alternative_names = alternative_names,
            academic_title = jsonResult['details']['akademischer_titel'],
            nobility_title_or_rank = jsonResult['details']['adels_oder_rangtitel'],
            age = -1 if analysisAge == 'unbekannt' else int(analysisAge),
            sex = "unknown" if analysisSex == "unbekannt" else "female" if analysisSex == 'weiblich' else "male",
            )
    
    
    @classmethod
    def fromPerfectResult(cls, json):
        return cls(name = json['name'],
            firstname = None,
            lastname = None,
            nickname = None,
            alternative_names = [] if 'alternativeNames' not in json.keys() else json['alternativeNames'],
            academic_title = None,
            nobility_title_or_rank = None,
            age = json['age'],
            sex = json['sex'],
            occurence = Occurence(firstnameCount=json['occurences']['firstNameOnly'],
                                  lastnameCount=json['occurences']['lastNameOnly'],
                                  fullnameCount=json['occurences']['fullName'],
                                  nicknameCount=0, #json['occurences']['nickname'],
                                  inTitle=json['inTitle'],
                                  inIntro=json['inIntro']
                                ),
            markedAsFormerNameOfOtherPerson = False,
            descriptiveTexts = list(map(lambda element: TextElement.fromJsonTextElement(element), json['descriptiveTexts'])) if ('descriptiveTexts' in json.keys() and None != json['descriptiveTexts']) else [],
            occupations = list(map(lambda element: TextElement.fromJsonTextElement(element), json['occupations'])) if ('occupations' in json.keys() and None != json['occupations']) else [],
            directQuotes = list(map(lambda element: TextElement.fromJsonTextElement(element), json['directQuotes'])) if ('directQuotes' in json.keys() and None != json['directQuotes']) else [],
            quotedInTitle = json['quotedInTitle'],
            quotedInIntro = json['quotedInIntro']
            )
    
    def setDescriptiveTexts(self, descriptiveTexts):
        self.descriptiveTexts = list(map(lambda text: TextElement(text), descriptiveTexts))
        
    def setOccupations(self, occupations):
        self.occupations = list(map(lambda text: TextElement(text), occupations))
    
    def setDirectQuotes(self, directQuotes):
        self.directQuotes = list(map(lambda text: TextElement(text), directQuotes))
        
    def updateWithDirectQuotesResults(self, directQuotesTextElements, quotedInTitle, quotedInIntro):
        self.directQuotes = list(map(lambda text: TextElement(text['text']), directQuotesTextElements))
        self.quotedInTitle = quotedInTitle
        self.quotedInIntro = quotedInIntro
        
    def setOccurence(self, occurence):
        self.occurence = occurence
    
    def isLastNameKnown(self):
        return self.lastname != None and self.lastname != 'unbekannt' and len(self.lastname) > 0
    
    def isFirstNameKnown(self):
        return self.firstname != None and self.firstname != 'unbekannt' and len(self.firstname) > 0
    
    def isNickmameKnown(self):
        return self.nickname != None and self.nickname != 'unbekannt' and len(self.nickname) > 0
    
    def hasNobiltiyTitle(self):
        return self.nobility_title_or_rank != None and self.nobility_title_or_rank != 'unbekannt' and len(self.nobility_title_or_rank) > 0
    
    def hasAcademicTitle(self):
        return self.academic_title != None and self.academic_title != 'unbekannt' and len(self.academic_title) > 0
    
    def totalName(self):
        return str.join("", [f"{(self.academic_title + ' ') if self.hasAcademicTitle() else ''}",
                f"{(self.nobility_title_or_rank + ' ') if self.hasNobiltiyTitle() else ''}",
                f"{(self.firstname + ' ') if self.isFirstNameKnown() else ''}",
                f"{(self.lastname) if self.isLastNameKnown() else ''}",
                f"{self.nickname if (not self.isLastNameKnown() and not self.isFirstNameKnown()) else ''}"]).strip()
    
    def nameWithFirstnameAndLastnameIfPresent(self):
        return str.join("", [f"{(self.firstname + ' ') if self.isFirstNameKnown() else ''}",
                f"{(self.lastname) if self.isLastNameKnown() else ''}",
                f"{self.nickname if (not self.isLastNameKnown() and not self.isFirstNameKnown()) else ''}"]).strip()
    
    def fullnameRegex(self):
        return re.compile("(\\b" + self.name + "s?\\b)", re.IGNORECASE) if (not self.isFirstNameKnown() and not self.isLastNameKnown()) else re.compile("(\\b" + self.nameWithFirstnameAndLastnameIfPresent() + "s?\\b)", re.IGNORECASE)

    #lastname regex is only valid if we know a firstname
    def lastnameRegex(self):
        return None if not self.isFirstNameKnown() else re.compile( "(?<!\\b" + self.firstname+"\\b )" + "(\\b" + self.lastname + "s?\\b)", re.IGNORECASE)
    
    #lastname regex is only valid if we know a firstname
    def firstnameRegex(self):
        return None if not self.isLastNameKnown() else re.compile("(\\b" + self.firstname + "s?\\b)" + "(?! \\b" + self.lastname+"s?\\b)" , re.IGNORECASE)
    
    def nicknameRegex(self):
        return None if not self.isNickmameKnown() else re.compile("(\\b" + self.nickname + "s?\\b)", re.IGNORECASE)
    
    def combinedNameAndFormerNames(self):
        names = [self.name];
        names = names + self.alternative_names
        names.sort()
        return names
    
    def markAsFormerNameOfOtherPerson(self):
        self.markedAsFormerNameOfOtherPerson = True
        
    def mergeWithDataFrom(self, otherPerson):
        if isinstance(otherPerson, Person):
            self.occupations = self.occupations + otherPerson.occupations
            self.descriptiveTexts = self.descriptiveTexts + otherPerson.descriptiveTexts
            self.directQuotes = self.directQuotes + otherPerson.directQuotes
            self.occurence.mergeWithDataFrom(otherPerson.occurence)
            self.alternative_names = list(set(self.alternative_names + otherPerson.alternative_names))
            self.alternative_names.remove(self.name)

    def toFormattedObject(self):
        return {
            "name": self.name,
            "alternativeNames": self.alternative_names,
            "age": self.age,
            "sex": self.sex,
            "occurences": {
                "total": self.occurence.total(),
                "firstNameOnly": self.occurence.firstnameCount,
                "lastNameOnly": self.occurence.lastnameCount,
                "fullName": self.occurence.fullnameCount,
                "nickname": self.occurence.nicknameCount
            },
            "inTitle": self.occurence.inTitle,
            "inIntro": self.occurence.inIntro,
            "_name": {
                "firstname": self.firstname if self.isFirstNameKnown() else None,
                "lastname": self.lastname if self.isLastNameKnown() else None,
                "nickname": self.nickname if self.isNickmameKnown() else None,
                "alternative_names": self.alternative_names,
                "academic_title": self.academic_title if self.hasAcademicTitle() else None,
                "nobility_title_or_rank": self.nobility_title_or_rank if self.hasNobiltiyTitle() else None
            },
            "descriptiveTexts": list(map(lambda textElement: {"text": textElement.text}, self.descriptiveTexts)) if self.descriptiveTexts != None else [],
            "occupations": list(map(lambda textElement: {"text": textElement.text}, self.occupations)) if self.occupations != None else [],
            "directQuotes": list(map(lambda textElement: {"text": textElement.text}, self.directQuotes)) if self.directQuotes != None else [],
            "quotedInTitle": self.occurence.inTitle,
            "quotedInIntro": self.occurence.inIntro,
        }
        
    def differencesOrFalse(self, other) -> dict | bool:
        if isinstance(other, Person):
            differences = dict()
            
            if self.name != other.name:
                differences['name'] = f"{self.name} != {other.name}"
            if self.age != other.age:
                differences['age'] = f"{self.age} != {other.age}"
            if self.sex != other.sex:
                differences['sex'] = f"{self.sex} != {other.sex}"
                
            occurenceDif = self.occurence.differencesOrFalse(other.occurence)
            
            if occurenceDif == None:
                differences['occurences'] = f"WRONG CLASS"
            elif isinstance(occurenceDif, dict):
                differences['occurences'] = occurenceDif
                
            missingAlternativeNames = []
            additionalAlternativeNames = []
            
            for aName in self.alternative_names:
                if aName not in other.alternative_names:
                    missingAlternativeNames.append(aName)
                    
            for aName in other.alternative_names:
                if aName not in self.alternative_names:
                    additionalAlternativeNames.append(aName)
            
            
                    
            
            if len(missingAlternativeNames) > 0 or len(additionalAlternativeNames) > 0:
                differences['alternativNames'] = {}
                
            if len(missingAlternativeNames) > 0:
                differences['alternativNames']['missingNameCount'] = len(missingAlternativeNames)
                differences['alternativNames']['missingNames'] = missingAlternativeNames
            if len(additionalAlternativeNames) > 0:
                differences['alternativNames']['additionalNameCount'] = len(additionalAlternativeNames)
                differences['alternativNames']['additionalNames'] = additionalAlternativeNames
            
            
            self.checkTextElements(other, differences, 'descriptiveTexts')
            self.checkTextElements(other, differences, 'occupations')
            self.checkTextElements(other, differences, 'directQuotes')
                
                
                
            # missingOccupations = []
            # additionalOccupations = []
            
            # for dText in self.occupations:
            #     if dText not in other.occupations:
            #         missingOccupations.append(dText)
            
            
            # for dText in other.occupations:
            #     if dText not in self.occupations:
            #         additionalOccupations.append(dText)
            
            # if len(self.occupations) == 0:
            #     percentagePresent = 1
            # else:
            #     percentagePresent = 1 - (len(missingOccupations) / len(self.occupations))
            
            # if len(missingOccupations) > 0 or len(additionalOccupations) > 0 or percentagePresent < 1:
            #     differences['occupations'] = {}
            
            # if percentagePresent < 1:
            #     differences['occupations']['percentage'] = round(percentagePresent,2)
                
            
            # if len(missingOccupations) > 0:
            #     differences['occupations']["missingTextsCount"] = len(missingOccupations)
            #     differences['occupations']["missingTexts"] = list(map(lambda element: element.text, missingOccupations))
            
            # if len(additionalOccupations) > 0:
            #     differences['occupations']["additionalTextsCount"] = len(additionalOccupations)
            #     differences['occupations']["additionalTexts"] = list(map(lambda element: element.text, additionalOccupations))
                
                
                
                
            # missingDirectQuotes = []
            # additionalDirectQuotes = []
            
            # for dText in self.directQuotes:
            #     if dText not in other.directQuotes:
            #         missingDirectQuotes.append(dText)
            
            
            # for dText in other.directQuotes:
            #     if dText not in self.directQuotes:
            #         additionalDirectQuotes.append(dText)
            
            # if len(self.directQuotes) == 0:
            #     percentagePresent = 1
            # else:
            #     percentagePresent = 1 - (len(missingDirectQuotes) / len(self.directQuotes))
            
            # if len(missingDirectQuotes) > 0 or len(additionalDirectQuotes) > 0 or percentagePresent < 1:
            #     differences['directQuotes'] = {}
            
            # if percentagePresent < 1:
            #     differences['directQuotes']['percentage'] = round(percentagePresent,2)
                
            
            # if len(missingDirectQuotes) > 0:
            #     differences['directQuotes']["missingTextsCount"] = len(missingDirectQuotes)
            #     differences['directQuotes']["missingTexts"] = list(map(lambda element: element.text, missingDirectQuotes))
            
            # if len(additionalDirectQuotes) > 0:
            #     differences['directQuotes']["additionalTextsCount"] = len(additionalDirectQuotes)
            #     differences['directQuotes']["additionalTexts"] = list(map(lambda element: element.text, additionalDirectQuotes))

        
        
            if len(differences.keys()) == 0:
                return False
            else:
                return differences
            
        else:
            return None

    def checkTextElements(self, other, differences, key):
        missingTextElements = []
        additionalTextElements = []
        
        selfElements = self.occupations if key == 'occupations' else self.descriptiveTexts if key == 'descriptiveTexts' else self.directQuotes if key == 'directQuotes' else []
        otherElements = other.occupations if key == 'occupations' else other.descriptiveTexts if key == 'descriptiveTexts' else other.directQuotes if key == 'directQuotes' else []
            
        for dText in selfElements:
            if dText not in otherElements:
                missingTextElements.append(dText)
            
            
        for dText in otherElements:
            if dText not in selfElements:
                additionalTextElements.append(dText)
            
        if len(selfElements) == 0:
            percentagePresent = 1
        else:
            percentagePresent = 1 - (len(missingTextElements) / len(selfElements))
            
        if len(missingTextElements) > 0 or len(additionalTextElements) > 0 or percentagePresent < 1:
            differences[key] = {}
            
        if percentagePresent < 1:
            differences[key]['percentage'] = round(percentagePresent,2)
                
            
        if len(missingTextElements) > 0:
            differences[key]["missingTextsCount"] = len(missingTextElements)
            differences[key]["missingTexts"] = list(map(lambda element: element.text, missingTextElements))
            
        if len(additionalTextElements) > 0:
            differences[key]["additionalTextsCount"] = len(additionalTextElements)
            differences[key]["additionalTexts"] = list(map(lambda element: element.text, additionalTextElements))
            
            
    
    def __repr__(self):
        return "Person(%s, %s, %s, also known as: %s)" % (self.name, self.sex, self.age, self.alternative_names)
    def __eq__(self, other):
        if isinstance(other, Person):
            return ((self.name == other.name) and (self.sex == other.sex) and (self.age == other.age))
        else:
            return False
    def __ne__(self, other):
        return (not self.__eq__(other))
    def __hash__(self):
        return hash(self.name + self.sex + str(self.age))