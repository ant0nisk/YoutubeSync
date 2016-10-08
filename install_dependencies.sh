#!/bin/bash

#
# Installs the necessary Python dependencies for YoutubeSync.
# Compatible with Mac OS and Linux
#
# LICENSE: 
# Copyright 2016 Antonios Katzourakis
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
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
