#!/bin/sh
set -e
# check to see if arachne-pnr folder is empty
if [ ! -d "$HOME/arachne-pnr/bin/" ]; then
  git clone https://github.com/cseed/arachne-pnr
  cd arachne-pnr
  make
  cd ..
else
  echo 'Using cached directory.';
fi
