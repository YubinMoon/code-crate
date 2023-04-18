#!/bin/bash

# Set the path where Baekjoon problems will be saved, e.g., /HOME/baekjoon/
bojPath="${HOME}/algorithm/baekjoon/"
# If the value is not 0, tiered directories will not be created.
tierDir=0
# If the value is not 0, the tier will be shown in the problem folder.
noTierOnPro=0
# If the value is not 0, a README file will not be created.
readme=0
# If the value is not 0, testdata will not be generated.
testdata=0
# Set the command name.
command="boj"

if [ ! -d "$bojPath" ]; then
    echo "Please set the directory to save Baekjoon problems"
    exit 1
fi

# Configure settings
args="--path ${bojPath}"
if [ $tierDir = "0" ]; then
    args="${args} --tier-dir"
fi
if [ $noTierOnPro = "0" ]; then
    args="${args} --no-tier"
fi
if [ $readme = "0" ]; then
    args="${args} --readme"
fi
if [ $testdata = "0" ]; then
    args="${args} --testdata"
fi

curl -L https://limeskin.kro.kr/files/setting.py > /tmp/setting.py

if [ $? -ne 0 ]; then
    echo "Failed to download the configuration file."
    exit 1
fi

/usr/bin/python /tmp/setting.py $args 2> /dev/null

if [ $? -ne 0 ]; then
    echo "Exiting the downloader."
    exit 1
fi

if [ ! -d "${HOME}/.local/bin/liboj" ]; then
    echo "${HOME}/.local/bin/liboj does not exist"
    echo "Creating directory"
    mkdir -p ~/.local/bin/liboj
    if [ $? -ne 0 ]; then
        echo "Failed to create the directory."
        exit 1
    fi
fi

curl -L https://limeskin.kro.kr/files/makeboj.py > ${HOME}/.local/bin/liboj/makeboj.py
curl -L https://limeskin.kro.kr/files/boj > ${HOME}/.local/bin/${command}
chmod +x ${HOME}/.local/bin/${command}