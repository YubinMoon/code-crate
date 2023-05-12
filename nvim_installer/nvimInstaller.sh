#!/bin/bash

# setting neovim
cd ~
curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim.appimage
chmod u+x nvim.appimage
mkdir -p .local/bin/
cp nvim.appimage .local/nvim

# setting nvcahd
git clone https://github.com/NvChad/NvChad ~/.config/nvim --depth 1 && nvim
