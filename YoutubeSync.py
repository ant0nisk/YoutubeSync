#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
	-------------
	
	Sync your iTunes or Rhythmbox Playlists with your Youtube Channel. 
	This will create private Playlists with the same songs as the ones found in your Music Library.

	Created by:	Antonis Katzourakis

	Twitter: 	@ant0nisktz
	Web: 		inatago.com

	-------------
"""

try:
	import requests
	import isodate
	from apiclient.discovery import build
	from apiclient.errors import HttpError
	from oauth2client.client import flow_from_clientsecrets
	from oauth2client.file import Storage
	from oauth2client.tools import argparser, run_flow
except:
	print("One or more dependencies were not installed. \nPlease run `python install_dependencies.py` (needs root priviliges)");
	exit(0)

import platform

try:
	import pyItunes
except:
	if platform.system() == "Darwin":
		print("You need to install pyItunes first. \nPlease run `python install_dependencies.py` (needs root priviliges)");
		exit(0)

try:
	import songdetails
except:
	if platform.system() == "Linux":
		print("You need to install songdetails first. \nPlease run `python install_dependencies.py` (needs root priviliges)");
		exit(0)

import httplib2
import time
import os
import shutil
import getpass
import urllib
import sys
import json
from lxml import etree

G__gleAPIKey = '' 								# Your API Key for this Project from console.developers.google.com
CLIENT_SECRETS_FILE = "client_secrets.json" 	# Where your client secrets file for this project is located. (From console.developers.google.com)
_default_language = 'en'						# Default Language

verbose = False	# Don't print a lot of stuff

# = Do not edit the below =
conf = {
	'synchable-playlists': [],
	'delete-removed-playlists': False,
	'previous-playlists': []
}

# Google Python Client Config
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
	message=MISSING_CLIENT_SECRETS_MESSAGE,
	scope=YOUTUBE_READ_WRITE_SCOPE)
	
storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
	flags = argparser.parse_args()
	credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
	  http=credentials.authorize(httplib2.Http()))
	
# Other Global Variables 
Home = ''
LibraryFile = ''
usersPlaylistsCache = {}
configSavePath = ''
configLoadPath = ''
system = platform.system()

if system == "Darwin":
	Home = os.path.join("/",'Users',getpass.getuser())
	LibraryFile = os.path.join(Home, 'Music', 'iTunes', 'iTunes Music Library.xml')
elif system == "Linux":
	Home = os.path.join("/",'home',getpass.getuser())
	LibraryFile = os.path.join(Home, '.local', 'share', 'rhythmbox', 'playlists.xml')
else:
	print("Only Mac and Linux are supported for now...")
	exit(0);

# Python 2 and 3 Compatibility
try:
	input = raw_input
except:
	pass

try:
	 range = xrange
except:
	pass

""" Syncer Functions """
def syncYoutubeAccount():
	# Perform the Synchronisation with Youtube
	global conf
	lbr = getLibrary()
	playlistNames = [p for p in getPlaylists(lbr) if p in conf['synchable-playlists']]
	warning404 = [p for p in conf['synchable-playlists'] if p not in playlistNames]
	if warning404 != [] and conf['delete-removed-playlists'] == False:
		print("Warning: The following playlists are no longer in your Music Library:\n \t- {}".format("\n\t- ".join(warning404)))

	toUploadDict = {}
	notFound = []
	
	for p in playlistNames:
		if verbose: print("Synchronising: {}".format(p))
		playlistTracks = getPlaylistTracks(lbr, p)
		youtubeResults = getVideosForPlaylist(playlistTracks)
		if youtubeResults != -1:
			notFound = youtubeResults[1]
			updateYTPlaylist(p, youtubeResults[0])
		else:
			print("An error occured...")
			return
		
	if conf['delete-removed-playlists']:
		toRemove = [p for p in conf['previous-playlists'] if p not in playlistNames]
		for p in toRemove:
			deleteYTPlaylist(p)
			
	conf['previous-playlists'] = playlistNames
	with open(configSavePath, 'w') as f:
		f.write(json.dumps(conf))
	
	if notFound != []:
		print("Couldn't find the following songs:\n \t- {}".format("\n\t- ".join(notFound)))
		
	print("Synced successfully!")
		
def loadConfig():
	# Load Configuration file
	global configSavePath,conf
	if os.path.isfile(os.path.join(Home,"Documents",".ytSync.conf")):
		configSavePath = os.path.join(Home,"Documents",".ytSync.conf")
		with open(os.path.join(Home,"Documents",".ytSync.conf"), 'r') as f:
			conf = json.loads(f.read())
	elif len(sys.argv) == 1:
		# No Config found
		tmpD = input("No Configuration file found. Do you want to create a new one? Yes/no \t(default: Yes)\n > ")
		if tmpD.lower().startswith('y') or not tmpD:
			newConfig()
	else:
		if os.path.isfile(sys.argv[1]) or configLoadPath:
			configSavePath = sys.argv[1]
			if configLoadPath:
				configSavePath = configLoadPath
				
			with open(sys.argv[1], 'r') as f:
				conf = json.loads(f.read())

def newConfig():
	# Create new Configuration File
	global conf, configSavePath
	lbr = getLibrary()
	playlists = getPlaylists(lbr)
	if len(playlists) == 0:
		print("No Playlists found! Please add a Playlist to your Music Library and try again.")
		exit(0)
	
	for i in range(len(playlists)):
		print("[{}] {}".format(i+1, playlists[i]))
	
	syncables_indx = input("Select which Playlists to Sync: \t(Comma-separated numbers as shown above)\n > ")
	syncables = [playlists[i] for i in range(len(playlists)) if str(i+1) in syncables_indx.replace(" ","").split(",")]
	delete_old = input("Should the Playlists you remove from iTunes be deleted from Youtube? [Yes/No] \t(default: No)\n > ")
	delete_old = delete_old.lower() == "yes"
	
	savePath = input("Where to save the Youtube Sync configuration file? \t(default: {})\n > ".format(os.path.join("~","Documents",".ytSync.conf")))
	if not savePath:
		savePath = os.path.join(Home, "Documents", ".ytSync.conf")
	
	savePath = savePath.replace("~" + os.sep, Home + os.sep)

	conf = {
		'synchable-playlists': syncables,
		'delete-removed-playlists': delete_old,
		'previous-playlists': conf['previous-playlists']
	}
	
	savePath = os.path.abspath(savePath)
	configSavePath = savePath
	with open(savePath, 'w') as f:
		f.write(json.dumps(conf))
	
	print("Configuration File saved!")
			
""" Local Library Functions """
def getLibrary():
	# Get the Music Library
	if system == "Darwin":
		# Get the iTunes Library (in pyItunes Library Object format)
		shutil.copy(LibraryFile, os.path.join("/tmp","__itunes_library__.xml"))
		lbry = pyItunes.Library(str(os.path.join("/tmp","__itunes_library__.xml")))
		return lbry
	
	# Get Rhythmbox Library (in XML format)
	libraryXMLTree = None
	try:
		with open(LibraryFile, 'r') as f:
			libraryXMLTree = etree.fromstring(f.read())	
			return libraryXMLTree
	except Exception,err:
		print("Error while opening Library file: {}".format(err))
		exit(0)
	
def getPlaylists(libraryInstance):
	# Return the Playlist Names
	if system == "Darwin":
		return libraryInstance.getPlaylistNames()

	rtObj = []
	for element in libraryInstance.iter():
		if element.tag == "playlist" and element.get('type') == 'static':
			rtObj.append(element.get('name'))

	return rtObj

def getPlaylistTracks(libraryInstance, playlistName): 
	# Get the songs included in the specified Playlist
	if system == "Darwin":
		return libraryInstance.getPlaylist(playlistName).tracks
	
	rtObj = []
	for element in libraryInstance.iter('playlist'):
		if element.get('name') == playlistName:
			for s in element.iter('location'):
				song = songdetails.scan(urllib.unquote(s.text[7:]))
				if verbose: print("\t- Adding Song: {}".format(song.title))
				if song != None:
					rtObj.append(song)
				else:
					print("Warning: Couldn't get Metadata for Song at Path: {}".format(element.text))

	return rtObj
	
""" Youtube Functions """
def updateYTPlaylist(playlistName, videoObjects):
	# Update a Youtube playlist. If the Playlist doesn't exist, it will be created.
	deleteYTPlaylist(playlistName)
		
	videoIDs = [v['id']['videoId'] for v in videoObjects]
	notFound = insertSongsToYTPlaylist(playlistName, videoIDs)
	
def insertSongsToYTPlaylist(playlistName, videoIDs):
	# Add the specified video IDs to a Playlist. If the Playlist doesn't exist, it will be created.
	uPlaylists = getUserPlaylists()
	if playlistName not in uPlaylists.keys():
		try:
			createYTPlaylist(playlistName)
		except Exception,err:
			print("insertSongsToYTPlaylist Error: {}".format(err))
			return -1
	
	for v_id in videoIDs:
		try:
			youtube.playlistItems().insert(
				part="snippet",
				body=dict(
					snippet={
						"playlistId": uPlaylists[playlistName],
						"resourceId": {
							"kind": "youtube#video",
							"videoId": v_id
						}
					})).execute()
		except Exception,err:
			print("insertSongsToYTPlaylist Error: {}".format(err))
			return -1
	
def deleteYTPlaylist(playlistName):
	# Delete a playlist on Youtube
	uPlaylists = getUserPlaylists()
	if playlistName in uPlaylists.keys():
		youtube.playlists().delete(id=uPlaylists[playlistName]).execute()

def createYTPlaylist(playlistNames):
	# Create the playlists on Youtube
	global usersPlaylistsCache
	uri = "https://www.googleapis.com/youtube/v3/playlists"

	if type(playlistNames) in [str, unicode]:
		playlistNames = [playlistNames]

	for p in playlistNames:
		playlists_insert_response = youtube.playlists().insert(
			part="snippet, status",
			body=dict(
				snippet=dict(
					title=p
				),
				status=dict(
					privacyStatus="private"
				)
			)).execute()
			
		usersPlaylistsCache[p] = playlists_insert_response['id']		
	
def getUserPlaylists():
	# Get the list of the user-generated playlists.
	global usersPlaylistsCache
	if usersPlaylistsCache != {}:
		return usersPlaylistsCache	
		
	if verbose: print("Fetching Youtube Playlists...")

	try:
		playlists = youtube.playlists().list(part='snippet', mine='true').execute()['items']
		for p in playlists:
			usersPlaylistsCache[p['snippet']['title']] = p['id']

		return usersPlaylistsCache
	except Exception,err:
		print("getUserPlaylists Error: {}".format(err))
		return -1
	
def getVideosForPlaylist(songObjects):
	# Search for specific songs on Youtube. songObjects are in the format of pyItunes (or songdetails for Linux), so that attributes such as the artist and the duration are fetched.
	videoObjects = []
	notFound = []

	for s in songObjects:
		nc = True
		if system == "Linux": s.name = s.title; s.length = s.duration.total_seconds()*1000
		if verbose: print("\t\t- Finding Videos for Song: {}".format(s.name))
		results = searchForVideos("{} - {}".format(s.name, s.artist))
		if results == -1:
			return -1
			
		for r in results:
			if abs(r['duration'] - round(s.length/1000.0)) < 10:
				videoObjects.append(r)
				nc = False
				break
		if nc:
			notFound.append("{} - {}".format(s.name, s.artist))
	
	return [videoObjects, notFound]

def getVideoDurations(v_ids):
	# Get Video Durations
	uri = 'https://www.googleapis.com/youtube/v3/videos?id=' + ','.join(v_ids) + '&key=' + G__gleAPIKey + '&part=contentDetails'
	
	try:
		r = requests.get(uri, headers={'Accept-Encoding': 'gzip'})
		return r.json()['items']
	except Exception,err:
		print("getVideoDurations Error: {}".format(err))
		return -1
	
def searchForVideos(name, type='video', language=None): 
	# Return the results of a Video Search on YouTube.
	if type not in ['video', 'playlist', 'channel']:
		type = 'video'
    
	if not language:
		language = _default_language

	uri = 'https://www.googleapis.com/youtube/v3/search?part=snippet&hl=' + language + '&key=' + G__gleAPIKey + '&q=' + urllib.quote(unicode(name).encode('utf8')) + '&type=' + type
	try:
		r = requests.get(uri, headers={'Accept-Encoding': 'gzip'})
		jsonData = r.json()
		if 'items' not in jsonData.keys():		
			print jsonData
			
		items = jsonData['items']
		ids = [g['id']['videoId'] for g in items]
		durations = getVideoDurations(ids)
		if durations == -1:
			return -1
					
		for i in range(len(items)):
			items[i].update({'duration' : isodate.parse_duration(durations[i]['contentDetails']['duration']).total_seconds()})

		return items
	except Exception,err:
		print("searchForVideos Error: {}".format(err))
		return -1
  
if __name__ == "__main__":
	if '--new-config' in sys.argv:
		newConfig()
		exit(0)
	elif '--config' in sys.argv:
		configLoadPath = sys.argv[sys.argv.index("--config")+1]
	elif '--help' in sys.argv or 'help' in sys.argv or '?' in sys.argv:
		print("""Usage: python {0} <config_path>

Other Options:
	--config configuration_path.conf : Load a Configuration File. If not used, the standard configuration location will be used.
	
	--new-config : Start a new Configuration Wizard
	
Example:
	These are equivalent:
		python {0} ytsync.conf
		python {0} --config ytsync.conf
		""".format(__file__))
		exit(0)
		
	loadConfig()
	syncYoutubeAccount()