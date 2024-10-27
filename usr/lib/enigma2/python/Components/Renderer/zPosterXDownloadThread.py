#!/usr/bin/python
# -*- coding: utf-8 -*-

# edit by lululla 07.2022
# recode from lululla 2023
from __future__ import absolute_import
from Components.config import config
from PIL import Image
from enigma import getDesktop
import os
import re
import requests
import socket
import sys
import threading
import unicodedata
import random
import json

try:
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 0
except ImportError:
    from httplib import HTTPConnection
    HTTPConnection.debuglevel = 0
from requests.adapters import HTTPAdapter, Retry
global my_cur_skin, srch


PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    import html
    html_parser = html
else:
    from HTMLParser import HTMLParser
    html = HTMLParser()


try:
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote_plus
except:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote_plus


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass


def getRandomUserAgent():
    useragents = [
        'Mozilla/5.0 (compatible; Konqueror/4.5; FreeBSD) KHTML/4.5.4 (like Gecko)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20120101 Firefox/35.0',
        'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    ]
    return random.choice(useragents)


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
fanart_api = "6d231536dea4318a88cb2520ce89473b"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


def clean_recursive(regexStr="", replaceStr="", eventTitle=""):
    while True:
        clean_name = re.sub(regexStr, replaceStr, eventTitle)
        if clean_name == eventTitle:
            break
        eventTitle = clean_name
    return clean_name


try:
    if my_cur_skin is False:
        skin_paths = {
            "tmdb_api": "/usr/share/enigma2/{}/apikey".format(cur_skin),
            "omdb_api": "/usr/share/enigma2/{}/omdbkey".format(cur_skin),
            "thetvdbkey": "/usr/share/enigma2/{}/thetvdbkey".format(cur_skin)
        }
        for key, path in skin_paths.items():
            if os.path.exists(path):
                with open(path, "r") as f:
                    value = f.read().strip()
                    if key == "tmdb_api":
                        tmdb_api = value
                    elif key == "omdb_api":
                        omdb_api = value
                    elif key == "thetvdbkey":
                        thetvdbkey = value
                my_cur_skin = True
except Exception as e:
    print("Errore nel caricamento delle API:", str(e))
    my_cur_skin = False


isz = "185,278"
screenwidth = getDesktop(0).size()
if screenwidth.width() <= 1280:
    isz = isz.replace(isz, "185,278")
elif screenwidth.width() <= 1920:
    isz = isz.replace(isz, "342,514")
else:
    isz = isz.replace(isz, "780,1170")


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


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


def dataenc(data):
    if PY3:
        data = data.decode("utf-8")
    else:
        data = data.encode("utf-8")
    return data


class zPosterXDownloadThread(threading.Thread):
    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        threading.Thread.__init__(self)
        self.checkMovie = ["film", "movie", "фильм", "кино", "ταινία",
                           "película", "cinéma", "cine", "cinema",
                           "filma"]
        self.checkTV = ["serial", "series", "serie", "serien", "série",
                        "séries", "serious", "folge", "episodio",
                        "episode", "épisode", "l'épisode", "ep.",
                        "animation", "staffel", "soap", "doku", "tv",
                        "talk", "show", "news", "factual",
                        "entertainment", "telenovela", "dokumentation",
                        "dokutainment", "documentary", "informercial",
                        "information", "sitcom", "reality", "program",
                        "magazine", "mittagsmagazin", "т/с", "м/с",
                        "сезон", "с-н", "эпизод", "сериал", "серия",
                        "actualité", "discussion", "interview", "débat",
                        "émission", "divertissement", "jeu", "magasine",
                        "information", "météo", "journal", "sport",
                        "culture", "infos", "feuilleton", "téléréalité",
                        "société", "clips", "concert", "santé",
                        "éducation", "variété"]

    def search_tmdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            self.dwn_poster = dwn_poster
            print('self.dwn_poster=', self.dwn_poster)
            title_safe = quoteEventName(title)
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&language={lng}&query={title_safe}"
            data = None
            retries = Retry(total=1, backoff_factor=1)
            adapter = HTTPAdapter(max_retries=retries)
            http = requests.Session()
            http.mount("http://", adapter)
            http.mount("https://", adapter)
            headers = {'User-Agent': getRandomUserAgent()}
            response = http.get(url, headers=headers, timeout=(10, 20), verify=False)
            response.raise_for_status()
            if response.status_code == requests.codes.ok:
                try:
                    data = response.json()
                except ValueError as e:
                    print(e)
                    data = None
                self.downloadData2(data)
                return True, "Download avviato con successo"
            else:
                return False, f"Errore durante la ricerca su TMDb: {response.status_code}"
        except Exception as e:
            print('Errore nella ricerca TMDb:', e)
            return False, "Errore durante la ricerca su TMDb"

    def downloadData(self, data):
        try:
            if isinstance(data, bytes):
                print("Decoding bytes to string...")
                data = data.decode('utf-8')
            json_data = json.loads(data)
            self.downloadData2(json_data)
        except Exception as e:
            print("Errore nel processare i dati scaricati:", e, "Tipo di dato:", type(data), "Contenuto:", data)

    def downloadData2(self, data):
        if isinstance(data, bytes):
            print("Decoding bytes to string...")
            data = data.decode('utf-8')
        data_json = data if isinstance(data, dict) else json.loads(data)
        if 'results' in data_json:
            try:
                for each in data_json['results']:
                    media_type = str(each['media_type'])
                    if media_type == "tv":
                        media_type = "serie"
                    if media_type in ['serie', 'movie']:
                        year = ""
                        if media_type == "movie" and 'release_date' in each and each['release_date']:
                            year = each['release_date'].split("-")[0]
                        elif media_type == "serie" and 'first_air_date' in each and each['first_air_date']:
                            year = each['first_air_date'].split("-")[0]
                        title = each.get('name', each.get('title', ''))
                        # new_height = int(isz.split(",")[1])
                        # backdrop = "http://image.tmdb.org/t/p/w1280" + each.get('backdrop_path', '')
                        # poster = "http://image.tmdb.org/t/p/w500" + each.get('poster_path', '')
                        backdrop = "http://image.tmdb.org/t/p/w1280" + each.get('backdrop_path', '')
                        poster = "http://image.tmdb.org/t/p/w500" + each.get('poster_path', '')
                        rating = str(each.get('vote_average', 0))
                        show_title = title
                        if year:
                            show_title = "{} ({})".format(title, year)
                        print('title, poster, backdrop, year, rating, show_title=', title, poster, backdrop, year, rating, show_title)
                        if poster:
                            self.savePoster(self.dwn_poster, poster)
                            if self.verifyPoster(self.dwn_poster):
                                self.resizePoster(self.dwn_poster)
                        return True, "[SUCCESS poster: tmdb] title {} [poster{}-backdrop{}] => year{} => rating{} => showtitle{}".format(title, poster, backdrop, year, rating, show_title)
                return False, "[SKIP : tmdb] Not found"
            except Exception as e:
                print('error=', e)
                if os.path.exists(self.dwn_poster):
                    os.remove(self.dwn_poster)
                return False, "[ERROR : tmdb]"

    def search_tvdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            series_nb = -1
            chkType, fd = self.checkType(shortdesc, fulldesc)
            title_safe = self.UNAC(title)
            year = re.findall(r'19\d{2}|20\d{2}', fd)
            if len(year) > 0:
                year = year[0]
            else:
                year = ''
            title_safe = quoteEventName(title_safe)
            url_tvdbg = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(title_safe)
            url_read = requests.get(url_tvdbg).text
            series_id = re.findall(r'<seriesid>(.*?)</seriesid>', url_read)
            series_name = re.findall(r'<SeriesName>(.*?)</SeriesName>', url_read)
            series_year = re.findall(r'<FirstAired>(19\d{2}|20\d{2})-\d{2}-\d{2}</FirstAired>', url_read)
            i = 0
            for iseries_year in series_year:
                if year == '':
                    series_nb = 0
                    break
                elif year == iseries_year:
                    series_nb = i
                    break
                i += 1
            poster = None
            if series_nb >= 0 and series_id and series_id[series_nb]:
                if series_name and series_name[series_nb]:
                    series_name = self.UNAC(series_name[series_nb])
                else:
                    series_name = ''
                if self.PMATCH(title_safe, series_name):
                    url_tvdb = "https://thetvdb.com/api/{}/series/{}".format(thetvdbkey, series_id[series_nb])
                    if lng:
                        url_tvdb += "/{}".format(lng)
                    else:
                        url_tvdb += "/en"
                    url_read = requests.get(url_tvdb).text
                    poster = re.findall(r'<poster>(.*?)</poster>', url_read)

            if poster and poster[0]:

                url_poster = "https://artworks.thetvdb.com/banners/{}".format(poster[0])
                self.savePoster(dwn_poster, url_poster)
                if self.verifyPoster(dwn_poster):
                    self.resizePoster(dwn_poster)
                return True, "[SUCCESS : tvdb] {} [{}-{}] => {} => {} => {}".format(title_safe, chkType, year, url_tvdbg, url_tvdb, url_poster)
            else:
                return False, "[SKIP : tvdb] {} [{}-{}] => {} (Not found)".format(title_safe, chkType, year, url_tvdbg)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : tvdb] {} => {} ({})".format(title, url_tvdbg, str(e))

    def search_fanart(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            year = None
            url_maze = ""
            url_fanart = ""
            url_poster = None
            id = "-"
            title_safe = quoteEventName(title)
            chkType, fd = self.checkType(shortdesc, fulldesc)
            try:
                if re.findall(r'19\d{2}|20\d{2}', title_safe):
                    year = re.findall(r'19\d{2}|20\d{2}', fd)[1]
                else:
                    year = re.findall(r'19\d{2}|20\d{2}', fd)[0]
            except:
                year = ''
                pass

            try:
                url_maze = "http://api.tvmaze.com/singlesearch/shows?q={}".format(title_safe)
                mj = requests.get(url_maze).json()
                id = (mj['externals']['thetvdb'])
            except Exception as err:
                print('Error:', err)

            try:
                m_type = 'tv'
                url_fanart = "https://webservice.fanart.tv/v3/{}/{}?api_key={}".format(m_type, id, fanart_api)
                fjs = requests.get(url_fanart, verify=False, timeout=5).json()
                try:
                    url = (fjs['tvposter'][0]['url'])
                except:
                    url = (fjs['movieposter'][0]['url'])

                url_poster = requests.get(url).json()
                print('url fanart poster:', url_poster)
                if url_poster and url_poster != 'null' or url_poster is not None or url_poster != '':
                    self.savePoster(dwn_poster, url_poster)
                    if self.verifyPoster(dwn_poster):
                        self.resizePoster(dwn_poster)
                    return True, "[SUCCESS poster: fanart] {} [{}-{}] => {} => {} => {}".format(title_safe, chkType, year, url_maze, url_fanart, url_poster)
                else:
                    return False, "[SKIP : fanart] {} [{}-{}] => {} (Not found)".format(title_safe, chkType, year, url_fanart)
            except Exception as e:
                print(e)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : fanart] {} [{}-{}] => {} ({})".format(title_safe, chkType, year, url_fanart, str(e))

    def search_imdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            url_poster = None
            chkType, fd = self.checkType(shortdesc, fulldesc)
            title_safe = self.UNAC(title)
            title_safe = quoteEventName(title_safe)
            aka = re.findall(r'\((.*?)\)', fd)
            if len(aka) > 1 and not aka[1].isdigit():
                aka = aka[1]
            elif len(aka) > 0 and not aka[0].isdigit():
                aka = aka[0]
            else:
                aka = None
            if aka:
                paka = self.UNAC(aka)
            else:
                paka = ''
            year = re.findall(r'19\d{2}|20\d{2}', fd)
            if len(year) > 0:
                year = year[0]
            else:
                year = ''
            imsg = ''
            url_mimdb = ''
            url_imdb = ''

            if aka and aka != title_safe:
                url_mimdb = "https://m.imdb.com/find?q={}%20({})".format(title_safe, quoteEventName(aka))
            else:
                url_mimdb = "https://m.imdb.com/find?q={}".format(title_safe)
            url_read = requests.get(url_mimdb).text
            rc = re.compile(r'<img src="(.*?)".*?<span class="h3">\n(.*?)\n</span>.*?\((\d+)\)(\s\(.*?\))?(.*?)</a>', re.DOTALL)
            url_imdb = rc.findall(url_read)

            if len(url_imdb) == 0 and aka:
                url_mimdb = "https://m.imdb.com/find?q={}".format(title_safe)
                url_read = requests.get(url_mimdb).text
                rc = re.compile(r'<img src="(.*?)".*?<span class="h3">\n(.*?)\n</span>.*?\((\d+)\)(\s\(.*?\))?(.*?)</a>', re.DOTALL)
                url_imdb = rc.findall(url_read)
            len_imdb = len(url_imdb)
            idx_imdb = 0
            pfound = False

            for imdb in url_imdb:
                imdb = list(imdb)
                imdb[1] = self.UNAC(imdb[1])
                tmp = re.findall(r'aka <i>"(.*?)"</i>', imdb[4])
                if tmp:
                    imdb[4] = tmp[0]
                else:
                    imdb[4] = ''
                imdb[4] = self.UNAC(imdb[4])
                imdb_poster = re.search(r"(.*?)._V1_.*?.jpg", imdb[0])
                if imdb_poster:
                    if imdb[3] == '':
                        if year and year != '':
                            if year == imdb[2]:
                                url_poster = "{}._V1_UY278,1,185,278_AL_.jpg".format(imdb_poster.group(1))
                                imsg = "Found title : '{}', aka : '{}', year : '{}'".format(imdb[1], imdb[4], imdb[2])
                                if self.PMATCH(title_safe, imdb[1]) or self.PMATCH(title_safe, imdb[4]) or (paka != '' and self.PMATCH(paka, imdb[1])) or (paka != '' and self.PMATCH(paka, imdb[4])):
                                    pfound = True
                                    break
                            elif not url_poster and (int(year) - 1 == int(imdb[2]) or int(year) + 1 == int(imdb[2])):
                                url_poster = "{}._V1_UY278,1,185,278_AL_.jpg".format(imdb_poster.group(1))
                                imsg = "Found title : '{}', aka : '{}', year : '+/-{}'".format(imdb[1], imdb[4], imdb[2])
                                if title_safe == imdb[1] or title_safe == imdb[4] or (paka != '' and paka == imdb[1]) or (paka != '' and paka == imdb[4]):
                                    pfound = True
                                    break
                        else:
                            url_poster = "{}._V1_UY278,1,185,278_AL_.jpg".format(imdb_poster.group(1))
                            imsg = "Found title : '{}', aka : '{}', year : ''".format(imdb[1], imdb[4])
                            if title_safe == imdb[1] or title_safe == imdb[4] or (paka != '' and paka == imdb[1]) or (paka != '' and paka == imdb[4]):
                                pfound = True
                                break
                idx_imdb += 1

            if url_poster and pfound:
                self.savePoster(dwn_poster, url_poster)
                if self.verifyPoster(dwn_poster):
                    self.resizePoster(dwn_poster)
                return True, "[SUCCESS url_poster: imdb] {} [{}-{}] => {} [{}/{}] => {} => {}".format(title_safe, chkType, year, imsg, idx_imdb, len_imdb, url_mimdb, url_poster)
            else:
                return False, "[SKIP : imdb] {} [{}-{}] => {} (No Entry found [{}])".format(title_safe, chkType, year, url_mimdb, len_imdb)
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : imdb] {} [{}-{}] => {} ({})".format(title_safe, chkType, year, url_mimdb, str(e))

    def search_programmetv_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            url_ptv = ''
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            chkType, fd = self.checkType(shortdesc, fulldesc)
            if chkType.startswith("movie"):
                return False, "[SKIP : programmetv-google] {} [{}] => Skip movie title".format(title, chkType)
            title_safe = self.UNAC(title)
            title_safe = title_safe.replace(' ', '')
            title_safe = quoteEventName(title_safe)
            url_ptv = "site:programme-tv.net+" + title_safe
            if channel and title_safe.find(channel.split()[0]) < 0:
                url_ptv += "+" + quoteEventName(channel)
            url_ptv = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_ptv)
            ff = requests.get(url_ptv, stream=True, headers=headers, cookies={'CONSENT': 'YES+'}).text
            if not PY3:
                ff = ff.encode('utf-8')
            ptv_id = 0
            plst = re.findall(r'\],\["https://www.programme-tv.net(.*?)",\d+,\d+]', ff)
            for posterlst in plst:
                ptv_id += 1
                url_poster = "https://www.programme-tv.net{}".format(posterlst)
                url_poster = re.sub(r"\\u003d", "=", url_poster)
                url_poster_size = re.findall(r'([\d]+)x([\d]+).*?([\w\.-]+).jpg', url_poster)
                if url_poster_size and url_poster_size[0]:
                    get_title = self.UNAC(url_poster_size[0][2].replace('-', ''))
                    if title_safe == get_title:
                        h_ori = float(url_poster_size[0][1])
                        h_tar = float(re.findall(r'(\d+)', isz)[1])
                        ratio = h_ori / h_tar
                        w_ori = float(url_poster_size[0][0])
                        w_tar = w_ori / ratio
                        w_tar = int(w_tar)
                        h_tar = int(h_tar)
                        url_poster = re.sub(r'/\d+x\d+/', "/" + str(w_tar) + "x" + str(h_tar) + "/", url_poster)
                        url_poster = re.sub(r'crop-from/top/', '', url_poster)
                        self.savePoster(dwn_poster, url_poster)
                        if self.verifyPoster(dwn_poster) and url_poster_size:
                            self.resizePoster(dwn_poster)
                            return True, "[SUCCESS url_poster: programmetv-google] {} [{}] => Found title_safe : '{}' => {} => {} (initial size: {}) [{}]".format(title_safe, chkType, get_title, url_ptv, url_poster, url_poster_size, ptv_id)
                        else:
                            if os.path.exists(dwn_poster):
                                os.remove(dwn_poster)

            return False, "[SKIP : programmetv-google] {} [{}] => Not found [{}] => {}".format(title_safe, chkType, ptv_id, url_ptv)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : programmetv-google] {} [{}] => {} ({})".format(title_safe, chkType, url_ptv, str(e))

    def search_molotov_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            url_mgoo = ''
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            chkType, fd = self.checkType(shortdesc, fulldesc)
            title_safe = self.UNAC(title)
            title_safe = quoteEventName(title_safe)
            if channel:
                pchannel = self.UNAC(channel).replace(' ', '')
            else:
                pchannel = ''
            poster = None
            pltc = None
            imsg = ''
            url_mgoo = "site:molotov.tv+" + title_safe
            if channel and title_safe.find(channel.split()[0]) < 0:
                url_mgoo += "+" + quoteEventName(channel)
            url_mgoo = "https://www.google.com/search?q={}&tbm=isch".format(url_mgoo)
            ff = requests.get(url_mgoo, stream=True, headers=headers, cookies={'CONSENT': 'YES+'}).text
            if not PY3:
                ff = ff.encode('utf-8')
            plst = re.findall(r'https://www.molotov.tv/(.*?)"(?:.*?)?"(.*?)"', ff)
            len_plst = len(plst)
            molotov_id = 0
            molotov_table = [0, 0, None, None, 0]
            partialtitle = 0
            partialchannel = 0
            for pl in plst:
                get_path = "https://www.molotov.tv/" + pl[0]
                get_name = self.UNAC(pl[1])
                get_title = re.findall(r'(.*?)[ ]+en[ ]+streaming', get_name)
                if get_title:
                    get_title = get_title[0]
                else:
                    get_title = None
                get_channel = re.findall(r'(?:streaming|replay)?[ ]+sur[ ]+(.*?)[ ]+molotov.tv', get_name)
                if get_channel:
                    get_channel = self.UNAC(get_channel[0]).replace(' ', '')
                else:
                    get_channel = re.findall(r'regarder[ ]+(.*?)[ ]+en', get_name)
                    if get_channel:
                        get_channel = self.UNAC(get_channel[0]).replace(' ', '')
                    else:
                        get_channel = None
                partialchannel = self.PMATCH(pchannel, get_channel)
                partialtitle = self.PMATCH(title_safe, get_title)
                if partialtitle > molotov_table[0]:
                    molotov_table = [partialtitle, partialchannel, get_name, get_path, molotov_id]
                if partialtitle == 100 and partialchannel == 100:
                    break
                molotov_id += 1

            if molotov_table[0]:
                ffm = requests.get(molotov_table[3], stream=True, headers=headers).text
                if not PY3:
                    ffm = ffm.encode('utf-8')
                pltt = re.findall(r'"https://fusion.molotov.tv/(.*?)/jpg" alt="(.*?)"', ffm)
                if len(pltt) > 0:
                    pltc = self.UNAC(pltt[0][1])
                    plst = "https://fusion.molotov.tv/" + pltt[0][0] + "/jpg"
                    imsg = "Found title ({}%) & channel ({}%) : '{}' + '{}' [{}/{}]".format(molotov_table[0], molotov_table[1], molotov_table[2], pltc, molotov_table[4], len_plst)
            else:
                plst = re.findall(r'\],\["https://(.*?)",\d+,\d+].*?"https://.*?","(.*?)"', ff)
                len_plst = len(plst)
                if len_plst > 0:
                    for pl in plst:
                        if pl[1].startswith("Regarder"):
                            pltc = self.UNAC(pl[1])
                            partialtitle = self.PMATCH(title_safe, pltc)
                            get_channel = re.findall(r'regarder[ ]+(.*?)[ ]+en', pltc)
                            if get_channel:
                                get_channel = self.UNAC(get_channel[0]).replace(' ', '')
                            else:
                                get_channel = None
                            partialchannel = self.PMATCH(pchannel, get_channel)
                            if partialchannel > 0 and partialtitle < 50:
                                partialtitle = 50
                            plst = "https://" + pl[0]
                            molotov_table = [partialtitle, partialchannel, pltc, plst, -1]
                            imsg = "Fallback title ({}%) & channel ({}%) : '{}' [{}/{}]".format(molotov_table[0], molotov_table[1], pltc, -1, len_plst)
                            break

            if molotov_table[0] == 100 and molotov_table[1] == 100:
                poster = plst
            elif chkType.startswith("movie"):
                imsg = "Skip movie type '{}' [{}%-{}%-{}]".format(pltc, molotov_table[0], molotov_table[1], len_plst)
            elif molotov_table[0] == 100:
                poster = plst
            elif molotov_table[0] >= 50 and molotov_table[1]:
                poster = plst
            elif molotov_table[0] >= 75:
                poster = plst
            elif chkType == '':
                imsg = "Skip unknown type '{}' [{}%-{}%-{}]".format(pltc, molotov_table[0], molotov_table[1], len_plst)
            elif molotov_table[0] >= 25 and molotov_table[1]:
                poster = plst
            elif molotov_table[0] >= 50:
                poster = plst
            else:
                imsg = "Not found '{}' [{}%-{}%-{}]".format(pltc, molotov_table[0], molotov_table[1], len_plst)
            if poster:
                url_poster = re.sub(r'/\d+x\d+/', "/" + re.sub(r', ', 'x', isz) + "/", poster)
                self.savePoster(dwn_poster, url_poster)
                if self.verifyPoster(dwn_poster):
                    self.resizePoster(dwn_poster)
                    return True, "[SUCCESS url_poster: molotov-google] {} ({}) [{}] => {} => {} => {}".format(title_safe, channel, chkType, imsg, url_mgoo, url_poster)
                else:
                    if os.path.exists(dwn_poster):
                        os.remove(dwn_poster)
                    return False, "[SKIP : molotov-google] {} ({}) [{}] => {} => {} => {} (jpeg error)".format(title_safe, channel, chkType, imsg, url_mgoo, url_poster)
            else:
                return False, "[SKIP : molotov-google] {} ({}) [{}] => {} => {}".format(title_safe, channel, chkType, imsg, url_mgoo)
        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : molotov-google] {} [{}] => {} ({})".format(title_safe, chkType, url_mgoo, str(e))

    def search_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            chkType, fd = self.checkType(shortdesc, fulldesc)
            poster = None
            url_poster = ''
            year = None
            srch = None
            title_safe = quoteEventName(title)
            year = re.findall(r'19\d{2}|20\d{2}', fd)
            if len(year) > 0:
                year = year[0]
            else:
                year = None
            if chkType.startswith("movie"):
                srch = chkType[6:]
            elif chkType.startswith("tv"):
                srch = chkType[3:]
            url_google = '"' + title_safe + '"'
            if channel and title_safe.find(channel) < 0:
                url_google += "+{}".format(quoteEventName(channel))
            if srch:
                url_google += "+{}".format(srch)
            if year:
                url_google += "+{}".format(year)
            # url_google = "https://www.google.com/search?q={}&tbm=isch".format(url_google)
            url_google = "https://www.google.com/search?q={}&tbm=isch&tbs=sbd:0".format(url_google)
            # url_google += "+{}".format(poster)
            ff = requests.get(url_google, stream=True, headers=headers, cookies={'CONSENT': 'YES+'}).text
            posterlst = re.findall(r'\],\["https://(.*?)",\d+,\d+]', ff)
            if len(posterlst) == 0:
                url_google = title_safe
                url_google = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_google)
                ff = requests.get(url_google, stream=True, headers=headers).text
                posterlst = re.findall(r'\],\["https://(.*?)",\d+,\d+]', ff)

            for pl in posterlst:
                url_poster = "https://{}".format(pl)
                url_poster = re.sub(r"\\u003d", " = ", url_poster)
                self.savePoster(dwn_poster, url_poster)
                if self.verifyPoster(dwn_poster):
                    self.resizePoster(dwn_poster)
                    poster = pl
                    break
            if poster:
                return True, "[SUCCESS poster: google] {} [{}-{}] => {} => {}".format(title_safe, chkType, year, url_google, url_poster)
            else:
                if os.path.exists(dwn_poster):
                    os.remove(dwn_poster)
                return False, "[SKIP : google] {} [{}-{}] => {} => {} (Not found)".format(title_safe, chkType, year, url_google, url_poster)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : google] {} [{}-{}] => {} => {} ({})".format(title_safe, chkType, year, url_google, url_poster, str(e))

    def downloadErrorInfo(self, error, url):
        print('Error during download from URL:', url, error)

    def savePoster(self, dwn_poster, url_poster):
        try:
            with open(dwn_poster, 'wb') as f:
                f.write(urlopen(url_poster).read())
            file_size = os.path.getsize(dwn_poster)
            if file_size == 0:
                os.remove(dwn_poster)
            else:
                print('Backdrop scaricato:', dwn_poster)
        except Exception as e:
            print('Errore nel salvataggio del backdrop:', e)
        return

    def resizePoster(self, dwn_poster):
        try:
            img = Image.open(dwn_poster)
            width, height = img.size
            ratio = float(width) / float(height)
            new_height = int(isz.split(",")[1])
            new_width = int(ratio * new_height)
            try:
                rimg = img.resize((new_width, new_height), Image.LANCZOS)
            except:
                rimg = img.resize((new_width, new_height), Image.ANTIALIAS)
            img.close()
            rimg.save(dwn_poster)
            rimg.close()
        except Exception as e:
            print("ERROR:{}".format(e))

    def verifyPoster(self, dwn_poster):
        try:
            img = Image.open(dwn_poster)
            img.verify()
            if img.format == "JPEG":
                pass
            else:
                try:
                    os.remove(dwn_poster)
                except:
                    pass
                return False
        except Exception as e:
            print(e)
            try:
                os.remove(dwn_poster)
            except:
                pass
            return False
        return True

    def checkType(self, shortdesc, fulldesc):
        if shortdesc and shortdesc != '':
            fd = shortdesc.splitlines()[0]
        elif fulldesc and fulldesc != '':
            fd = fulldesc.splitlines()[0]
        else:
            fd = ''
        global srch
        srch = "multi"
        return srch, fd

    def UNAC(self, string):
        string = html.unescape(string)
        string = unicodedata.normalize('NFD', string)
        string = re.sub(r"u0026", "&", string)
        string = re.sub(r"u003d", "=", string)
        string = re.sub(r'[\u0300-\u036f]', '', string)
        string = re.sub(r"[,!?\.\"]", ' ', string)
        string = re.sub(r"[-/:']", '', string)
        string = re.sub(r"[^a-zA-Z0-9 ]", "", string)
        string = string.lower()
        string = re.sub(r'\s+', ' ', string)
        string = string.strip()
        return string

    def PMATCH(self, textA, textB):
        if not textB or textB == '' or not textA or textA == '':
            return 0
        if textA == textB:
            return 100
        if textA.replace(" ", "") == textB.replace(" ", ""):
            return 100
        if len(textA) > len(textB):
            lId = len(textA.replace(" ", ""))
        else:
            lId = len(textB.replace(" ", ""))
        textA = textA.split()
        cId = 0
        for id in textA:
            if id in textB:
                cId += len(id)
        cId = 100 * cId / lId
        return cId
