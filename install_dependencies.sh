#!/bin/bash

#
# Installs the necessary Python dependencies for YoutubeSync.
# Compatible with Mac OS and Linux
#

if [ "$(uname -s)" = "Darwin" ];
then
     pip install pyItunes
else
     pip install mpeg1audio
     pip install git+https://github.com/Ciantic/pytagger/
     pip install git+https://github.com/Ciantic/songdetails/
fi

pip install --upgrade google-api-python-client
pip install --upgrade requests
pip install isodate
