#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020, 11.2020, 06.2021
# file by sunriser 07.2021
# <widget source="session.Event_Now" render="zInfoEvents"/>
# <widget source="session.Event_Next" render="zInfoEvents"/>
# <widget source="Event" render="zInfoEvents"/>
# edit by lululla 07.2022

from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from Components.config import config
from enigma import eLabel
from enigma import eTimer
from enigma import eEPGCache
from time import gmtime
import json
import os
import re
import sys
import NavigationInstance
import unicodedata
PY3 = sys.version_info.major >= 3

global my_cur_skin, path_folder

try:
    from urllib.parse import quote
    from urllib.request import urlopen
    from _thread import start_new_thread
    from urllib.error import HTTPError, URLError
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    xrange = range
except:
    from urllib import quote
    from urllib2 import urlopen
    from thread import start_new_thread
    from urllib2 import HTTPError, URLError
    _str = str
    str = unicode
    range = xrange
    unicode = unicode
    basestring = basestring

apikey = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
epgcache = eEPGCache.getInstance()
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


REGEX = re.compile(
        r'([\(\[]).*?([\)\]])|'
        r'(: odc.\d+)|'
        r'(\d+: odc.\d+)|'
        r'(\d+ odc.\d+)|(:)|'
        r'( -(.*?).*)|(,)|'
        r'!|'
        r'/.*|'
        r'\|\s[0-9]+\+|'
        r'[0-9]+\+|'
        r'\s\d{4}\Z|'
        r'([\(\[\|].*?[\)\]\|])|'
        r'(\"|\"\.|\"\,|\.)\s.+|'
        r'\"|:|'
        r'????????????????\.\s|'
        r'(??|??|??|??|??|??|??|??)/??\s|'
        r'(??|??|??|??|??|??|??|??)/??\s|'
        r'\s(??|??)(????????|????????|-??|-??)\s.+|'
        r'\s\d{1,3}\s(??|??\.|??\.|??)\s.+|'
        r'\.\s\d{1,3}\s(??|??\.|??\.|??)\s.+|'
        r'\s(??|??\.|??\.|??)\s\d{1,3}.+|'
        r'\d{1,3}(-??|-??|\s??-??).+|', re.DOTALL)


