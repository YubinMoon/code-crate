import os
import sys
import requests
import io
import configparser
import subprocess
import logging
import time
from bs4 import BeautifulSoup
from liboj.config import Config
from fnmatch import fnmatch

logger = logging.getLogger(__name__)

TYPES = [".cpp", ".c", ".py"]


class RunError(Exception):
    pass


def getMatchingDirectories(directory, pattern) -> str:
    for root, directories, files in os.walk(directory):
        for dir_name in directories:
            if fnmatch(dir_name, pattern):
                dir_path = os.path.join(root, dir_name)
                return dir_path
    return ""


def getTestdata(proPath: str, one: bool) -> tuple[list, list]:
    inputs = []
    outputs = []
    testFile = os.path.join(proPath, "testdata.txt")
    try:
        with open(testFile, "r") as f:
            while True:
                a = f.readline()
                if "input>" in a:
                    input = ""
                    while True:
                        a = f.readline()
                        if "<end" in a:
                            break
                        input += a
                    inputs.append(input)
                if "output>" in a:
                    output = ""
                    while True:
                        a = f.readline()
                        if "<end" in a:
                            break
                        output += a
                    outputs.append(output)
                if not a:
                    break
    except FileNotFoundError:
        logger.error(f"'{testFile}'이 존재하지 않습니다.")
        exit(1)
    if len(inputs) != len(outputs):
        logger.error(f"'{testFile}'에 오류가 있습니다.")
        exit(1)
    if one:
        inputs = [inputs[0]]
        outputs = [outputs[0]]

    return inputs, outputs


def getCompile(proPath: str, file: str) -> str:
    fileType = file.split(".")[-1]
    logger.debug(f"file type: {fileType}")
    if fileType in ["cpp", "c"]:
        output = "a.out"
        os.chdir(proPath)
        result = subprocess.run(
            ["g++", f"./{file}", "-o", f"{output}", "-fdiagnostics-color=always"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(result.stderr.decode("utf-8"), end="")
            raise RunError
        output = os.path.join(proPath, output)
    elif fileType in ["py"]:
        output = os.path.join(proPath, file)
    return output


def getChange(file):
    before = os.path.getmtime(file)
    while True:
        time.sleep(0.1)
        after = os.path.getmtime(file)
        if before != after:
            break


def run(args) -> None:
    name = args.name
    noCheck = args.noCheck
    one = args.one
    proNum = args.pro_num
    repeat = args.repeat

    proPath = getMatchingDirectories(Config.bojPath, f"*-{proNum}.*")
    logger.debug(f"problem path: {proPath}")
    if not proPath:
        logger.error(f"{proNum}번 문제를 찾을 수 없습니다.")
        exit(1)

    # set file
    fileList = os.listdir(proPath)
    fileList = [
        file for file in fileList for type in TYPES if file.endswith(type)]
    if name:
        fileList = [file for file in fileList if name in file]
    if not fileList:
        logger.error(
            f"'{proPath}'에 '{name}'파일이 존재하지 않습니다." if name else f"'{proPath}'에 실행 가능한 파일이 없습니다.")
        exit(1)
    if len(fileList) > 1:
        userIn = 0
        for i, file in enumerate(fileList):
            print(f"{i+1}: {file}")
        while not 1 <= userIn <= len(fileList):
            try:
                userIn = int(input("실행 할 파일을 선택하세요 >> "))
            except ValueError:
                continue
        file = fileList[userIn-1]
    else:
        file = fileList[0]
    logger.debug(f"file name: {file}")

    try:
        while True:
            try:
                runfile = getCompile(proPath=proPath, file=file)
                logger.debug(f"run file: {runfile}")
                inputs, outputs = getTestdata(proPath=proPath, one=one)
                i = 1
                try:
                    for input, output in zip(inputs, outputs):
                        if noCheck:
                            result = subprocess.run(
                                [f"{runfile}"], input=input, text=True, timeout=5)
                            if result.returncode != 0:
                                if result.returncode == -11:
                                    print("Segmentation fault")
                                else:
                                    print(f"'{result.returncode}' error")
                        else:
                            start = time.time()
                            result = subprocess.run(
                                [f"{runfile}"], input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                            end = time.time() - start
                            if result.stdout == output:
                                print(
                                    f"{i}: success {format(end*1000,'.3f')}ms")
                            else:
                                print(f"{i}: fail")
                                print("need:")
                                print(output)
                                print("output:")
                                print(result.stdout)
                            i += 1
                except subprocess.TimeoutExpired:
                    print("timed out after 5 sec")

                if repeat:
                    getChange(file=file)
                    continue
            except RunError:
                pass
            break
    except KeyboardInterrupt:
        logger.info("exit by key")
