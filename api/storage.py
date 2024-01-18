import base64
import hashlib
import sys
from pathlib import Path
from typing import List

import schemas
import config
from config import settings
from fastapi import UploadFile
from loguru import logger
from os import listdir
from os.path import isfile, join
import json
import os
import traceback


class Storage:
    def __init__(self, is_test: bool):
        self.block_path: List[Path] = [
            Path("/tmp") / f"{settings.FOLDER_PREFIX}-{i}-test"
            if is_test
            else Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}"
            for i in range(config.NUM_DISKS)
        ]
        self.dic = {}
        print(config.NUM_DISKS)
        self.__create_block()

    def __create_block(self):
        for path in self.block_path:
            logger.warning(f"Creating folder: {path}")
            path.mkdir(parents=True, exist_ok=True)
        f = open("/usr/home/judge/hw4/musical-potato/api/json","w+")
        f.close()

    def delete(self,filename):
        self.dic[filename] = 0
        print(self.dic)
        for j in range(0,config.NUM_DISKS):
            try:
                os.remove(str(self.block_path[j]) + '/' + filename)
            except:
                pass
        pass

    async def file_integrity(self, filename: str) -> bool:
        # check exists
        print(f"check filename : {filename}")
        for i in range(0,config.NUM_DISKS):
            onlyfiles = [f for f in listdir(str(self.block_path[i]) + '/') if isfile(join(str(self.block_path[i]) + '/', f))]
            print(f"{i} in file_integrity : ")
            print(onlyfiles)
            print()
            if filename not in onlyfiles:
                self.delete(filename)
                return False

        # check size
        size = -1
        for j in range(0,config.NUM_DISKS):
            file_stats = os.stat(str(self.block_path[j]) + '/' + filename)
            if size == -1:
                size = file_stats.st_size
            else:
                if size != file_stats.st_size:
                    self.delete(filename)
                    return False
        # check xor
        xor = -1
        for j in range(0,config.NUM_DISKS - 1):
            f = open(str(self.block_path[j]) + '/' + filename,"rb")
            if xor == -1:
                xor = f.read()
            else:
                t = f.read()
                xor = self.encrypt1(xor,t)
            f.close()
        f = open(str(self.block_path[config.NUM_DISKS - 1]) + '/' + filename,"rb")
        t = f.read()
        f.close()
        if t != xor:
            self.delete(filename)
            return False

        return True
        
        """TODO: check if file integrity is valid
        file integrated must satisfy following conditions:
            1. all data blocks must exist (v)
            2. size of all data blocks must be equal (v)
            3. parity block must exist 
            4. paricty verify must success

        if one of the above conditions is not satisfied
        the file does not exist
        and the file is considered to be damaged
        so we need to delete the file
        """

    def encrypt1(self,var, key):
        return bytes(a ^ b for a, b in zip(var, key))

    async def create_file(self, file: UploadFile) -> schemas.File:
        # TODO: create file with data block and parity block and return it's schema
        try : 
            print("content",flush=True)
            content  = file.file.read()
            print("size",flush=True)
            size = len(content)
            print(f"size : {size}",flush=True )
            n = config.NUM_DISKS - 1
            moreLenDisk = size % n
            cursor = 0
            print("filename",flush=True)
            name = file.filename
            print(f"filename : {name}",flush=True)
            self.dic[name] = 1
            if moreLenDisk != 0:
                print("in if",flush=True)
                base = int(size / n)
                xor = 0
                print(f"in first for",flush=True)
                for i in range(0,moreLenDisk):
                    print(f"in for i : {i}",flush=True)
                    f = open(str(self.block_path[i]) + '/' + file.filename,"wb+")
                    for j in range(0,base + 1):
                        f.write(content[cursor + j:cursor + j + 1])
                    if i == 0:
                        xor = content[cursor:cursor+base+1]
                    else :
                        xor = self.encrypt1(xor,content[cursor:cursor+base+1])
                    cursor += base + 1 
                    f.close()
                print(f"in second for",flush=True)
                for i in range(moreLenDisk,n):
                    print(f"in for i : {i}",flush=True)
                    f = open(str(self.block_path[i]) + '/' + file.filename,"wb+")
                    for j in range(0,base):
                        f.write(content[cursor + j:cursor+j+1])
                    f.write(bytes(1))
                    xor = self.encrypt1(xor,content[cursor:cursor+base] + bytes(1))
                    cursor += base
                    f.close()
                print(f"in last open",flush=True)
                f = open(str(self.block_path[config.NUM_DISKS - 1]) + '/' + file.filename,"wb+")
                f.write(xor)
                f.close()
                print(f"end last open",flush=True)
            else:
                print("in else",flush=True)
                base = int(size / n)
                xor = 0
                for i in range(0,n):
                    print(f"in for i : {i}",flush=True)
                    f = open(str(self.block_path[i]) + '/' + file.filename,"wb+")
                    for j in range(0,base):
                        f.write(content[cursor + j:cursor+ j + 1])
                    print("in xor",flush=True)
                    if i == 0:
                        xor = content[cursor:cursor+base]
                    else :
                        xor = self.encrypt1(xor,content[cursor:cursor+base])
                    cursor += base
                    f.close()
                print(f"in last open",flush=True)
                f = open(str(self.block_path[config.NUM_DISKS - 1]) + '/' + file.filename,"wb+")
                f.write(xor)
                f.close()
                print(f"end last open",flush=True)
        except Exception as e:
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
        print("start create file",flush = True)
        print(f"nane : {name}",flush = True)
        print(f"size : {size}",flush = True)
        print(f"checksum : {hashlib.md5(content).hexdigest()}",flush = True)
        if file.content_type == None:
            content_type = ''
        else:
            content_type = file.content_type 
        print(f"content_type : {file.content_type}",flush = True)
        answer = schemas.File(
            name=name,
            size=size,
            checksum=hashlib.md5(content).hexdigest(),
            content=base64.b64encode(content),
            #content=123,
            content_type=content_type,
        )
        print("end create file",flush = True)
        print(f"file : {answer}",flush = True)
        return answer
        



    async def retrieve_file(self, filename: str) -> bytes:
        # TODO: retrieve the binary data of file
        self.dic[filename] = 2
        a = -1
        for i in range(0,config.NUM_DISKS - 1):
            f = open(str(self.block_path[i]) + '/' + filename,"rb")
            t = f.read()
            space = bytes(1)
            if t[-1:] == space:
                t = t[0:-1]
            if a == -1:
                a = t
            else:
                a = a + t[:]
            f.close()
        # self.checkfile(filename+'retrieve',a)
        return a

    async def update_file(self, file: UploadFile) -> schemas.File:
        # TODO: update file's data block and parity block and return it's schema
        self.delete(file.filename)
        return await self.create_file(file)

    async def delete_file(self, filename: str) -> bool:
        self.delete(filename)
        return True
        # TODO: delete file's data block and parity block
        pass

    async def fix_block(self, block_id: int) -> None:
        d = {}
        print("start fix",flush = True)
        for i in range(0,config.NUM_DISKS):
            onlyfiles = [f for f in listdir(str(self.block_path[i]) + '/') if isfile(join(str(self.block_path[i]) + '/', f))]
            for j in onlyfiles:
                if j not in d:
                    d[j] = 1
                else:
                    d[j] += 1
        # for i in d:
        #     if d[i] != config.NUM_DISKS:
        #         filename = i
        #         break
        # return
        
        # TODO: fix the broke block by using rest of block
        str(self.block_path[block_id].mkdir(parents=True, exist_ok=True))
        for i in d:
            filename = i
            xor = -1
            for i in range(0,config.NUM_DISKS):
                if i == block_id:
                    continue
                f = open(str(self.block_path[i]) + '/' + filename,"rb")
                if xor == -1:
                    xor = f.read()
                else:
                    t = f.read()
                    xor = self.encrypt1(xor,t)
                f.close()

            f = open(str(self.block_path[block_id]) + '/' + filename,"wb+")
            f.write(xor)
            f.close()
        print("finish fix",flush = True)


storage: Storage = Storage(is_test="pytest" in sys.modules)
