from utils import print_elapsed_time, extract_quoted_sentences
import time
import json
import singleArticleAnalyzer
import random
import struct
from typing import Union

from os import listdir
from os.path import isfile, join


MAGIC_BYTE = b'\xaa'

generatorPath = '/opt/ki/ki/evaluation-files/sample-2/'

targetPath = '/opt/ki/ki/evaluation-files/assisted-tagged/'
articleFiles = [f for f in listdir(generatorPath) if isfile(join(generatorPath, f))]

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


    

def readFiles():

    globalTimeAtStart = time.time()
    
    fileCount = 1
    for articlepath in articleFiles:
        
        filePath = join(generatorPath, articlepath)
        targetFilePath = join(targetPath, articlepath + ".json")
        print("Filepath")
        print(filePath)
        
        if isfile(targetFilePath):
            print("skipping")
            continue
        
        fileCount -= 1
        if fileCount < 0:
            return
        
        
        articleUnion = readFile(filePath)
        articleId = articleUnion[0]
        title = str(articleUnion[1], 'utf-8')
        intro = str(articleUnion[2], 'utf-8')
        text = str(articleUnion[3], 'utf-8')

            
        # print("Expected result")
        # print(handTaggedResult)
        
        # articleProcessing.start_server('Meta-Llama-3-8B-Instruct-V2.Q8_0.gguf')
        timeAtStart = time.time()
        resultPersonSet = singleArticleAnalyzer.processArticleWithParameters(title, intro, text)

        print(json.dumps(resultPersonSet, sort_keys=True, indent=2))

    print("Full duration:")
    print_elapsed_time(globalTimeAtStart)


readFiles();   


exit()

        
