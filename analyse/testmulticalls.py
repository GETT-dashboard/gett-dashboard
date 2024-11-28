import threading
from testData import texts
import processonly

# Called by each thread
def runPrompt(text):
    print(processonly.processArticle(text))

threads = []

for article in texts:
    t = threading.Thread(target=runPrompt, args = (article,))
    t.daemon = True
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()
