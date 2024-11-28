## Overview
This project contains the GETT analysis process, used to extract data from media articles.

The code is the result of mutliple student work assignments.

## Getting Started


1. Install pip requirements.
2. Make sure to have llama.cpp setup and configured.

The analysis relys on the use of [llama.cpp](https://github.com/ggerganov/llama.cpp) as a llm server.
When executing the code locally make sure to edit the executable path in articleProcessing.py accordingly to your personal server.
HINT: while it is possible to run without GPU hardware acceleration, CPU only inference on llm models is slow. A single article might take 10+ minutes without hardware acceleration.
Check articleProcessing.py to adapt the call to the local llama.cpp server.

3. Run analyzer.
The simplest usage would be the use of the analyzer.py script.
Using "python3 -m analyzer < INPUTFILE" would run the script and print the result to the console.

The INPUTFILE Format needs to follow a specific structure as defined in analyzer.py:

MAGIC_BYTE = b'\xaa'

8 bytes => article UUID
4 bytes => length of following title bytes (= x)
x bytes => title bytes
MAGIC_BYTE
4 bytes => length of following article summary/teaser bytes (= y)
y bytes => summary/teaser bytes
MAGIC_BYTE
8 bytes => length of following article text bytes (= z)
z bytes =>  article text bytes


