import schemas
from fastapi import APIRouter, Response, UploadFile, status
from storage import storage
from typing import Annotated, Union
from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse
import config
import os
import os.path
from urllib.parse import quote
import sys
import traceback

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    name="file:create_file",
)
async def create_file(file: UploadFile):
    try:
        content  = file.file.read()
        file.file.seek(0)
        print(f"in create_file name : {file.filename} size : {len(content)}")
        if len(content) > config.MAX_SIZE:
            re = {}
            re["detail"] = "File too large"
            # re = json.dumps(re)
            # return Response(content=re,status_code=413, headers={
            #     'Content-Type' : 'application/json',
            # },)
            return JSONResponse(content=re, status_code=413,media_type="application/json",headers={"Content-Type": "application/json"})
        elif await storage.file_integrity(file.filename) == True:
            re = {}
            re["detail"] = "File already exists"
            return JSONResponse(content=re, status_code=409,media_type="application/json",headers={"Content-Type": "application/json"})
        return await storage.create_file(file)
    except Exception as e:
#    print(e)
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg)
        print("An error occurred:", type(e).__name__, "–", e) # An error occurred: NameError – name 'x' is not defined
        for i in traceback.extract_tb(tb):
            print(i)
        traceback.print_exc()
        print("end")

@router.get("/", name="file:retrieve_file")
async def retrieve_file(filename: str) -> Response:
    # TODO: Add headers to ensure the filename is displayed correctly
    #       You should also ensure that enables the judge to download files directly
    try:
        print(f"in retrieve name : {filename}")
        if await storage.file_integrity(filename) == False:
            re = {}
            re["detail"] = "File not found"
            return JSONResponse(status_code=404, content=re)
        temp = filename.split('.')
        file_nameN = ''
        for i in temp:
            file_nameN += quote(i)
            file_nameN += quote('.')
        file_nameN = file_nameN[:-1]
        if file_nameN [-1:] == ';':
            file_nameN = file_nameN[:-1]
        # file_nameN = quote(filename)
        return Response(
            await storage.retrieve_file(filename),
            status_code=200,
            media_type="application/octet-stream",
            headers={
                'Content-Disposition':"attachment;filename*=UTF-8''{0}".format(file_nameN),
                'Content-Type' : 'application/octet-stream',
            },

        )
    except Exception as e:
#    print(e)
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg)
        print("An error occurred:", type(e).__name__, "–", e) # An error occurred: NameError – name 'x' is not defined
        for i in traceback.extract_tb(tb):
            print(i)
        traceback.print_exc()
        print("end")

@router.put("/",  name="file:update_file")
#@router.delete("/", name="file:delete_file")
async def update_file(file: UploadFile):
    try:
        content  = file.file.read()
        file.file.seek(0)
        print(f"in update name : {file.filename}, size = {len(content)}")
        if len(content) > config.MAX_SIZE:
            re = {}
            re["detail"] = "File too large"
            return JSONResponse(content=re, status_code=413,media_type="application/json",headers={"Content-Type": "application/json"})
        elif await storage.file_integrity(file.filename) == False:
            re = {}
            re["detail"] = "File not found"
            return JSONResponse(status_code=404, content=re)
        f = open("/usr/home/judge/hw4/" + str(file.filename),"wb+")
        f.write(content)
        f.close()
        return await storage.update_file(file)
    except Exception as e:
#    print(e)
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg)
        print("An error occurred:", type(e).__name__, "–", e) # An error occurred: NameError – name 'x' is not defined
        for i in traceback.extract_tb(tb):
            print(i)
        traceback.print_exc()
        print("end")

#@router.delete("/", status_code=status.HTTP_200_OK, name="file:delete_file")
@router.delete("/",  name="file:delete_file")
async def delete_file(filename: str) -> str:
    if await storage.file_integrity(filename) == False:
        re = {}
        re["detail"] = "File not found"
        return JSONResponse(status_code=404, content=re)
    else:
        storage.delete(filename)
        re = {}
        re["detail"] = "File deleted"
        return JSONResponse(status_code=200, content=re)
