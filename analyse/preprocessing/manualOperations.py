import re

TEXT_PART_SEPERATOR = " ;;; "

def replacementForGroup(match):
    matchedText = match.group(0)
    if matchedText.endswith(" "):
        matchedText = matchedText[:-1]
    return matchedText + "\n"

interviewerAtStartOfSentenceRegex = re.compile(r'(^\b\S+:\s\b)')

def splitIntoParagraphs(text):
    
    splitByDoubleNewLineText = text.split("\n\n")

    return splitByDoubleNewLineText

def splitIntoSentences(joinedText, isInterview = False):
    partsSplit = joinedText.split(TEXT_PART_SEPERATOR)
    title =partsSplit[0]
    intro =partsSplit[1]
    text =partsSplit[2]
    replacedTitle = split_text(title)
    replacedIntro = split_text(intro)
    replacedText = split_text(text)

    replacedTitle = [x for x in replacedTitle if len(x) > 0]
    replacedIntro = [x for x in replacedIntro if len(x) > 0]
    if isInterview:
        replacedText = [interviewerAtStartOfSentenceRegex.sub("", x) for x in replacedText if len(x) > 0]
    
    return replacedTitle + replacedIntro + replacedText

def split_text(text):
    
    # Schritt 1: Zitate schützen
    quotes = re.findall(r'([»|\"|“].*?[«|\"|“])', text)
    protected_text = text
    for i, quote in enumerate(quotes):
        quoteReplacement = f"__QUOTE_{i}__"
        if quote[-2] in ".?!":
            quoteReplacement = quoteReplacement + "."
        protected_text = protected_text.replace(quote, quoteReplacement)
    
    
    # Schritt 2: Text in Sätze aufteilen
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-ZÄÖÜ][a-zäöüß]\.)(((?<=\.|\?|\!)[\s|\r\n|\r|\n]+)|([\r\n|\r|\n]{2}))(?!Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember|[a-zäöüß])', protected_text)
    
    # Schritt 3: Platzhalter wieder durch Zitate ersetzen
    final_sentences = []
    for sentence in sentences:
        if sentence != None:
            for i, quote in enumerate(quotes):
                quoteReplacement = f"__QUOTE_{i}__"
                if quote[-2] in ".?!":
                    quoteReplacement = quoteReplacement + "."
                
                sentence = sentence.replace(quoteReplacement, quote)
            final_sentences.append(sentence)
    
    return final_sentences