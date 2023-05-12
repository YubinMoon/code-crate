import os
import re
import asyncio
import logging
import subprocess
from liboj.config import Config
from liboj.runboj import getMatchingDirectories
from liboj.parser import Parser
from liboj.makeboj import setReadme, getTestdata

logger = logging.getLogger(__name__)


async def async_update(proPathList: list, args) -> None:
    gpt = args.gpt
    test = args.test
    
    tasks = []
    for proPath in proPathList:
        num = re.search(r'-(\d+)\.', proPath).group(1)
        readmePath = os.path.join(proPath, "README.md")
        parser = Parser(num)
        task = asyncio.create_task(
            setReadme(parser=parser, file=readmePath, gpt=gpt))
        tasks.append(task)

        if test:
            testdataPath = os.path.join(proPath, "testdata.txt")
            result = getTestdata(parser=parser)
            with open(testdataPath, "w") as f:
                f.write(result)
    await asyncio.gather(*tasks)

def update(args) -> None:
    pro_num = args.pro_num

    if pro_num == "all":
        proPathList = getMatchingDirectories(Config.bojPath, f"[1-5]-[0-9]*")
    else:
        proPathList = getMatchingDirectories(
            Config.bojPath, f"[1-5]-{pro_num}.*")

    if not proPathList:
        logger.error(f"{pro_num}번 문제를 찾을 수 없습니다.")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_update(proPathList=proPathList, args=args))
