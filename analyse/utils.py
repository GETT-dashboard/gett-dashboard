import time
import re
import fileLogger
logger = fileLogger.FileLogger(__name__)

debugPrint = False

def print_elapsed_time(start_time, file=None):
    # logger.finfo(f"Elapsed time: {getElapsedTime(start_time)}", file=file)
    if debugPrint:
        print(f"Elapsed time: {getElapsedTime(start_time)}", file=file)
    else:
        
        logger.finfo(f"Elapsed time: {getElapsedTime(start_time)}")

def getElapsedTime(start_time):
    elapsed_time = time.time() - start_time
    minutes = elapsed_time // 60
    seconds = elapsed_time - minutes*60
    return f"{minutes} minutes {seconds:.2f} seconds"


def extract_quoted_sentences(text):
    pattern_1 = r'"([^"]*)"'
    pattern_2 = r'»(.*?)«'
    
    # Find all matches of the pattern in the text
    quoted_sentences = re.findall(pattern_1, text) + re.findall(pattern_2, text)
    return quoted_sentences