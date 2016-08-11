#!/usr/bin/env python3
import requests
import random
import m3u8

class TwitchData:               
    USHER_API = 'http://usher.twitch.tv/api/channel/hls/{channel}.m3u8?'+\
                'player=twitchweb&token={token}&sig={sig}&$allow_audio_o'+\
                'nly=true&allow_source=true&type=any&p={random}'
    TOKEN_API = 'http://api.twitch.tv/api/channels/{channel}/access_token'
          
    def __init__(self, streamername):
        self.token_url = TwitchData.TOKEN_API.format(channel=streamername)
        self.token_data = requests.get(self.token_url)
        self.usher_url = TwitchData.USHER_API.format(
                                channel=streamername,
                                sig=self.token_data.json()["sig"], 
                                token=self.token_data.json()["token"],
                                random=random.randint(0,1E7))
        self.usher_data = requests.get(self.usher_url)
        self.m3u8 = m3u8.loads(self.usher_data.text)