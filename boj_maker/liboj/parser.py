import requests
from liboj.config import Config
from bs4 import BeautifulSoup

TIER = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby"]
RANK = ["I", "II", "III", "IV", "V"]
TYPES = [("description", "문제 설명"), ("input", "입력"),
         ("output", "출력"), ("limit", "제한")]


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, pro_num: int):
        self._pro_num = pro_num
        self._title = None
        self._level = None
        self._tier = None
        self._rank = None
        self._info = None
        self._input = None
        self._output = None
        self._memText = None
        self._timeText = None

    def get_pro_info(self):
        # problem info
        url = "https://solved.ac/api/v3/problem/show"
        headers = {"Content-Type": "application/json"}
        params = {"problemId": self._pro_num}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code >= 300:
            raise ParserError
        data = response.json()
        self._title = data.get("titleKo", "")
        self._level = data.get("level", 0)
        self._tag_list = []

        # set tag
        tags = data['tags']
        tag_name_list = [tag["displayNames"] for tag in tags]
        for names in tag_name_list:
            ko = "no result"
            en = "no result"
            for name in names:
                if name["language"] == "ko":
                    ko = name["name"]
                if name["language"] == "en":
                    en = name["name"]
            self._tag_list = [*self._tag_list, [ko, en]]

        # set tier and rank
        if self._level == 0:
            self._tier = "Unrated"
            self._rank = 0
        else:
            self._tier = TIER[(self._level-1)//5]
            self._rank = 5 - (self._level-1) % 5

    def get_pro_data(self):
        # problem detail
        self._info = {}
        self._input = []
        self._output = []
        url = f"https://www.acmicpc.net/problem/{self._pro_num}"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0Win64x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 300:
            raise ParserError
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        for type in TYPES:
            div_tag = soup.select_one(
                f"#problem_{type[0]}").find_all(recursive=False)
            self._info[type[0]] = "\n".join([str(tag) for tag in div_tag])

        i = 0
        while True:
            i += 1
            testIn = soup.select_one(f"#sample-input-{i}")
            testOut = soup.select_one(f"#sample-output-{i}")
            if not testIn or not testOut:
                break
            txtIn = testIn.text
            txtOut = testOut.text
            self._input.append(txtIn)
            self._output.append(txtOut)

    def get_pro_status(self):
        url = f"https://www.acmicpc.net/status?from_mine=1&problem_pro_num={10989}&user_pro_num={Config.bojID}"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0Win64x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 300:
            raise ParserError
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.select(f"#status-table tbody tr")
        self._memText = ""
        self._timeText = ""
        for line in table:
            if line.select_one(".result-ac"):
                memory = line.select_one(".memory")
                unit = memory.select_one(
                    "span")['class'][0].replace("-text", "")
                size = memory.text
                self._memText = f"{size} {unit}"
                time = line.select_one(".time")
                unit = time.select_one("span")['class'][0].replace("-text", "")
                size = time.text
                self._timeText = f"{size} {unit}"

    @property
    def pro_num(self) -> int:
        return self._pro_num

    @property
    def title(self) -> str:
        if self._title is None:
            self.get_pro_info()
        return self._title

    @property
    def level(self) -> str:
        if self._level is None:
            self.get_pro_info()
        return self._level

    @property
    def tier(self) -> str:
        if self._tier is None:
            self.get_pro_info()
        return self._tier

    @property
    def rank(self) -> int:
        if self._rank is None:
            self.get_pro_info()
        return self._rank

    @property
    def tag_list(self) -> list[str, str]:
        if self._tag_list is None:
            self.get_pro_info()
        return self._tag_list

    @property
    def info(self) -> dict[str, str]:
        if self._info is None:
            self.get_pro_data()
        return self._info

    @property
    def input(self) -> list[str]:
        if self._input is None:
            self.get_pro_data()
        return self._input

    @property
    def output(self) -> list[str]:
        if self._output is None:
            self.get_pro_data()
        return self._output

    @property
    def memText(self) -> str:
        if self._memText is None:
            self.get_pro_status()
        return self._memText

    @property
    def timeText(self) -> str:
        if self._timeText is None:
            self.get_pro_status()
        return self._timeText


if __name__ == "__main__":
    test = Parser(99999)
    print(test.timeText)
    print(test.title)
    print(test.level)
    print(test.tag_list)
