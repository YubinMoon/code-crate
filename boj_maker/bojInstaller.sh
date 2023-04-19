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
# Set the command name. 아직 안만듬
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

curl -L -o /tmp/boj.tar.gz https://limeskin.kro.kr/files/boj.tar.gz

if [ $? -ne 0 ]; then
    echo "Failed to download the file."
    exit 1
fi

tar xzf /tmp/boj.tar.gz -C /tmp/

/usr/bin/python /tmp/setting.py $args 2> /dev/null

if [ $? -ne 0 ]; then
    echo "Exiting the downloader."
    exit 1
fi


rm -r ${HOME}/.local/bin/liboj
mv /tmp/liboj /tmp/boj ${HOME}/.local/bin/
chmod +x ${HOME}/.local/bin/boj