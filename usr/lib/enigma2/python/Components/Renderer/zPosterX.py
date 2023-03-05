#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021,
# 08.2021(stb lang support),
# 09.2021 mini fixes
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# for infobar,
# <widget source="session.Event_Now" render="zPosterX" position="0,125" size="185,278" path="/media/hdd/poster/" nexts="10" language="en" zPosition="9" />
# <widget source="session.Event_Next" render="zPosterX" position="100,100" size="185,278" />
# <widget source="session.Event_Now" render="zPosterX" position="100,100" size="185,278" nexts="2" />
# <widget source="session.CurrentService" render="zPosterX" position="100,100" size="185,278" nexts="3" />
# for ch,
# <widget source="ServiceEvent" render="zPosterX" position="820,100" size="100,150" path="/media/hdd/poster/" zPosition="9" />
# for secondInfobar,
# <widget source="session.Event_Now" render="zPosterX" position="20,155" size="100,150" path="/media/hdd/poster/" zPosition="9" />
# <widget source="session.Event_Next" render="zPosterX" position="1080,155" size="100,150" path="/media/hdd/poster/" zPosition="9" />
# for epg, event
# <widget source="Event" render="zPosterX" position="931,184" size="185,278" path="/media/hdd/poster/" zPosition="9" />
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.Renderer.zPosterXDownloadThread import zPosterXDownloadThread
from Components.Sources.CurrentService import CurrentService
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent
from Components.config import config
from ServiceReference import ServiceReference
from enigma import ePixmap, loadJPG, eEPGCache
from enigma import eTimer
import NavigationInstance
import os
import re
import socket             
import sys
import time

import unicodedata

PY3 = sys.version_info.major >= 3

try:
    if PY3:
        import queue
        from _thread import start_new_thread
        from urllib.error import HTTPError, URLError
        PY3 = True
        unicode = str
        unichr = chr
        long = int
        xrange = range
    else:
        import Queue
        from thread import start_new_thread
        from urllib2 import HTTPError, URLError
        _str = str
        str = unicode
        range = xrange
        unicode = unicode
        basestring = basestring
except:
    pass


try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen


# w92
# w154
# w185
# w342
# w500
# w780
# original
formatImg = 'w185'
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

if not os.path.exists(path_folder):
    os.makedirs(path_folder)
if not os.path.exists(path_folder):
    path_folder = "/tmp/poster"


try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        # print('skinz namez', myz_skin)
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        # print('skinz namez', omdb_skin)
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
        # print('skinz namez', thetvdb_skin)
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


epgcache = eEPGCache.getInstance()
apdb = dict()


try:
    from Components.config import config
    language = config.osd.language.value
    language = language[:-3]
except:
    language = 'en'
    pass
print('language: ', language)

'''
# def setupTimer(method):
    # from enigma import eTimer  # @UnresolvedImport
    # timer = eTimer()
    # try:
        # conn = timer.timeout.connect(method)
        # return (timer, conn)
    # except AttributeError:
        # timer.callback.append(method)
        # return (timer, None)
'''
# SET YOUR PREFERRED BOUQUET FOR AUTOMATIC POSTER GENERATION
# WITH THE NUMBER OF ITEMS EXPECTED (BLANK LINE IN BOUQUET CONSIDERED)
# IF NOT SET OR WRONG FILE THE AUTOMATIC POSTER GENERATION WILL WORK FOR
# THE CHANNELS THAT YOU ARE VIEWING IN THE ENIGMA SESSION


autobouquet_file = '/etc/enigma2/userbouquet.favourites.tv'
autobouquet_count = 32
# Short script for Automatic poster generation on your preferred bouquet
if not os.path.exists(autobouquet_file):
    autobouquet_file = None
    autobouquet_count = 0
else:
    with open(autobouquet_file, 'r') as f:
        lines = f.readlines()
    if autobouquet_count > len(lines):
        autobouquet_count = len(lines)
    for i in range(autobouquet_count):
        if '#SERVICE' in lines[i]:
            line = lines[i][9:].strip().split(':')
            if len(line) == 11:
                value = ':'.join((line[3], line[4], line[5], line[6]))
                if value != '0:0:0:0':
                    service = ':'.join((line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]))
                    apdb[i] = service


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
        r'\s\*\d{4}\Z|'
        r'([\(\[\|].*?[\)\]\|])|'
        r'(\"|\"\.|\"\,|\.)\s.+|'
        r'\"|:|'
        r'Премьера\.\s|'
        r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
        r'(х|Х|м|М|т|Т|д|Д)/с\s|'
        r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
        r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
        r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)


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


