#!/bin/bash
CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_PREFIX_PATH=/usr/local/cuda-12.3" FORCE_CMAKE=1 pip install -r requirements.txt