def intCheck():
    import socket
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


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cleantitle(text=''):
    try:
        print('text ->>> ', text)
        # import unicodedata
        if text != '' or text is not None:
            '''
            # text = text.replace('\xc2\x86', '')
            # text = text.replace('\xc2\x87', '')
            '''
            text = REGEX.sub('', text)
            text = re.sub(r"[-,!/\.\":]", ' ', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = text.strip()
            '''
            # try:
                # text = unicode(text, 'utf-8')
            # except Exception as e:
                # print('error name ',e)
                # pass
            # text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
            '''
            text = unicodify(text)
            text = text.lower()
            return text
    except Exception as e:
        print('cleantitle error: ', e)


class zInfoEvents(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        adsl = intCheck()
        if not adsl:
            return

    GUI_WIDGET = eLabel

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            self.text = ""
            return
        if what[0] != self.CHANGED_CLEAR:
            self.showInfos()

    def showInfos(self):
        self.event = self.source.event
        if self.event:
            self.delay2()
            self.evntNm = REGEX.sub("", self.event.getEventName()).strip().replace('??', '??')
            infos_file = "{}/{}.json".format(path_folder, quote(self.evntNm))
            if not os.path.exists(infos_file):
                self.downloadInfos(infos_file)
            if os.path.exists(infos_file):
                try:
                    with open(infos_file) as f:
                        data = json.load(f)
                        Title = ''
                        imdbRating = ''
                        Country = ''
                        Year = ''
                        Rated = ''
                        Genre = ''
                        Awards = ''
                        Director = ''
                        Writer = ''
                        Actors = ''
                        if 'Title' in data:
                            Title = data["Title"]
                        if 'imdbrating' in data:
                            imdbRating = data["imdbRating"]
                        if 'country' in data:
                            Country = data["Country"]
                        if 'year' in data:
                            Year = data["Year"]
                        if 'rated' in data:
                            Rated = data["Rated"]
                        if 'genre' in data:
                            Genre = data["Genre"]
                        if 'awards' in data:
                            Awards = data["Awards"]
                        if 'director' in data:
                            Director = data["Director"]
                        if 'writer' in data:
                            Writer = data["Writer"]
                        if 'actors' in data:
                            Actors = data["Actors"]

                        # if Title != "N/A" or Title != "":
                            # self.text = "Anno: %s\nNazione: %s\nGenere: %s\nRegista: %s\nAttori: %s" % (str(Year), str(Country), str(Genre), str(Director), str(Actors))
                        # else:
                            # self.text = None

                        if Title and Title != "N/A":
                            with open("/tmp/rating", "w") as f:
                                f.write("%s\n%s" % (imdbRating, Rated))
                            self.text = "Title : %s" % str(Title)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nYear : %s" % str(Year)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nCountry : %s" % str(Country)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nGenre : %s" % str(Genre)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nDirector : %s" % str(Director)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nAwards : %s" % str(Awards)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nWriter : %s" % str(Writer)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nCast : %s" % str(Actors)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nRated : %s" % str(Rated)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nImdb : %s" % str(imdbRating)  # .encode('utf-8').decode('utf-8')
                            print("text= ", self.text)
                            self.text = "Anno: %s\nNazione: %s\nGenere: %s\nRegista: %s\nAttori: %s" % (str(Year), str(Country), str(Genre), str(Director), str(Actors))

                        else:
                            if os.path.exists("/tmp/rating"):
                                os.remove("/tmp/rating")
                                print('/tmp/rating removed')
                                self.text = None
                            return self.text
                except Exception as e:
                    print(e)
            else:
                self.text = None

    def downloadInfos(self, infos_file):
        self.year = self.filterSearch()
        try:
            try:
                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&include_adult=true&query={}".format(self.srch, apikey, quote(self.evntNm))
                if self.year is not None:
                    url_tmdb += "&year={}".format(self.year)
                if PY3:
                    import six
                    url_tmdb = six.ensure_str(url_tmdb)
                try:
                    title = json.load(urlopen(url_tmdb))["results"][0]["title"]
                except:
                    title = json.load(urlopen(url_tmdb))["results"][0]["original_name"]
                print('Title1: ', title)
            except:
                pass
            try:
                url_omdb = "http://www.omdbapi.com/?apikey={}&t={}".format(omdb_api, quote(title))
                data_omdb = json.load(urlopen(url_omdb))
                dwn_infos = "{}/{}.json".format(path_folder, quote(self.evntNm))
                open(dwn_infos, "w").write(json.dumps(data_omdb))
            except:
                pass
        except Exception as e:
            print('error ', str(e))

    def filterSearch(self):
        try:
            sd = "%s\n%s\n%s" % (self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
            w = [
                    "t/s",
                    "??/s",
                    "SM",
                    "SM",
                    "d/s",
                    "D/s",
                    "stagione",
                    "Sig.",
                    "episodio",
                    "serie TV",
                    "serie"
                    ]
            for i in w:
                if i in sd:
                    self.srch = "tv"
                    break
                else:
                    self.srch = "multi"
            yr = [_y for _y in re.findall(r'\d{4}', sd) if '1930' <= _y <= '%s' % gmtime().tm_year]
            return '%s' % yr[-1] if yr else None
        except:
            pass

    def epgs(self):
        try:
            events = None
            ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
            events = epgcache.lookupEvent(['IBDCT', (ref, 0, -1, -1)])
            for i in range(9):
                titleNxt = events[i][4]
                self.evntNm = REGEX.sub('', titleNxt).rstrip().replace('??', '??')
                # self.evntNm = html_escape(titleNxt).rstrip().replace('??', '??')
                infos_file = "{}/{}.json".format(path_folder, quote(self.evntNm))
                if not os.path.exists(infos_file):
                    self.downloadInfos(infos_file)
                '''
                # # evnt = event.getEventName().encode('utf-8')
                # evntNm = html_escape(titleNxt).strip()
                # rating_json = "{}{}.json".format(path_folder, evntNm)
                '''
        except:
            pass

    def delay2(self):
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.dwn)
        except:
            self.timer.callback.append(self.dwn)
        self.timer.start(50, True)

    def dwn(self):
        start_new_thread(self.epgs, ())
