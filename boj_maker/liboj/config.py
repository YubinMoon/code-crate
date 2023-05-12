import os
import configparser
import json

class Config:
    bojPath: str
    tierdir: str
    tierOnName: str
    readme: str
    openai: str
    testdata: str
    bojID: str


home = os.getenv("HOME")
configPath = os.path.join(home, ".config/boj/config.json")
try:
    properties = json.load(open(configPath, "r"))
except FileExistsError:
    print(f"'{configPath}' is not exist")
    exit(1)

Config.bojPath = properties.get("bojPath")
Config.tierdir = properties.get("tierDir")
Config.tierOnName = properties.get("tierOnName")
Config.readme = properties.get("readme")
Config.openai = properties.get("openai")
Config.testdata = properties.get("testdata")
Config.bojID = properties.get("bojID")

for name, value in vars(Config).items():
    if not name.startswith("__") and value is None:
        print(f"Please set '{name}'config at '{configPath}'")

if not os.path.isdir(Config.bojPath):
    print(f"'{Config.bojPath}' does not exist")
    print("Create the directory and retry")
    print(f"or modify config at '{configPath}'")
    exit(1)
