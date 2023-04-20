import os
import requests
import configparser
from . import gpt
from bs4 import BeautifulSoup


TIER = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby"]
RANK = ["I", "II", "III", "IV", "V"]
TYPES = [("description", "문제 설명"), ("input", "입력"),
         ("output", "출력"), ("limit", "제한")]


class MakeBoj:
    def __init__(self, args):
        self.force = args.force
        self.pro_num = args.pro_num
        self.gpt = args.gpt
        self.set_config()
        self.get_problem_data()
        self.set_directory()
        self.get_boj_info()
        self.create_files()

        if self.readme == "YES":
            self.create_readme()

        if self.testdata == "YES":
            self.create_testdata()

    def set_config(self):
        home = os.getenv("HOME")
        configPath = os.path.join(home, ".config/boj/config.ini")
        properties = configparser.ConfigParser()
        properties.read(configPath)
        self.bojPath = properties["DEFAULT"]["bojpath"]
        self.tierdir = properties["DEFAULT"]["tierdir"]
        self.notier = properties["DEFAULT"]["notier"]
        self.readme = properties["DEFAULT"]["readme"]
        self.apikey = properties["DEFAULT"]["openai"]
        self.testdata = properties["DEFAULT"]["testdata"]

        if not os.path.isdir(self.bojPath):
            print(f"{self.bojPath} does not exist")
            print("Create the directory and retry")
            print(f"or modify {configPath}")
            exit(1)

    def get_problem_data(self):
        url = "https://solved.ac/api/v3/problem/show"
        headers = {"Content-Type": "application/json"}
        params = {"problemId": self.pro_num}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        self.id = data.get("problemId", 00000)
        self.title = data.get("titleKo", "title")
        self.level = data.get("level", 0)
        tags = data['tags']
        tag_name_list = [tag["displayNames"] for tag in tags]

        self.tag_list = []
        for names in tag_name_list:
            ko = "no result"
            en = "no result"
            for name in names:
                if name["language"] == "ko":
                    ko = name["name"]
                if name["language"] == "en":
                    en = name["name"]
            self.tag_list = [*self.tag_list, [ko, en]]

    def set_directory(self):
        if self.level == 0:
            self.tier = "Unrated"
            self.rank = 0
        else:
            self.tier = TIER[(self.level-1)//5]
            self.rank = (self.level-1) % 5

        tier_dir = self.bojPath if self.tierdir != "YES" else os.path.join(
            self.bojPath, self.tier)
        if not os.path.isdir(tier_dir):
            print(f"{tier_dir} does not exist")
            print(f"create {tier_dir}")
            os.mkdir(tier_dir)

        pro_dir_name = f"{self.rank}-{self.id}. {self.title}" if self.notier == "YES" else f"{self.tier}{self.rank}-{self.id}. {self.title}"
        self.pro_dir = os.path.join(tier_dir, pro_dir_name)

        if os.path.isdir(self.pro_dir):
            print(f"{self.pro_dir} already exists")
            if self.force:
                print(f"Force create")
            else:
                print("Retry with force option")
                exit(1)
        else:
            os.mkdir(self.pro_dir)

    def create_files(self):
        self.readme_path = os.path.join(self.pro_dir, "README.md")
        self.data_path = os.path.join(self.pro_dir, "testdata.txt")
        cfile_path = os.path.join(self.pro_dir, "a.cpp")

        with open(cfile_path, "a") as fp:
            pass

    def get_boj_info(self):
        self.info = {}
        self.input = []
        self.output = []
        url = f"https://www.acmicpc.net/problem/{self.id}"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0Win64x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        for type in TYPES:
            div_tag = soup.select_one(
                f"#problem_{type[0]}").find_all(recursive=False)
            self.info[type[0]] = [str(tag) for tag in div_tag]

        i = 0
        while True:
            i += 1
            testIn = soup.select_one(f"#sample-input-{i}")
            testOut = soup.select_one(f"#sample-output-{i}")
            if not testIn or not testOut:
                break
            txtIn = testIn.text
            txtOut = testOut.text
            self.input.append(txtIn)
            self.output.append(txtOut)

    def create_readme(self):
        result = ""

        def insert(content: str):
            nonlocal result
            result += content
            result += "\n\n"

        insert(f"# [{self.tier} {RANK[self.rank-1]}] {self.title}")
        insert(f"[문제 링크](https://www.acmicpc.net/problem/{self.id})")
        insert(f"### 성능 요약")
        insert(f"### 분류")
        tags = [f"{tag[0]}({tag[1]})" for tag in self.tag_list]
        insert(", ".join(tags))

        for type in TYPES:
            if self.info[type[0]]:
                insert(f"### {type[1]}")
                for detail in self.info[type[0]]:
                    insert(detail)

        if self.gpt:
            try:
                print("readme 수정 중...")
                messages = []
                messages.append(gpt.make_message(
                    content="I am a machine translator and I output only the results in markdown based on the user's requested content.", role="system"))
                messages.append(gpt.make_message(
                    content=f"{result}\n\nConvert the HTML parts in the file to Markdown, but do not change level of # tags."))
                result = gpt.chat_comple(apikey=self.apikey, message=messages)
            except gpt.NoApikey as e:
                print(e)

        with open(self.readme_path, "w") as f:
            f.write(result)

    def create_testdata(self):
        result = ""

        for i in range(len(self.input)):
            result += "input>\n"
            result += self.input[i]
            result += "<end\n"
            result += "output>\n"
            result += self.output[i]
            result += "<end\n\n"

        with open(self.data_path, "w") as fp:
            fp.write(result)
