import os
import asyncio
import logging
from liboj.config import Config
from liboj.parser import Parser
from liboj.gpt import html2md, NoApikey

RANK = ["I", "II", "III", "IV", "V"]
TYPES = [("description", "문제 설명"), ("input", "입력"),
         ("output", "출력"), ("limit", "제한")]

logger = logging.getLogger(__name__)


async def setReadme(parser: Parser, file: str, gpt: bool) -> str:
    result = ""
    logger.info("creating readme...")

    def insert(content: str):
        nonlocal result
        result += content
        result += "\n\n"

    insert(f"# [{parser.tier} {RANK[parser.rank-1]}] {parser.title}")
    insert(
        f"[문제 링크](https://www.acmicpc.net/problem/{parser.pro_num})")
    insert(f"## 성능 요약")
    if parser.timeText:
        insert(f"{parser.memText}, {parser.timeText}")
    insert(f"## 분류")
    tags = [f"{tag[0]}({tag[1]})" for tag in parser.tag_list]
    insert(", ".join(tags))

    if gpt:
        tasks = []
        for type in TYPES:
            if parser.info[type[0]]:
                task = asyncio.create_task(
                    html2md(type[0], parser.info[type[0]]))
                tasks.append(task)
        try:
            results = await asyncio.gather(*tasks)
        except NoApikey as e:
            logger.warning(e)
            gpt = False
        results = {result[0]: result[1] for result in results}
        logger.info(results)
        for type in TYPES:
            if results.get(type[0]):
                insert(f"## {type[1]}")
                text = results[type[0]]
                insert(text)

    if not gpt:
        for type in TYPES:
            if parser.info[type[0]]:
                insert(f"## {type[1]}")
                text = parser.info[type[0]]
                insert(text)
    with open(file, "w") as f:
        f.write(result)


def getTestdata(parser: Parser) -> str:
    result = ""
    for i in range(len(parser.input)):
        result += "input>\n"
        result += parser.input[i]
        result += "<end\n"
        result += "output>\n"
        result += parser.output[i]
        result += "<end\n\n"
    return result


def run(args) -> None:
    force = args.force
    gpt = args.gpt
    parser = Parser(pro_num=args.pro_num)

    if force:
        logger.warning("force running")
    logger.info(f"title: {parser.title}")

    # set pro dir
    tier_dir = os.path.join(
        Config.bojPath, parser.tier) if Config.tierdir else Config.bojPath
    if not os.path.isdir(tier_dir):
        logger.debug(f"{tier_dir} does not exist")
        logger.info(f"create {tier_dir}")
        os.mkdir(tier_dir)

    pro_dir_name = f"{parser.tier}{parser.rank}-{parser.pro_num}. {parser.title}" if Config.tierOnName else f"{parser.rank}-{parser.pro_num}. {parser.title}"
    pro_dir = os.path.join(tier_dir, pro_dir_name)

    if os.path.isdir(pro_dir):
        logger.info(f"{pro_dir} already exists")
    else:
        os.mkdir(pro_dir)

    # create readme
    readmePath = os.path.join(pro_dir, "README.md")
    if not force and os.path.isfile(readmePath):
        logger.warning(f"'{readmePath}' is exist - run with force")
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            setReadme(parser=parser, file=readmePath, gpt=gpt))

    # create testdata
    testPath = os.path.join(pro_dir, "testdata.txt")
    if not force and os.path.isfile(testPath):
        logger.warning(f"'{testPath}' is exist - run with force")
    else:
        result = getTestdata(parser=parser)
        with open(testPath, "w") as f:
            f.write(result)

    with open(os.path.join(pro_dir, "a.cpp"), "a") as f:
        pass
