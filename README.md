# OpenVINO LLM API - simple model serve with streaming
FastAPI HTTP API Service witn minimal OpenAI API compatable services (for example OpenWebUI).

## Installation
 - Python >=3.14 (sorry :))
 - Create venv
	```shell
	python3 -m venv venv
	```
	Linux
	```shell
	source ./venv/bin/activate
	```
	Windows:
	Open cmd.exe, go to path with project
	```shell
	cd C:\Path\To\Project
	venv\Scripts\activate
	```
 - Install requirements
 	```shell
	pip install -r requirements.txt
	```
 - Download OpenVino models from huggingface:
	```sheel
	hf download OpenVINO/gemma-3-4b-it-int4-cw-ov --local-dir models/gemma-3-4b-it-int4-cw-ov
	```
 - Configure what models do you have and what OpenVino Pipeline need for model (see config.py MODELS variable)
 - Run project to serve models
 	```shell
	uvicorn main:app --host=0.0.0.0 --port=11435
	or
	python main.py
   	```

### TODO:
 - unload models after N-time
 - working with many workers with shared pipeline in memory
 - modes: single model mode