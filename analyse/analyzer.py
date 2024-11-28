from utils import print_elapsed_time, extract_quoted_sentences
import time
from time import sleep
import logging
logger = logging.getLogger()
logger.setLevel(level=logging.ERROR)
import fileLogger

# "Name of the person who said a quote":"Direct or indirect quote"

import sys
import struct
import json
from typing import Union

import singleArticleAnalyzer

MAGIC_BYTE = b'\xaa'

logger = fileLogger.FileLogger(__name__)

def readStdIn() -> Union[tuple[int, bytes, bytes, bytes], None]:
    articleIdBytes = sys.stdin.buffer.read(8)
    if (len(articleIdBytes) == 0):
        return None
    articleId: int = struct.unpack(">Q", articleIdBytes)[0]

    titleSizeBytes = sys.stdin.buffer.read(4)
    titleSize: int = struct.unpack(">I", titleSizeBytes)[0]
    title = sys.stdin.buffer.read(titleSize)

    magicByte = sys.stdin.buffer.read(1)
    if (magicByte != MAGIC_BYTE):
        return None

    summarySizeBytes = sys.stdin.buffer.read(4)
    summarySize: int = struct.unpack(">I", summarySizeBytes)[0]
    summary = sys.stdin.buffer.read(summarySize)

    magicByte = sys.stdin.buffer.read(1)
    if (magicByte != MAGIC_BYTE):
        return None

    fileSizeBytes = sys.stdin.buffer.read(8)
    fileSize: int = struct.unpack(">Q", fileSizeBytes)[0]
    text = sys.stdin.buffer.read(fileSize)
    return articleId, title, summary, text

def writeStdOut(articleId, resultJson):
    articleIdBytes = struct.pack(">Q", articleId)
    logger.finfo("writeStdOut before write articleIdBytes")
    sys.stdout.buffer.write(articleIdBytes)

    dataSize = len(resultJson)
    dataSizeBytes = struct.pack(">Q", dataSize)
    sys.stdout.buffer.write(dataSizeBytes)
    sys.stdout.buffer.write(bytes(resultJson, 'utf-8'))
    sys.stdout.buffer.flush()

def processArticle(title, intro, article):
    
    logger.finfo("processArticle method started")
    try:
        
        return json.dumps(singleArticleAnalyzer.processArticleWithParameters(title.decode('utf-8'), intro.decode('utf-8'), article.decode('utf-8'), model="gemma-2-9b-it-Q6_K.gguf", temperature=0.1, repeat_penalty=1, top_p=0.9, top_k=80))
    
    except Exception as e:
        
        logger.finfo("processArticle method Exception" + str(e))
        return json.dumps({"error": str(e)})

while True:
    time.sleep(1)
    data = readStdIn()
    if (data is None):
        time.sleep(1)
        continue
    resultJson = processArticle(data[1], data[2], data[3])
    time.sleep(1)
    writeStdOut(data[0], resultJson)
    time.sleep(1)

