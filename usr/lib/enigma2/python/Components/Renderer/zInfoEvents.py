#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020, 11.2020, 06.2021
# file by sunriser 07.2021
# <widget source="session.Event_Now" render="zInfoEvents"/>
# <widget source="session.Event_Next" render="zInfoEvents"/>
# <widget source="Event" render="zInfoEvents"/>
# edit by lululla 07.2022
# recode from lululla 2023
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from Components.config import config
from enigma import (
    eLabel,
    eEPGCache,
    eTimer,
)
from time import gmtime
import json
import os
import re
import socket
import sys
import NavigationInstance
from .Converlibr import convtext, quoteEventName
global my_cur_skin, path_folder

my_cur_skin = False
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    from _thread import start_new_thread
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen
else:
    from thread import start_new_thread
    from urllib2 import HTTPError, URLError
    from urllib2 import urlopen


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
# thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
epgcache = eEPGCache.getInstance()


def isMountedInRW(mount_point):
    with open("/proc/mounts", "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) > 1 and parts[1] == mount_point:
                return True
    return False


cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
path_folder = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if isMountedInRW("/media/hdd"):
        path_folder = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if isMountedInRW("/media/usb"):
        path_folder = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if isMountedInRW("/media/mmc"):
        path_folder = "/media/mmc/poster"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


try:
    if my_cur_skin is False:
        skin_paths = {
            "tmdb_api": "/usr/share/enigma2/{}/tmdbkey".format(cur_skin),
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
    return True


class zInfoEvents(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.adsl = intCheck()
        if not self.adsl:
            print("Connessione assente, modalità offline.")
            return
        else:
            print("Connessione rilevata.")
        self.text = ""

    GUI_WIDGET = eLabel

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            return self.text
        if what[0] != self.CHANGED_CLEAR:
            if self.instance:
                self.instance.hide()
            self.showInfos()

    def showInfos(self):
        self.event = self.source.event
        if self.event and self.event != 'None' or self.event is not None:
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            if not self.event:
                return
            if not PY3:
                self.evnt = self.evnt.encode('utf-8')
            self.evntNm = convtext(self.evnt)
            self.infos_file = "{}/{}".format(path_folder, self.evntNm)
            self.text = ''
            if not os.path.exists(self.infos_file):
                self.downloadInfos()
            if os.path.exists(self.infos_file):
                try:
                    with open(self.infos_file, 'r') as f:
                        data = json.load(f)
                        Title = data.get("Title", "")
                        imdbRating = data.get("imdbRating", "")
                        Country = data.get("Country", "")
                        Year = data.get("Year", "")
                        Rated = data.get("Rated", "")
                        Genre = data.get("Genre", "")
                        Awards = data.get("Awards", "")
                        Director = data.get("Director", "")
                        Writer = data.get("Writer", "")
                        Actors = data.get("Actors", "")

                        if Title and Title != "N/A":
                            with open("/tmp/rating", "w") as f_rating:
                                f_rating.write("%s\n%s" % (imdbRating, Rated))
                            self.text = "Title: %s\nYear: %s\nCountry: %s\nGenre: %s\nDirector: %s\nAwards: %s\nWriter: %s\nCast: %s\nRated: %s\nImdb: %s" % (
                                str(Title), str(Year), str(Country), str(Genre), str(Director),
                                str(Awards), str(Writer), str(Actors), str(Rated), str(imdbRating)
                            )
                            print("iInfoEvents self.text= ", self.text)
                            self.instance.show()
                        else:
                            if os.path.exists("/tmp/rating"):
                                os.remove("/tmp/rating")
                                print('/tmp/rating removed')
                        return self.text
                except Exception as e:
                    print(e)
            else:
                return self.text

    def downloadInfos(self):
        self.year = self.filterSearch()
        try:
            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(self.srch, tmdb_api, quoteEventName(self.evntNm))
            if self.year:
                url_tmdb += "&year={}".format(self.year)
            print('downloadInfos url_tmdb=', url_tmdb)
            try:
                response_tmdb = urlopen(url_tmdb)
                data_tmdb = json.load(response_tmdb)
                try:
                    title = data_tmdb["results"][0]["title"]
                except KeyError:
                    title = data_tmdb["results"][0]["original_name"]
                print('downloadInfos Title: ', title)
                url_omdb = "http://www.omdbapi.com/?apikey={}&t={}".format(omdb_api, quoteEventName(title))
                print('downloadInfos url_omdb=', url_omdb)
                response_omdb = urlopen(url_omdb)
                data_omdb = json.load(response_omdb)
                with open(self.infos_file, "w") as f:
                    f.write(json.dumps(data_omdb))
            except Exception as e:
                print("Errore durante il download delle informazioni: ", str(e))

        except Exception as e:
            print("Errore generale: ", str(e))

    def filterSearch(self):
        try:
            self.srch = "multi"
            sd = "%s\n%s\n%s" % (self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
            keywords = [
                "t/s", "Т/s", "SM", "d/s", "D/s", "stagione",
                "Sig.", "episodio", "serie TV", "serie"
            ]
            for keyword in keywords:
                if keyword in sd:
                    self.srch = "tv"
                    break
            years = re.findall(r'\d{4}', sd)
            valid_years = [_y for _y in years if '1930' <= _y <= str(gmtime().tm_year)]
            return valid_years[-1] if valid_years else None
        except Exception as e:
            print("Errore in filterSearch:", str(e))
            return False

    def epgs(self):
        try:
            events = None
            ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
            events = epgcache.lookupEvent(['IBDCT', (ref, 0, -1, -1)])
            for i in range(9):
                titleNxt = events[i][4]
                self.evntNm = convtext(titleNxt)
                self.infos_file = "{}/{}".format(path_folder, self.evntNm)
                if not os.path.exists(self.infos_file):
                    self.downloadInfos()
        except:
            pass

    def delay2(self):
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.dwn)
        except:
            self.timer.callback.append(self.dwn)
        self.timer.start(10, True)

    def dwn(self):
        start_new_thread(self.epgs, ())
