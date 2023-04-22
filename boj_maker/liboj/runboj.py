import os
import sys
import requests
import io
import configparser
import subprocess
import time
from bs4 import BeautifulSoup

TYPES = [".cpp", ".c", ".py"]


class RunError(Exception):
    pass


class RunBoj:
    def __init__(self, args):
        self.name = args.name
        self.noCheck = args.noCheck
        self.one = args.one
        self.pro_num = args.pro_num
        self.repeat = args.repeat
        self.set_config()
        self.get_pro_dir()
        self.get_pro_file()
        try:
            while True:
                try:
                    self.compile()
                    self.get_testdata()
                    self.run_code()
                    if self.repeat:
                        self.get_change()
                        continue
                except RunError:
                    pass
                break
        except KeyboardInterrupt:
            print("exit by key")

    def set_config(self):
        home = os.getenv("HOME")
        configPath = os.path.join(home, ".config/boj/config.ini")
        properties = configparser.ConfigParser()
        properties.read(configPath)
        self.bojPath = properties["DEFAULT"]["bojpath"]
        self.tierdir = properties["DEFAULT"]["tierdir"]
        self.notier = properties["DEFAULT"]["notier"]
        self.readme = properties["DEFAULT"]["readme"]
        self.testdata = properties["DEFAULT"]["testdata"]

        if not os.path.isdir(self.bojPath):
            print(f"{self.bojPath} does not exist")
            print("Create the directory and retry")
            print(f"or modify {configPath}")
            exit(1)

    def get_pro_dir(self):
        self.tierPath = self.bojPath
        self.proPath = None

        def find_pro_title(path):
            pro_dir = os.listdir(path)
            for title in pro_dir:
                if str(self.pro_num) in title:
                    self.proPath = os.path.join(self.tierPath, title)

        if self.tierdir == "YES":
            tiers = os.listdir(self.bojPath)
            for tier in tiers:
                self.tierPath = os.path.join(self.bojPath, tier)
                find_pro_title(os.path.join(self.bojPath, tier))
        else:
            find_pro_title(self.bojPath)
        if not self.proPath:
            print(f"{self.pro_num}번 문제를 찾을 수 없습니다.")
            exit(1)

    def get_pro_file(self):
        fileList = os.listdir(self.proPath)
        fileList = [
            file for file in fileList for type in TYPES if file.endswith(type)]
        if not fileList:
            print(f"'{self.proPath}'에 실행 가능한 파일이 없습니다.")
            exit(1)
        if self.name:
            fileList = [file for file in fileList if self.name in file]
            if not fileList:
                print(f"'{self.proPath}'에 '{self.name}'파일이 존재하지 않습니다.")
                exit(1)
        if len(fileList) > 1:
            userIn = 0
            for i, file in enumerate(fileList):
                print(f"{i+1}: {file}")
            while not 1 <= userIn <= len(fileList):
                try:
                    print("실행 할 파일을 선택하세요 >> ", end="")
                    userIn = int(input())
                except ValueError:
                    continue
            self.file = fileList[userIn-1]
        else:
            self.file = fileList[0]

    def compile(self):
        self.fileType = self.file.split(".")[-1]
        if self.fileType in ["cpp", "c"]:
            output = "a.out"
            os.chdir(self.proPath)
            result = subprocess.run(
                ["g++", f"./{self.file}", "-o", f"{output}", "-fdiagnostics-color=always"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print(result.stderr.decode("utf-8"), end="")
                raise RunError
            self.output = os.path.join(self.proPath, output)
        elif self.fileType in ["py"]:
            self.output = self.file

    def get_testdata(self):
        self.inputs = []
        self.outputs = []
        testFile = os.path.join(self.proPath, "testdata.txt")
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
                        self.inputs.append(input)
                    if "output>" in a:
                        output = ""
                        while True:
                            a = f.readline()
                            if "<end" in a:
                                break
                            output += a
                        self.outputs.append(output)
                    if not a:
                        break
        except FileNotFoundError:
            print(f"'{testFile}'이 존재하지 않습니다.")
            exit(1)
        if len(self.inputs) != len(self.outputs):
            print(f"'{testFile}'에 오류가 있습니다.")
        if self.one:
            self.inputs = [self.inputs[0]]
            self.outputs = [self.outputs[0]]

    def run_code(self):
        i = 1
        try:
            for input, output in zip(self.inputs, self.outputs):
                if self.noCheck:
                    result = subprocess.run(
                        [f"{self.output}"], input=input, text=True, timeout=5)
                    if result.returncode != 0:
                        if result.returncode == -11:
                            print("Segmentation fault")
                        else:
                            print(f"'{result.returncode}' error")
                else:
                    start = time.time()
                    result = subprocess.run(
                        [f"{self.output}"], input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                    end = time.time() - start
                    if result.stdout == output:
                        print(f"{i}: success {format(end*1000,'.3f')}ms")
                    else:
                        print(f"{i}: fail")
                        print("need:")
                        print(output)
                        print("output:")
                        print(result.stdout)
                    i += 1
        except subprocess.TimeoutExpired:
            print("timed out after 5 sec")

    def get_change(self):
        before = os.path.getmtime(self.file)
        while True:
            time.sleep(0.1)
            after = os.path.getmtime(self.file)
            if before != after:
                break
