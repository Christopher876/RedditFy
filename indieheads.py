#!/usr/bin/env python
import requests
import csv
import time
import spotipy
import spotipy.util as util
from bs4 import BeautifulSoup


url = "https://old.reddit.com/r/indieheads/top/"
# Headers to mimic a browser visit
headers = {'User-Agent': 'Mozilla/5.0'}

# Returns a requests.models.Response object
page = requests.get(url, headers=headers)

soup = BeautifulSoup(page.text, 'html.parser')

scope = 'playlist-modify-public'
username = '99kylel'


token = util.prompt_for_user_token(username,scope,client_id='',client_secret='',redirect_uri='http://localhost/')


if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
        

    albumTitles = []
    trackTitles = []

    trackLinks = []

    for data in soup.find_all('p', class_='title'):
        for a in data.find_all('a'):

            #spotify album link
            if 'spotify.com/album' in a.get('href'):
                temp = []
                temp = sp.album_tracks(a.get('href'))

                #temporary fix, issue when non-released album posted
                try:
                    test = temp['tracks']
                except KeyError:
                    continue
           
                for s in temp['tracks']['items']:
                    count = 0;
                    if(len(trackLinks)<100 and count<10):
                        trackLinks.append(s['id'])
                        count = count+1

            #spotify track link
            elif 'spotify.com/track' in a.get('href'):
                trackLinks.append(a.get('href'))


            #Album without spotify link
            elif '[FRESH ALBUM]' in a.text:
                x = a.text
                search = sp.search(x[13:], limit = 1, offset = 0, type = 'album', market = None)
            
                if search['albums']['total'] > 0:
                    for s in search['albums']['items']:
                        temp = []
                        temp = sp.album_tracks(s['id'])

                        #temporary fix, issue when non-released album posted
                        try:
                            test = temp['tracks']
                        except KeyError:
                            continue
           
                        for b in temp['tracks']['items']:
                            count = 0
                            if(len(trackLinks)<100 and count<10):
                                trackLinks.append(b['id']) 
                                count = count+1
                
            #Song without spotify link
            elif '[FRESH]' in a.text:

                x = a.text
                
                search = sp.search(x[7:], limit = 1, offset = 0, type = 'track', market = None)
            
                if search['tracks']['total'] > 0:

                    for s in search['tracks']['items']:
                        if(len(trackLinks)<100):
                            trackLinks.append(s['id'])

          
    existing_tracks = sp.user_playlist_tracks(token,'75svY6VFRSQ1CCXZa6t9Bk')

    #keeps playlist to a max 100 songs
    if((existing_tracks['total']+len(trackLinks))>100):
        dTracks = []
        
        for x in range((existing_tracks['total']+len(trackLinks))-100):
            try:

                dtemp = existing_tracks['items'][x]
                dTracks.append(dtemp['track']['id'])
            except IndexError:
                continue
       
        sp.user_playlist_remove_all_occurrences_of_tracks(username, '75svY6VFRSQ1CCXZa6t9Bk', dTracks, snapshot_id=None)

    uriList = []

    #prevents adding duplicate songs
    existing_tracks = sp.user_playlist_tracks(token,'75svY6VFRSQ1CCXZa6t9Bk')
    dupCheck = []
    for x in existing_tracks['items']:
        dupCheck.append(x['track']['id'])


    for c in trackLinks:

        t = sp.track(c).get('uri')[14:]
        if t not in dupCheck:
            uriList.append(t)



    if uriList: 
        results = sp.user_playlist_add_tracks(username, '75svY6VFRSQ1CCXZa6t9Bk', uriList)
        print("New songs have been added to r/indieheads")
    else:
        print("Nothing new to add to playlist")


else:
    print("Can't get token for", username)
