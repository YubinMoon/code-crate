#!/bin/bash

# get env
if [ -f ./.env ]; then
    . .env
else
    echo please set \'.env\' file with \'.env.template\'
    exit 1
fi

# dir check
if [ ! -d "$BOJ_PATH" ]; then
    echo "'$BOJ_PATH' is not exist"
    echo "Please set the directory to save Baekjoon problems"
    exit 1
fi

configPath=$HOME/.config/boj
if [ ! -d $configPath ]; then
    mkdir -p $configPath
fi

cat <<EOF >$configPath/config.json
{
  "bojPath": "$BOJ_PATH",
  "tierDir": $ADD_TIER_DIR,
  "tierOnName": $TIER_ON_PRO_DIR,
  "readme": $README,
  "openai": "$OPENAI_API_KEY",
  "testdata": $TEST_DATAa,
  "bojID": "$BOJ_ID"
}
EOF

if [ -d $HOME/.local/bin/$COMMAND ]; then
    echo \'$HOME/.local/bin/$COMMAND\' is exist as directory
    echo set default command boj
    COMMAND=boj
fi

if [ -d $HOME/.local/bin/liboj ]; then
    rm -r $HOME/.local/bin/liboj
fi

cp -r ./liboj $HOME/.local/bin/
cp ./boj $HOME/.local/bin/$COMMAND
chmod +x $HOME/.local/bin/$COMMAND
