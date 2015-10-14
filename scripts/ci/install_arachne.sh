#!/bin/sh
set -e
# check to see if arachne-pnr folder is empty
if [ ! -d "$HOME/arachne-pnr/bin/" ]; then
  git clone https://github.com/cseed/arachne-pnr $HOME/arachne-pnr
  cd $HOME/arachne-pnr
  make
else
  echo 'Using cached directory.';
fi
