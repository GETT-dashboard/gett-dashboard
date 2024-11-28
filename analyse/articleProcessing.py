import subprocess
import requests
import json
from time import sleep
import time
import atexit
import re
import asyncio
from utils import print_elapsed_time, getElapsedTime

import fileLogger

logger = fileLogger.FileLogger(__name__)

post_chat_url = 'http://localhost:8000/v1/chat/completions'
post_url = 'http://localhost:8000/v1/completions'
token_count_url = 'http://localhost:8000/extras/tokenize/count'

get_url = 'http://localhost:8000/health'
headers = {'Content-Type': 'application/json'}
process = None
server_is_up = False
activeModel = None
debug = True
remoteServerActive = False


sem = asyncio.Semaphore(n:=1)

modelParams = {
    "Meta-Llama-3-8B-Instruct.Q8_0.gguf": { "gpuLayers": "33", "contextSize": "0"},
    "Meta-Llama-3-8B-Instruct-V2.Q8_0.gguf": { "gpuLayers": "33", "contextSize": "0"},
    "Meta-Llama-3-8B-Instruct.Q6_K.gguf": { "gpuLayers": "33", "contextSize": "0"},
    "Meta-Llama-3-8B-Instruct-V2.Q5_1.gguf": { "gpuLayers": "33", "contextSize": "0"},
    "Llama-3-SauerkrautLM-8b-Instruct-Q8_0_L.gguf": { "gpuLayers": "33", "contextSize": "0"},
    "Meta-Llama-3.1-8B-Instruct-Q8_0.gguf": { "gpuLayers": "33", "contextSize": "24576"},
    "Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf": { "gpuLayers": "33", "contextSize": "24576"},
    "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf": { "gpuLayers": "33", "contextSize": "24576"},
    "Meta-Llama-3.1-8B-Instruct-Q3_K_S.gguf": { "gpuLayers": "33", "contextSize": "24576"},
    "Llama-3.1-SauerkrautLM-8b-Instruct.Q8_0.gguf": { "gpuLayers": "33", "contextSize": "24576"},
    "gemma-2-9b-it-Q8_0.gguf": { "gpuLayers": "43", "contextSize": "0"},
    "gemma-2-9B-it-advanced-v2.1-Q5_K_M.gguf": { "gpuLayers": "43", "contextSize": "16384"},
    "gemma-2-9b-it-Q5_K_M.gguf": { "gpuLayers": "43", "contextSize": "20480"},
    "gemma-2-9b-it-Q6_K.gguf": { "gpuLayers": "43", "contextSize": "16384"},
    "Gemma-2-9B-It-SPPO-Iter3-Q6_K.gguf": { "gpuLayers": "43", "contextSize": "16384"},
    "Gemma-2-9B-It-SPPO-Iter3-Q8_0_L.gguf": { "gpuLayers": "43", "contextSize": "12288"},
    "gemma-2-9b-it-SimPO.Q6_K.gguf": { "gpuLayers": "43", "contextSize": "16384"},
    "gemma-2-27b-it-Q4_K_S.gguf": { "gpuLayers": "28", "contextSize": "12288"},
    "gemma-2-27b-it-IQ3_M.gguf": { "gpuLayers": "36", "contextSize": "12288"},
    "Phi-3-medium-128k-instruct-Q5_K_M.gguf": { "gpuLayers": "41", "contextSize": "12288"},
    "Phi-3.1-mini-128k-instruct-Q8_0.gguf": { "gpuLayers": "41", "contextSize": "12288"},
    "Phi-3.5-mini-instruct.Q8_0.gguf": { "gpuLayers": "33", "contextSize": "16384"},
}