if PY3:
    pdb = queue.LifoQueue()
else:
    pdb = Queue.LifoQueue()


class PosterDB(zPosterXDownloadThread):
    def __init__(self):
        zPosterXDownloadThread.__init__(self)
        self.logdbg = None

    def run(self):
        self.logDB("[QUEUE] : Initialized")
        while True:
            try:
                canal = pdb.get()
                self.logDB("[QUEUE] : {} : {}-{} ({})".format(canal[0], canal[1], canal[2], canal[5]))
                dwn_poster = path_folder + '/' + canal[5] + ".jpg"

                if os.path.exists(dwn_poster):
                    os.utime(dwn_poster, (time.time(), time.time()))

                if not os.path.exists(dwn_poster) and language == "it":
                    val, log = self.search_molotov_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                    self.logDB(log)

                if not os.path.exists(dwn_poster):
                    val, log = self.search_tmdb(dwn_poster, canal[5], canal[4], canal[3])
                    self.logDB(log)

                if not os.path.exists(dwn_poster):
                    val, log = self.search_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                    self.logDB(log)

                pdb.task_done()
                print('zPosterX task_done')
            except Exception as e:
                print('zPosterX exceptions', str(e))

    def logDB(self, logmsg):
        if self.logdbg:
            w = open("/tmp/PosterDB.log", "a+")
            w.write("%s\n" % logmsg)
            w.close()


threadDB = PosterDB()
threadDB.start()


