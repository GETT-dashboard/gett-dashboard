import re

pronounRegex = re.compile(r'\b([iI]ch|[Dd]u|[Ee]r|[Ss]ie?)\b')
# print(pronounRegex)


def replacementForGroup(match, counter):
    # print(match)
    return match.group(0)+f"[=?{counter.incrementAndGet()}]"

class Counter:
    def __init__(self):
        self.value = 0
        
    def incrementAndGet(self):
        self.value = self.value+1
        return self.value


def annotatedTextWithMarkers(text):
    
    counter = Counter()
    
    fullTextAltered = pronounRegex.sub(lambda m: replacementForGroup(m, counter)
        , text)
    
    return {
        "text": fullTextAltered,
        "counter": counter.value
    }
    