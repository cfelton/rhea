#!/bin/sh
set -e
# check to see if icestorm folder is empty
if [ ! -d "$HOME/icestorm/icepack/" ]; then
  git clone https://github.com/cliffordwolf/icestorm $HOME/icestorm
  cd $HOME/icestorm
  make
else
  echo 'Using cached directory.';
fi
