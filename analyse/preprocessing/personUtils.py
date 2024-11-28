from difflib import SequenceMatcher
import re

regexDoppelName = re.compile("([A-ZÄÖÜ]{1}[a-zA-ZäöüÄÖÜß]+-[A-ZÄÖÜ]{1}[a-zA-ZäöüÄÖÜß]+)")
            
            
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def reduceFoundNames(listOfNames):
    
    #start with shortest names
    sortedNames = sorted(listOfNames, key=len)
    notsimilar_new_list = []
    for name in sortedNames:
        
        #eliminate if there is an "Anrede"
        if name.startswith("Herr") or name.startswith("Frau"):
            name = name[4:] 
        
        #do not add if it is no a "Eigenname" => lower letter starting string
        if name[0].islower():
            continue
        
        #Capslock names are normally the magazine itself
        if name.isupper():
            continue
        
        if len(notsimilar_new_list) == 0:
            notsimilar_new_list.append(name)
        else:
            isSimiliar = False
            for newListName in notsimilar_new_list:
                if similar(newListName, name) > 0.9:
                    isSimiliar = True
            if not isSimiliar:
                notsimilar_new_list.append(name)
    
    
    ##Doppelnamen Check:
    
    # for each: if contains "-"
    doppelNameCheckedList = []
    for name in notsimilar_new_list:
        matches = regexDoppelName.match(name)
        if matches:
            firstPart = name.split("-")[0]
            for secondIterName in notsimilar_new_list:
                if name != secondIterName:
                    if secondIterName.endswith(firstPart):
                        doppelNameCheckedList.append(f"{secondIterName}{name[len(firstPart):]}")
        else:
            doppelNameCheckedList.append(name)
    
    
    new_list = []
    reverseSortedNotSimilarNames = sorted(doppelNameCheckedList, key=len, reverse=True)
    for name in reverseSortedNotSimilarNames:
        if len(new_list) == 0:
            new_list.append(name)
        else:
            isSimiliar = False
            for newListName in new_list:
                if name in newListName:
                    isSimiliar = True
                    break
            if not isSimiliar:
                new_list.append(name)
    
    new_list = list(map(lambda s: s if not s.endswith("s") else (s[:-1] + " oder " + s), new_list))
                
    return new_list


def replaceENSpellingWithGermanIfPresent(en_names, de_names):
    
    result = []
    for en_name in en_names:
        replaced = False
        for de_name in de_names:
            if similar(en_name, de_name) > 0.90:
                # print(f"replaced_name: {en_name} with {de_name}")
                result.append(de_name)
                replaced = True
                break
        if not replaced:
            result.append(en_name)
    
    return result