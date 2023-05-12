import unittest
from unittest.mock import patch, mock_open
from liboj.parser import Parser, ParserError
from dataclasses import dataclass
from liboj.makeboj import run


class ParserTest(unittest.TestCase):
    num_list = [1000, 1864, 16951, 23777]

    def test_get_parser(self):
        print("test_get_parser")
        for num in self.num_list:
            data = Parser(num)
            print(f"{num}'s title : {data.title}")
            self.assertTrue(data.pro_num)
            self.assertTrue(data.title)
            self.assertTrue(data.level)
            self.assertTrue(data.tag_list)
            self.assertTrue(data.info)
            self.assertTrue(data.input)
            self.assertTrue(data.output)
            self.assertTrue(data.memText)
            self.assertTrue(data.timeText)
        with self.assertRaises(ParserError):
            print(f"'abc' is error")
            data = Parser(-1)
            data.title


class MakeBojTest(unittest.TestCase):
    @dataclass
    class TestArgs:
        force: bool
        gpt: bool
        pro_num: int

    @patch('os.mkdir')
    @patch('builtins.open')
    def test_makeboj(self, mock_openm, mock_path):
        print("test_makeboj")
        args = self.TestArgs(False, False, 1000)
        run(args=args)
        args = self.TestArgs(False, True, 1864)
        run(args=args)
        args = self.TestArgs(True, False, 16951)
        run(args=args)
        args = self.TestArgs(True, True, 23777)
        run(args=args)


if __name__ == "__main__":
    unittest.main()
