import os
import argparse
import configparser

if __name__ == "__main__":
    # args init
    parser = argparse.ArgumentParser(description="Config for boj app")
    parser.add_argument(
        "-p", "--path", help="location to store the BOJ problems", metavar="[PATH]", required=True, dest="path")
    parser.add_argument("-T", "--tier-dir",
                        help="티어 디렉토리를 생성합니다.", action="store_true",dest="tierdir")
    parser.add_argument("-n", "--no-tier",
                        help="문제 디렉토리에 티어를 표시하지 않습니다.", action="store_true",dest="notier")
    parser.add_argument(
        "-r", "--readme", help="readme파일을 생성합니다.", action="store_true",dest="readme")
    parser.add_argument("-t", "--testdata",
                        help="testdata를 생성합니다.", action="store_true",dest="testdata")
    args = parser.parse_args()
    
    # import bs4
    try:
        import bs4
    except ImportError:
        import subprocess
        subprocess.check_call(
            ["python", '-m', 'pip', 'install', 'beautifulsoup4'])

    # boj path
    if not os.path.isdir(args.path):
        print(f"{args.path} is not exist")
        print(f"디렉토리를 생성하시겠습니까? (Y/N)")
        print(">> ",end="")
        userInput = input()
        if userInput not in ["Y", "y", "YES", "yes"]:
            print("셋팅을 종료합니다.")
            exit(1)
        os.makedirs(args.path)

    # config path settings
    configPath = os.path.join(os.getenv("HOME"),".config/boj/")
    if os.path.isdir(configPath):
        print(f"{configPath} is exist")
        print("설정을 초기화 하시겠습니까? (Y/N)")
        print(">> ",end="")
        userInput = input()
        if userInput not in ["Y", "y", "YES", "yes"]:
            print("설정을 변경하지 않았습니다.")
            exit(0)
    else:
        os.makedirs(configPath)
    configFile = os.path.join(configPath,"config.ini")
    
    # set config  
    properties = configparser.ConfigParser()
    properties.set("DEFAULT","bojpath",args.path)
    properties.set("DEFAULT","tierdir","YES" if args.tierdir else "NO")
    properties.set("DEFAULT","notier","YES" if args.notier else "NO")
    properties.set("DEFAULT","readme","YES" if args.readme else "NO")
    properties.set("DEFAULT","testdata","YES" if args.testdata else "NO")
    with open(configFile,"w")as f:
        properties.write(f)