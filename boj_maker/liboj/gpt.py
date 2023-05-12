import os
import requests
import configparser
import aiohttp
import re
import logging
from liboj.config import Config

logger = logging.getLogger(__name__)


class NoApikey(Exception):
    def __init__(self, msg) -> None:
        self.msg = msg

    def __str__(self) -> str:
        result = "openai apikey가 없습니다.\n"
        result += f"'{self.msg}'에서 생성 후 config에 등록해 주세요"
        return result


def make_message(content: str, role: str = "user") -> dict[str, str]:
    return {"role": role, "content": content}


def chat_comple(apikey: str, message: list) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apikey}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": message,
        "temperature": 0,
        "top_p": 1,
    }
    result = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if result.status_code == 401:
        m = re.search(
            "https?://(www.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}.[a-z]{2,6}([-a-zA-Z0-9@:%_\+~#()?&/=]*)", result.text)
        raise NoApikey(m.group())
    res = result.json()
    response = res["choices"][0]["message"]["content"]
    return response


async def async_chat_comple(apikey: str, message: list) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apikey}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": message,
        "temperature": 0,
        "top_p": 1,
    }
    async with aiohttp.ClientSession() as client:
        async with client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as result:
            result = requests.post(
                "https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            if result.status_code == 401:
                m = re.search(
                    "https?://(www.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}.[a-z]{2,6}([-a-zA-Z0-9@:%_\+~#()?&/=]*)", result.text)
                raise NoApikey(m.group())
            res = result.json()
            response = res["choices"][0]["message"]["content"]
            return response


async def html2md(type: str, text: str) -> str:
    messages = []
    logger.debug(f"get gpt {text}")
    messages.append(make_message(content="You are a translator AI that converts HTML text into markdown. You translate a given string into markdown without changing or adding the format and content. Do not use #Tag while converting to markdown."))
    messages.append(make_message(
        content=f"{text}"))
    result = await async_chat_comple(apikey=Config.openai, message=messages)
    return type, result


if __name__ == "__main__":
    configPath = os.path.join(os.getenv("HOME"), ".config/boj/config.ini")
    properties = configparser.ConfigParser()
    properties.read(configPath)
    apikey = properties["DEFAULT"]["openai"]
    result = chat_comple(apikey=apikey, message=[make_message(content="안녕?")])
    print(result)