class PosterAutoDB(zPosterXDownloadThread):
    def __init__(self):
        zPosterXDownloadThread.__init__(self)
        self.logdbg = None

    def run(self):
        self.logAutoDB("[AutoDB] *** Initialized")
        while True:
            time.sleep(7200)  # 7200 - Start every 2 hours
            self.logAutoDB("[AutoDB] *** Running ***")
            # AUTO ADD NEW FILES - 1440 (24 hours ahead)
            for service in apdb.values():
                try:
                    events = epgcache.lookupEvent(['IBDCTESX', (service, 0, -1, 1440)])
                    newfd = 0
                    newcn = None
                    for evt in events:
                        canal = [None, None, None, None, None, None]
                        canal[0] = ServiceReference(service).getServiceName()  # .replace('\xc2\x86', '').replace('\xc2\x87', '')
                        if evt[1] is None or evt[4] is None or evt[5] is None or evt[6] is None:
                            self.logAutoDB("[AutoDB] *** missing epg for {}".format(canal[0]))
                        else:
                            canal[1] = evt[1]
                            canal[2] = evt[4]
                            canal[3] = evt[5]
                            canal[4] = evt[6]
                            canal[5] = cleantitle(canal[2])
                            self.logAutoDB("[AutoDB] : {} : {}-{} ({})".format(canal[0], canal[1], canal[2], canal[5]))
                            dwn_poster = path_folder + '/' + canal[5] + ".jpg"
                            if os.path.exists(dwn_poster):
                                os.utime(dwn_poster, (time.time(), time.time()))

                            if not os.path.exists(dwn_poster) and language == "it":
                                val, log = self.search_molotov_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            if not os.path.exists(dwn_poster):
                                val, log = self.search_tmdb(dwn_poster, canal[2], canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1

                            if not os.path.exists(dwn_poster):
                                val, log = self.search_google(dwn_poster, canal[2], canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                        newcn = canal[0]
                    self.logAutoDB("[AutoDB] {} new file(s) added ({})".format(newfd, newcn))
                except Exception as e:
                    print('error logAutoDB ', e)
                    self.logAutoDB("[AutoDB] *** service")

            # AUTO REMOVE OLD FILES
            now_tm = time.time()
            emptyfd = 0
            oldfd = 0
            pathlist = path_folder + '/'
            for f in os.listdir(pathlist):
                diff_tm = now_tm - os.path.getmtime(pathlist + f)
                if diff_tm > 120 and os.path.getsize(pathlist + f) == 0:  # Detect empty files > 2 minutes
                    os.remove(pathlist + f)
                    emptyfd = emptyfd + 1
                if diff_tm > 259200:  # Detect old files > 3 days old
                    os.remove(pathlist + f)
                    oldfd = oldfd + 1
            self.logAutoDB("[AutoDB] {} old file(s) removed".format(oldfd))
            self.logAutoDB("[AutoDB] {} empty file(s) removed".format(emptyfd))
            self.logAutoDB("[AutoDB] *** Stopping ***")

    def logAutoDB(self, logmsg):
        if self.logdbg:
            w = open("/tmp/PosterAutoDB.log", "a+")
            w.write("%s\n" % logmsg)
            w.close()


threadAutoDB = PosterAutoDB()
threadAutoDB.start()


class zPosterX(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        adsl = intCheck()
        if not adsl:
            return
        self.nxts = 0
        self.path = path_folder + '/'
        self.canal = [None, None, None, None, None, None]
        self.oldCanal = None
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.showPoster)
        except:
            self.timer.callback.append(self.showPoster)
        self.timer.start(100, True)
        self.logdbg = None

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value,) in self.skinAttributes:
            if attrib == "nexts":
                self.nxts = int(value)
            if attrib == "path":
                self.path = str(value)
            attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
        if what[0] != self.CHANGED_CLEAR:
            servicetype = None
            try:
                service = None
                if isinstance(self.source, ServiceEvent):  # source="ServiceEvent"
                    service = self.source.getCurrentService()
                    servicetype = "ServiceEvent"
                elif isinstance(self.source, CurrentService):  # source="session.CurrentService"
                    service = self.source.getCurrentServiceRef()
                    servicetype = "CurrentService"
                elif isinstance(self.source, EventInfo):  # source="session.Event_Now" or source="session.Event_Next"
                    service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                    servicetype = "EventInfo"
                elif isinstance(self.source, Event):  # source="Event"
                    if self.nxts:
                        service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                    else:
                        self.canal[0] = None
                        self.canal[1] = self.source.event.getBeginTime()
                        self.canal[2] = self.source.event.getEventName()
                        self.canal[3] = self.source.event.getExtendedDescription()
                        self.canal[4] = self.source.event.getShortDescription()
                        self.canal[5] = cleantitle(self.canal[2])
                    servicetype = "Event"
                if service:
                    events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
                    self.canal[0] = ServiceReference(service).getServiceName()  # .replace('\xc2\x86', '').replace('\xc2\x87', '')
                    self.canal[1] = events[self.nxts][1]
                    self.canal[2] = events[self.nxts][4]
                    self.canal[3] = events[self.nxts][5]
                    self.canal[4] = events[self.nxts][6]
                    self.canal[5] = cleantitle(self.canal[2])
                    if not autobouquet_file:
                        if self.canal[0] not in apdb:
                            apdb[self.canal[0]] = service.toString()

            except Exception as e:
                print('changed error exc 2 ', e)
                self.instance.hide()
                return
            if not servicetype:
                self.instance.hide()
                return
            try:
                curCanal = "{}-{}".format(self.canal[1], self.canal[2])
                if curCanal == self.oldCanal:
                    return
                self.oldCanal = curCanal
                pstrNm = self.path + self.canal[5] + ".jpg"
                if os.path.exists(pstrNm):
                    self.timer.start(50, True)
                else:
                    canal = self.canal[:]
                    pdb.put(canal)
                    start_new_thread(self.waitPoster, ())
            except Exception as e:
                print('changed error 1', e)
                self.instance.hide()
                return

    def showPoster(self):
        self.instance.hide()
        if self.canal[5]:
            print('show poster init')
            pstrNm = self.path + self.canal[5] + ".jpg"
            if os.path.exists(pstrNm):
                # self.logPoster("[LOAD : showPoster] {}".format(pstrNm))
                self.instance.setPixmap(loadJPG(pstrNm))
                self.instance.setScale(1)
                self.instance.show()

    def waitPoster(self):
        self.instance.hide()
        print('show poster init')
        if self.canal[5]:
            pstrNm = self.path + self.canal[5] + ".jpg"
            loop = 180
            found = None
            # self.logPoster("[LOOP : waitPoster] {}".format(pstrNm))
            while loop >= 0:
                if os.path.exists(pstrNm):
                    if os.path.getsize(pstrNm) > 0:
                        loop = 0
                        found = True
                time.sleep(0.5)
                loop = loop - 1
            if found:
                self.timer.start(50, True)
                print('if found')

    def logPoster(self, logmsg):
        if self.logPoster:
            w = open("/tmp/zPosterX.log", "a+")
            w.write("%s\n" % logmsg)
            w.close()
