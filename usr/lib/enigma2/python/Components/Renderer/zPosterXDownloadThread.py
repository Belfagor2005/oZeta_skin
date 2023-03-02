#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from Components.config import config
import os
import re
import requests
import sys
import threading
import socket

global my_cur_skin

PY3 = sys.version_info.major >= 3
try:
    from urllib.parse import quote
except:
    from urllib import quote


try:
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
except:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen


# formatImg = "w92"
# formatImg = "w154"
# formatImg = "w342"
# formatImg = "w500"
# formatImg = "w780"
# formatImg = "original"
formatImg = "w185"

apikey = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


def isMountReadonly(mnt):
    with open('/proc/mounts') as f:
        for line in f:
            line = line.split(',')[0]
            line = line.split()   
            print('line ', line)
            try:
                device, mount_point, filesystem, flags = line
            except Exception as err:
                   print("Error: %s" % err)                    
            if mount_point == mnt:
                return 'ro' in flags            
    return "mount: '%s' doesn't exist" % mnt        

path_folder = "/tmp/poster" 
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        path_folder = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        path_folder = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        path_folder = "/media/mmc/poster"    
else:
    path_folder = "/tmp/poster" 

if not os.path.exists(path_folder):
    os.makedirs(path_folder)
if not os.path.exists(path_folder):    
    path_folder = "/tmp/poster" 


try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                apikey = f.read()
        if os.path.exists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
        if os.path.exists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
except:
    my_cur_skin = False


try:
    from Components.config import config
    language = config.osd.language.value
    language = language[:-3]
except:
    language = 'en'
    pass
print('language: ', language)


def intCheck():
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True


class zPosterXDownloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        adsl = intCheck()
        if not adsl:
            return

    def search_tmdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            fd = "{}\n{}\n{}".format(title, shortdesc, fulldesc)
            srch = "multi"
            year = None
            url_tmdb = ""
            try:
                pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
                pattern = re.findall('\d{4}', pattern[0])
                year = pattern[0]
            except:
                year = None
                pass

            checkMovie = ["film", "movie", "фильм", "кино", "ταινία", "película", "cinéma", "cine", "cinema", "filma"]
            for i in checkMovie:
                if i in fd.lower():
                    srch = "movie"
                    break

            checkTV = ["serial", "series", "serie", "serien", "série", "séries",
                       "serious", "folge", "episodio", "episode", "épisode",
                       "l'épisode", "ep.", "staffel", "soap", "doku", "tv", "talk",
                       "show", "news", "factual", "entertainment", "telenovela",
                       "dokumentation", "dokutainment", "documentary", "informercial",
                       "information", "sitcom", "reality", "program", "magazine", "mittagsmagazin",
                       "т/с", "м/с", "сезон", "с-н", "эпизод", "сериал", "серия",
                       "magazine", "actualité", "discussion", "interview", "débat",
                       "émission", "divertissement", "jeu", "information", "météo", "journal",
                       "talk-show", "sport", "culture", "infos", "feuilleton", "téléréalité",
                       "société", "clips"]
            if srch != "movie":
                for i in checkTV:
                    if i in fd.lower():
                        srch = "tv"
                        break

            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&include_adult=true&query={}".format(srch, apikey, quote(title))
            # id = requests.get(url_tmdb).json()['results'][0]['id']
            # url_tmdb = "https://api.themoviedb.org/3/{}/{}?api_key={}&append_to_response=images".format(srch, int(id), apikey)
            if year:
                url_tmdb += "&year={}".format(year)
            if language:
                url_tmdb += "&language={}".format(language)
            poster = requests.get(url_tmdb).json()['results'][0]['poster_path']
            # url_poster = "https://image.tmdb.org/t/p/{}{}".format(str(formatImg), poster)
            url_poster = "https://image.tmdb.org/t/p/{}{}".format(str(formatImg), poster)
            # url_poster = requests.get(url_tmdb).json()['results'][0]['poster_path']  # poster = json.load(urlopen(url_tmdb))['results'][0]['poster_path']
            if poster:
                try:
                    open(dwn_poster, 'wb').write(requests.get(url_poster, stream=True, allow_redirects=True).content)
                    # url_poster = "https://image.tmdb.org/t/p/w{}{}".format(str(formatImg.split(",")[0]), poster)
                    # self.savePoster(dwn_poster, url_poster)
                    # print('=============11111111=================\n')
                    return True, "[SUCCESS : tmdb] {} => {} => {}".format(title, url_tmdb, url_poster)
                except:
                    # open(dwn_poster, 'wb').write(requests.get(url_poster, stream=True, allow_redirects=True).content)
                    # url_poster = "https://image.tmdb.org/t/p/w{}{}".format(str(formatImg.split(",")[0]), poster)
                    self.savePoster(dwn_poster, url_poster)
                    # print('===========2222222222==================\n')
                    return True, "[SUCCESS : tmdb] {} => {} => {}".format(title, url_tmdb, url_poster)
            else:
                return False, "[ERROR : tmdb] {} => {} (None)".format(title, url_tmdb)
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : tmdb] {} => {} ({})".format(title, url_tmdb, str(e))

    def search_molotov_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        # if intCheck():
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            fd = "{}\n{}".format(shortdesc, fulldesc)
            year = None
            try:
                pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
                pattern = re.findall('\d{4}', pattern[0])
                year = pattern[0]
            except:
                year = None
                pass
            url_tmdb = "site:molotov.tv+" + quote(title)
            if year:
                url_tmdb += "+{}".format(year)
            url_tmdb = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_tmdb)
            ff = requests.get(url_tmdb, stream=True, headers=headers).text
            poster = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
            if poster.find("molotov"):
                poster = re.sub('\d+x\d+', re.sub(',', 'x', formatImg), poster)
                url_poster = "https://{}".format(poster)
                try:
                    open(dwn_poster, 'wb').write(requests.get(url_poster, stream=True, allow_redirects=True).content)
                    return True, "[SUCCESS : molotov-google] {} => {} => {}".format(title, url_tmdb, url_poster)
                except Exception as e:
                    # print('search_molotov_google ', str(e))
                    self.savePoster(dwn_poster, url_poster)
                    return True, "[SUCCESS : molotov-google] {} => {} => {}".format(title, url_tmdb, url_poster)
            else:
                return False, "[ERROR : molotov-google] {} => {} (not in molotov site)".format(title, url_tmdb)
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : molotov-google] {} => {} ({})".format(title, url_tmdb, str(e))

    def search_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        # if intCheck():
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            fd = "{}\n{}".format(shortdesc, fulldesc)
            year = None
            try:
                pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
                pattern = re.findall('\d{4}', pattern[0])
                year = pattern[0]
            except:
                year = None
                pass
            #  url_tmdb = quote(title) + "%20" + quote(channel)
            url_tmdb = quote(title)
            if year:
                url_tmdb += "+{}".format(year)
            #  url_tmdb = url_tmdb + "%20imagesize:" + re.sub(',','x',formatImg)
            url_tmdb = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_tmdb)
            ff = requests.get(url_tmdb, stream=True, headers=headers).text
            poster = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
            url_poster = "https://{}".format(poster)
            try:
                open(dwn_poster, 'wb').write(requests.get(url_poster, stream=True, allow_redirects=True).content)
                return True, "[SUCCESS : google] {} => {} => {}". format(title, url_tmdb, url_poster)
            except Exception as e:
                # print('search_google ', str(e))
                self.savePoster(dwn_poster, url_poster)
                return True, "[SUCCESS : google] {} => {} => {}". format(title, url_tmdb, url_poster)
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : google] {} => {} ({})".format(title, url_tmdb, str(e))

    def savePoster(self, dwn_poster, url_poster):
        with open(dwn_poster, 'wb') as f:
            f.write(requests.get(url_poster, stream=True, allow_redirects=True).content)  # f.write(urlopen(url_poster).read())
            f.close()
