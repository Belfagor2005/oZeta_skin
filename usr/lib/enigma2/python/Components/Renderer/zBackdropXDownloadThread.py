#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import requests
import socket
import sys
import threading
import json
from Components.config import config
global my_cur_skin

PY3 = (sys.version_info[0] == 3)
try:
    if PY3:
        from urllib.parse import quote
        import html
        html_parser = html
    else:
        from urllib2 import quote
        from HTMLParser import HTMLParser
        html_parser = HTMLParser()
except:
    pass

try:
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
except:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass

isz = "original"
'''
isz = "w780"
"backdrop_sizes": [
      "w45",
      "w92",
      "w154",
      "w185",
      "w300",
      "w500",
      "w780",
      "w1280",
      "w1920",
      "original"
    ]
'''
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
# thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
thetvdbkey = "acbe31f8-f39a-4910-9b45-2c1d01c38478"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')

if os.path.isdir("/tmp"):
    pathLoc = "/tmp/infos/"
else:
    pathLoc = "/tmp/infos/"
if not os.path.exists(pathLoc):
    os.mkdir(pathLoc)

try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
        if os.path.exists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
        if os.path.exists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
except:
    my_cur_skin = False


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


class zBackdropXDownloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        adsl = intCheck()
        if not adsl:
            return

    def search_tmdb(self, dwn_backdrop, title, shortdesc, fulldesc, channel=None):
        try:
            fd = "{}\n{}\n{}".format(title, shortdesc, fulldesc)
            srch = "multi"
            year = None
            url_tmdb = ""
            backdrop = None
            checkMovie = ["film", "movie", "фильм", "кино", "ταινία", "película", "cinéma", "cine", "cinema", "filma"]
            for i in checkMovie:
                if i in fd.lower():
                    srch = "movie"
                    break
            '''
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
            '''
            try:
                pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
                pattern = re.findall('\d{4}', pattern[0])
                year = pattern[0]
            except:
                year = None
                pass

            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&include_adult=true&query={}".format(srch, tmdb_api, quote(title))
            if year:
                # url_tmdb += "&year={}".format(year)
                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&primary_release_year={}&include_adult=true&query={}".format(srch, tmdb_api, str(year), quote(title))
            if lng:
                url_tmdb += "&language={}".format(lng)
            backdrop = requests.get(url_tmdb).json()['results'][0]['backdrop_path']  # backdrop = json.load(urlopen(url_tmdb))['results'][0]['backdrop_path']
            if backdrop != 'null':
                url_backdrop = "https://image.tmdb.org/t/p/{}{}".format(str(isz), backdrop)
                try:
                    open(dwn_backdrop, 'wb').write(requests.get(url_backdrop, stream=True, allow_redirects=True).content)
                    return True, "[SUCCESS : tmdb] {} => {} => {}".format(title, url_tmdb, url_backdrop)
                except Exception as e:
                    return False, "[Error : tmdb] {} => {} => {} ({})".format(title, url_tmdb, url_backdrop, str(e))
            else:
                return False, "[ERROR : tmdb] {} => {} (None)".format(title, url_tmdb)
        except Exception as e:
            if os.path.exists(dwn_backdrop):
                os.remove(dwn_backdrop)
            return False, "[ERROR : tmdb] {} => {} ({})".format(title, url_tmdb, str(e))

    def search_molotov_google(self, dwn_backdrop, title, shortdesc, fulldesc, channel=None):
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
            backdrop = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
            if backdrop.find("molotov"):
                backdrop = re.sub('\d+x\d+', re.sub(',', 'x', isz), backdrop)
                url_backdrop = "https://{}".format(backdrop)
                try:
                    open(dwn_backdrop, 'wb').write(requests.get(url_backdrop, stream=True, allow_redirects=True).content)
                    return True, "[SUCCESS : molotov-google] {} => {} => {}".format(title, url_tmdb, url_backdrop)
                except Exception as e:
                    return False, "[SUCCESS : molotov-google] {} => {} => {} ({})".format(title, url_tmdb, url_backdrop, str(e))
            else:
                return False, "[ERROR : molotov-google] {} => {} (not in molotov site)".format(title, url_tmdb)
        except Exception as e:
            if os.path.exists(dwn_backdrop):
                os.remove(dwn_backdrop)
            return False, "[ERROR : molotov-google] {} => {} ({})".format(title, url_tmdb, str(e))

    def search_google(self, dwn_backdrop, title, shortdesc, fulldesc, channel=None):
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
            url_tmdb = quote(title)
            if year:
                url_tmdb += "+{}".format(year)
            url_tmdb = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_tmdb)
            ff = requests.get(url_tmdb, stream=True, headers=headers).text
            backdrop = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
            url_backdrop = "https://{}".format(backdrop)
            try:
                open(dwn_backdrop, 'wb').write(requests.get(url_backdrop, stream=True, allow_redirects=True).content)
                return True, "[SUCCESS : google] {} => {} => {}". format(title, dwn_backdrop, url_backdrop)
            except Exception as e:
                print('search_google ', str(e))
                # self.saveBackdrop(dwn_backdrop, url_backdrop)
                return False, "[ERROR : google] {} => {} ({})".format(title, url_backdrop, str(e))
        except Exception as e:
            if os.path.exists(dwn_backdrop):
                os.remove(dwn_backdrop)
            return False, "[ERROR : google] {} => {} ({})".format(title, url_tmdb, str(e))

    def saveBackdrop(self, dwn_backdrop, url_backdrop):
        with open(dwn_backdrop, 'wb') as f:
            f.write(requests.get(url_backdrop, stream=True, allow_redirects=True).content)  # f.write(urlopen(url_backdrop).read())
            f.close()


# tpx = backdropXDownloadThread()
# dwn_backdrop = "test-download-file.jpg"
# print("search_tmdb")
# val, log = tpx.search_tmdb(dwn_backdrop,"The Voice is not a MadMax","","")
# print(log)
# print("search_molotov_google")
# val, log = tpx.search_molotov_google(dwn_backdrop,"The Voice","","")
# print(log)
# print("search_google")
# val, log = tpx.search_google(dwn_backdrop,"The Voice","","","TF1")
# print(log)
