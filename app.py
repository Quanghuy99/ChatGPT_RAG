from typing import Callable, List
from fastapi import FastAPI, Request, Response, HTTPException, Form, File, UploadFile
from fastapi.routing import APIRoute
from fastapi.exceptions import FastAPIError
from fastapi.responses import JSONResponse
import uvicorn
from io import BytesIO
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import os
import time
import traceback
import torch
import ast
from predict import predict_llm
from config_app.config import get_config
from utils.logging import Logger_Days, Logger_maxBytes
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
import openpyxl
import pandas as pd
from search_product import product_seeking 

config_app = get_config()

if not os.path.exists("./logs"):
    os.makedirs("./logs")
file_name = './logs/logs'
log_obj = Logger_Days(file_name)

app = FastAPI()

class InputData(BaseModel):
    InputText: str
    IdRequest: str
    NameBot: str
    User: str

numberrequest = 0
@app.post('/llm')
async def post(data: InputData, request: Request = None):
    start_time = time.time()
    global numberrequest
    numberrequest = numberrequest + 1
    print("numberrequest", numberrequest)
    
    results = {
    "products" : [],
    "terms" : [],
    "content" : "",
    "status" : 200,
    "message": "",
    "time_processing":''
    }
    log_obj.info("-------------------------NEW_SESSION----------------------------------")
    log_obj.info("GuildID  = :" + " " + str(data.IdRequest)) 
    log_obj.info("User  = :" + " " + str(data.User))
    log_obj.info("NameBot  = :" + " " + str(data.NameBot))
    log_obj.info("InputText:" + " " + str(data.InputText)) # cau hoi
    log_obj.info("IP_Client: " +str(request.client.host))
    log_obj.info("NumberRequest: " +str(numberrequest))
    result = predict_llm(data.InputText, data.IdRequest, data.NameBot, data.User, log_obj)

    results["content"] = result

    # tim san pham
    results = product_seeking(results = results, texts=result,path="./data/product_info.xlsx")
            
    results['time_processing'] = str(time.time() - start_time)
    print(results)
    return results

uvicorn.run(app, host=config_app['server']['ip_address'], port=int(config_app['server']['port']))

# str(User) + "/" + str(NameBot) + "/" + str(IdRequest)