def sendChatPrompt(systemprompt, userprompt, temperature = 0.2, repeat_penalty = 1.1, top_p = 0.95, min_p = 0.05, top_k = 40, responseType="text", response_schema=None, promptDescription="none", model=activeModel, timeoutcall=False):
    
    if not remoteServerActive and (not server_is_up or activeModel != model):
        start_server(model)

    request_body = {
        "messages": [
            {
                "content": systemprompt,
                "role": 'system'
            },
            {
                "content": userprompt,
                "role": 'user'
            },
        ],
        "top_p": top_p,
        "min_p": min_p,
        "top_k": top_k,
        "temperature": temperature,
        "repeat_penalty": repeat_penalty,
        "response_format": {
            "type": responseType,
            "schema": response_schema
        }
    }
    # logger.finfo(request_body)
    data= json.dumps(request_body)
    try:

        prompt_start_time = time.time()
        if debug:
            logger.finfo(f"Prompt: {promptDescription}", end='', flush=True)
        logger.finfo(f"Prompt: {promptDescription}")
        response = requests.post(post_chat_url, data=data, headers=headers, timeout=240)

        if debug:    
            logger.finfo(f" took {getElapsedTime(prompt_start_time)} with temperature= {temperature}, repeat_penalty={repeat_penalty}, top_p={top_p}, min_p={min_p}, top_k={top_k}")
            logger.finfo(response.json())
        logger.finfo(f" took {getElapsedTime(prompt_start_time)} with temperature= {temperature}, repeat_penalty={repeat_penalty}, top_p={top_p}, min_p={min_p}, top_k={top_k}")
        if response.json()['choices'][0] != None:
            textResult = response.json()['choices'][0]['message']['content'];
            textResult = textResult.replace("[ ,", "[ ")
            # if debug:   
                # logger.finfo(textResult)
            return json.loads(textResult)
        else:
            if debug:
                logger.finfo("None Result!")
            logger.finfo(f"None Result: {response.json()}")
            if not timeoutcall:
                return sendChatPrompt(systemprompt, userprompt, temperature, repeat_penalty, top_p, min_p, top_k, responseType, response_schema, promptDescription, model, True)
            else:
                return "ERROR";
    except requests.exceptions.Timeout:
        if debug:
            logger.finfo("Timed out")
        
        logger.finfo("restarting server due to timeout")
        start_server(model)
        
        if not timeoutcall:
            return sendChatPrompt(systemprompt, userprompt, temperature, repeat_penalty, top_p, min_p, top_k, responseType, response_schema, promptDescription, model, True)
        else:
            return "ERROR";
    except Exception as e:
        logger.finfo("exception on send chat prompt; answer is only ERROR")
        logger.finfo(str(e))
        if debug: 
            logger.finfo('Exception: ', e)
        return "ERROR";

async def sendPrompt(prompt, temperature = 0, repeat_penalty = 1, top_p = 0.95, top_k = 40, responseType="text", response_schema=None, promptDescription="none"):
    
    if not server_is_up:
        await start_server()
    
    request_body = {
        "prompt": prompt,
        "top_p": top_p,
        "top_k": top_k,
        "temperature": temperature,
        "repeat_penalty": repeat_penalty,
        "response_format": {
            "type": responseType,
            "schema": response_schema
        }
    }
    # logger.finfo(request_body)
    data= json.dumps(request_body)
    try:

        prompt_start_time = time.time()
        response = requests.post(post_url, data=data, headers=headers)
        if debug:
            print_elapsed_time(prompt_start_time)
            # logger.finfo(response.json())
        return str(response.json()['choices'][0]['text'])
    except Exception as e:
        if debug:
            logger.finfo('Exception: ', e)
        return "ERROR";

##returns token count
def approximateTokenCount(text):
    if not server_is_up:
        start_server()

    request_body = {
        "input": text
    }
    # logger.finfo(request_body)
    data= json.dumps(request_body)
    try:

        prompt_start_time = time.time()
        response = requests.post(token_count_url, data=data, headers=headers)
        if debug:
            print_elapsed_time(prompt_start_time)
        return int(response.json()['count'])
    except Exception as e:
        if debug:
            logger.finfo('Exception: ', e)
        return "ERROR";

def start_server(model):

    global process, server_is_up, activeModel, gpuLayersByModelId

    if server_is_up:
        cleanup()
        server_is_up= False
    

    activeModel = model
    server_start_time = time.time()
    
    cmds = ["/opt/llamacpp/llama.cpp/llama-server", "--host", "0.0.0.0", "-m", 
                    f"/opt/ki/ki/models/{model}", "-ngl", modelParams[model]['gpuLayers'], "-c", modelParams.get(model)['contextSize'], "--chat-template", "chatml", "--port", "8000"]
    # if debug:
    logger.finfo("Server Start Command: " + " ".join(cmds))
    process = subprocess.Popen(cmds, shell=False, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL ,stdout=subprocess.DEVNULL)

    # llama-2-7b-chat.Q8_0.gguf
    # codellama-34b-instruct.Q8_0.gguf
    # llama-2-13b-chat.Q8_0.gguf
    # gemma-7b-it.Q8_0.gguf

    while not server_is_up:
        result = None
        try:
            result = requests.get(get_url)
            pass
        except Exception as e:
            if debug:
                logger.finfo("Server is still not running...")
            pass
        else:
            
            if result is not None and result.status_code >= 200 and result.status_code < 500:
                server_is_up = True
        sleep(3)
    if debug:
        logger.finfo("Server is running...")
        print_elapsed_time(server_start_time)

def close_server():
    process.terminate()


def cleanup():
    global process, remoteServerActive
    
    if remoteServerActive:
        return
    timeout_sec = 2
    p_sec = 0
    for second in range(timeout_sec):
        if process.poll() == None:
            time.sleep(1)
            p_sec += 1
        if p_sec >= timeout_sec:
            process.kill() # supported from python 2.6
    if debug:
        logger.finfo('cleaned up!')
        time.sleep(2)

atexit.register(cleanup)


# python3 -m llama_cpp.server --host 0.0.0.0 --config_file models.config --n_gpu_layers -1 --n_ctx 0 --chat_format chatml --use_mmap 0

