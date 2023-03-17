#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import requests
import socket
import sys
import threading
from Components.config import config
global my_cur_skin

PY3 = (sys.version_info[0] == 3)
try:
    from urllib.parse import quote
except:
    from urllib2 import quote

try:
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
except:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen

try:
    language = config.osd.language.value
    language = language[:-3]
except:
    language = 'en'
    pass
formatImg = "w154"
# w92
# w154
# w185
# w342
# w500
# w780
# formatImg = "original"

apikey = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


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
            poster = None

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
            try:
                pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
                pattern = re.findall('\d{4}', pattern[0])
                year = pattern[0]
            except:
                year = None
                pass

            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&include_adult=true&query={}".format(srch, apikey, quote(title))
            if year:
                url_tmdb += "&year={}".format(year)
            if language:
                url_tmdb += "&language={}".format(language)

            poster = requests.get(url_tmdb).json()
            if poster and poster['results'] and poster['results'][0] and poster['results'][0]['poster_path']:
                url_poster = "https://image.tmdb.org/t/p/{}{}".format(str(formatImg), poster['results'][0]['poster_path'])
                try:
                    open(dwn_poster, 'wb').write(requests.get(url_poster, stream=True, allow_redirects=True).content)
                    # self.savePoster(dwn_poster, url_poster)
                    return True, "[SUCCESS : tmdb] {} => {} => {}".format(title, url_tmdb, url_poster)
                except Exception as e:
                    return False, "[Error : tmdb] {} => {} => {} ({})".format(title, dwn_poster, url_poster, str(e))
            else:
                return False, "[ERROR : tmdb] {} => {} (None)".format(title, url_tmdb)
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : tmdb] {} => {} ({})".format(title, url_tmdb, str(e))

    def search_molotov_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
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
                    # self.savePoster(dwn_poster, url_poster)
                    return False, "[ERROR : molotov-google] {} => {} => {} ({})".format(title, url_tmdb, url_poster, str(e))
            else:
                return False, "[ERROR : molotov-google] {} => {} (not in molotov site)".format(title, url_tmdb)
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : molotov-google] {} => {} ({})".format(title, url_tmdb, str(e))

    def search_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            fd = "{}\n{}".format(shortdesc, fulldesc)
            poster = None
            url_tmdb = ''
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
            poster = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
            url_poster = "https://{}".format(poster)
            try:
                open(dwn_poster, 'wb').write(requests.get(url_poster, stream=True, allow_redirects=True).content)
                return True, "[SUCCESS : google] {} => {} => {}". format(title, url_tmdb, url_poster)
            except Exception as e:
                # print('search_google ', str(e))
                # self.savePoster(dwn_poster, url_poster)
                return False, "[ERROR : google] {} => {} ({})".format(title, url_tmdb, str(e))
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : google] {} => {} ({})".format(title, url_tmdb, str(e))

    def savePoster(self, dwn_poster, url_poster):
        with open(dwn_poster, 'wb') as f:
            f.write(requests.get(url_poster, stream=True, allow_redirects=True).content)  # f.write(urlopen(url_poster).read())
            f.close()
