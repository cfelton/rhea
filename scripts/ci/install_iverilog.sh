#!/bin/sh
set -e
# check to see if iverilog folder is empty
if [ ! -d "$HOME/iverilog/bin/" ]; then
    git clone git://github.com/steveicarus/iverilog $HOME/iverilog
    cd $HOME/iverilog
    sh autoconf.sh
    ./configure --prefix=$HOME/iverilog/
    make
    make check
    make install
else
  echo 'Using cached directory.';
fi
