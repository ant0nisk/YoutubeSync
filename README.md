# YoutubeSync

YoutubeSync will synchronise your iTunes or Rhythmbox Playlists with your Youtube Channel. Generate the configuration files and select the Playlists you want to sync. 

All the Youtube Playlists will be Private.

## Features
- Easy to use and one-time setup
- Use with *cron jobs* and have automatic syncs with your Youtube Playlists
- Option to Auto-delete Youtube playlists if you remove them from your Library
- Uses OAuth-2.0 for maximum security of the End-User
- Compatibility: Python 2 and 3

## Usage
To run YoutubeSync just run this on your Terminal:
`python YoutubeSync.py`

You can see the help like this: `python YoutubeSync.py --help`

The first run will ask you to create a configuration file. The default location for a configuration file is at *~/Documents/.ytSync.conf*. However, you can specify the location of your configuration file when you create it.

To use a configuration file which isn't located at the default location, do as follows: `python YoutubeSync.py /path/to/configuration_file.conf`

On the first run, you will also get a OAuth prompt. It should open a Google Login page, and once you login and authorize the App, the OAuth response will be fetched automatically and saved to the same directory as YoutubeSync.

## Setup
### Dependency Installation
To install the dependencies that YoutubeSync needs, run `sh install_dependencies.sh`. 

(You will need root priviledges, so you will probably need to prepend *sudo* to that command).

### Google API Keys and OAuth
You need to create a Project on the [Google Developers](https://console.developers.google.com) console. Follow these steps:
1) Enable the Youtube-Data-API.
2) Go to Credentials and create an API Key for YoutubeSync
3) Create OAuth Client ID, for Application-Type: *Other*.

You will need to **download the OAuth Credentials** JSON file to the same directory as YoutubeSync and save it as *client_secrets.json*. 
You should also edit YoutubeSync&#46;py and set the API Key at the `G__gleAPIKey` variable. 

## Notes & Warnings
- Please note that if you have a Playlist on Youtube with the **same** name on your Music Library, **IT WILL BE OVERWRITTEN**. 
- If you remove a song from your local Playlist, it will be removed from the Youtube Playlist.
- Not all songs can be found. This means that sometimes the Youtube Playlists might have less songs than your iTunes or Rhythmbox playlist. The script will warn you about those songs.
- For insurance reasons, the sync process works one way. If you add/remove a song in your Youtube Playlist, it won't be added or removed on your local Playlist.
- If you add a song on the Youtube playlist, it won't be downloaded to your computer. *This is to prevent piracy.*
- YoutubeSync is under heavy testing. Please test it yourself before you make any automated syncs to your Youtube channel.

## TODO
- Option to set the type of a synced Youtube Playlist: Not only *Private*, but also *Unlisted* or *Public*. 

## HOWTO
You can find a simple tutorial on how to set up YoutubeSync with `cron` to have automated syncs [here...](http://inatago.com/betalog/youtube_sync.html)

## License
    Copyright 2016 Antonios Katzourakis

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
 
      http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

