#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021,
# 08.2021(stb lang support),
# 09.2021 mini fixes
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# russian and py3 support by sunriser...
# downloading in the background while zaping...
# by beber...03.2022,
# 03.2022 several enhancements : several renders with one queue thread, google search (incl. molotov for france) + autosearch & autoclean thread ...
# 02.2023 fix major Lululla
# 04.2023 fix major Lululla
# for infobar,
# <widget source="session.Event_Now" render="zPosterX" position="0,125" size="185,278" path="/media/hdd/poster/" nexts="10" language="en" zPosition="9" />
# <widget source="session.Event_Next" render="zPosterX" position="100,100" size="185,278" />
# <widget source="session.Event_Now" render="zPosterX" position="100,100" size="185,278" nexts="2" />
# <widget source="session.CurrentService" render="zPosterX" position="100,100" size="185,278" nexts="3" />

# for ch,
# <widget source="ServiceEvent" render="zPosterX" position="100,100" size="185,278" path="/media/hdd/poster/" zPosition="9" />
# <widget source="ServiceEvent" render="zPosterX" position="100,100" size="185,278" path="/media/hdd/poster/" nexts="2" zPosition="9" />

# for secondInfobar,
# <widget source="session.Event_Now" render="zPosterX" position="20,155" size="100,150" path="/media/hdd/poster/" zPosition="9" />
# <widget source="session.Event_Next" render="zPosterX" position="1080,155" size="100,150" path="/media/hdd/poster/" zPosition="9" />

# for epg, event
# <widget source="Event" render="zPosterX" position="931,184" size="185,278" path="/media/hdd/poster/" zPosition="9" />

from __future__ import print_function
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
PY3 = sys.version_info.major >= 3

try:
    import queue
    from _thread import start_new_thread
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    xrange = range
except:
    import Queue
    from thread import start_new_thread
    from urllib2 import HTTPError, URLError
    from urllib2 import urlopen
    _str = str
    str = unicode
    range = xrange
    unicode = unicode
    basestring = basestring


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


epgcache = eEPGCache.getInstance()
apdb = dict()


try:
                                     
    language = config.osd.language.value
    language = language[:-3]
except:
    language = 'en'
    pass

'''
def setupTimer(method):
    from enigma import eTimer  # @UnresolvedImport
    timer = eTimer()
    try:
        conn = timer.timeout.connect(method)
        return (timer, conn)
    except AttributeError:
        timer.callback.append(method)
        return (timer, None)
SET YOUR PREFERRED BOUQUET FOR AUTOMATIC POSTER GENERATION
WITH THE NUMBER OF ITEMS EXPECTED (BLANK LINE IN BOUQUET CONSIDERED)
IF NOT SET OR WRONG FILE THE AUTOMATIC POSTER GENERATION WILL WORK FOR
THE CHANNELS THAT YOU ARE VIEWING IN THE ENIGMA SESSION
'''


def SearchBouquetTerrestrial():
    import glob
    for file in sorted(glob.glob('/etc/enigma2/*.tv')):
        f = open(file, 'r').read()
        x = f.strip().lower()
        if x.find('eeee0000') != -1:
            if x.find('82000') == -1 and x.find('c0000') == -1:
                return file
                break


try:
    autobouquet_file = SearchBouquetTerrestrial()
except:
    autobouquet_file = '/etc/enigma2/userbouquet.favourites.tv'
print('autobouquet_file = ', autobouquet_file)
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
adsl = intCheck()
if not adsl:
    return


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cleantitle(text=''):
    try:
        print('zPosterX text ->>> ', text)
        # import unicodedata
        if text != '' or text is not None or text != 'None':
            '''
            # text = text.replace('\xc2\x86', '')
            # text = text.replace('\xc2\x87', '')
            '''
            text = REGEX.sub('', text)
            text = re.sub(r"[-,!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            # text = text.strip()
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
            print('zPosterX text <<<- ', text)
        else:
            text = text
            print('zPosterX text <<<->>> ', text)
        return text
    except Exception as e:
        print('cleantitle error: ', e)
        pass


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
                if not os.path.exists(dwn_poster):
                    val, log = self.search_tmdb(dwn_poster, canal[5], canal[4], canal[3])
                    self.logDB(log)

                if not os.path.exists(dwn_poster):
                    val, log = self.search_molotov_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                    self.logDB(log)

                # if not os.path.exists(dwn_poster):
                    # val, log = self.search_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                    # self.logDB(log)

                pdb.task_done()
            except Exception as e:
                print('ZPoster exceptions', str(e))

    def logDB(self, logmsg):
        try:
            w = open("/tmp/PosterDB.log", "a+")
            w.write("%s\n" % logmsg)
            w.close()
        except Exception as e:
            print('logDB exceptions', str(e))


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
                            if not os.path.exists(dwn_poster):
                                val, log = self.search_tmdb(dwn_poster, canal[2], canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            if not os.path.exists(dwn_poster):
                                val, log = self.search_molotov_google(dwn_poster, canal[2], canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            # if not os.path.exists(dwn_poster):
                                # val, log = self.search_google(dwn_poster, canal[2], canal[4], canal[3], canal[0])
                                # if val and log.find("SUCCESS"):
                                    # newfd += 1
                            newcn = canal[0]
                        self.logAutoDB("[AutoDB] {} new file(s) added ({})".format(newfd, newcn))
                except Exception as e:
                    self.logAutoDB("[AutoDB] *** service error ({})".format(e))
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
                    os.remove("/tmp/PosterAutoDB.log")  # remove PosterAutoDB > 3 days old
                    os.remove("/tmp/zPoster.log")  # remove zPosterX > 3 days old
                    oldfd = oldfd + 1
            self.logAutoDB("[AutoDB] {} old file(s) removed".format(oldfd))
            self.logAutoDB("[AutoDB] {} empty file(s) removed".format(emptyfd))
            self.logAutoDB("[AutoDB] *** Stopping ***")

    def logAutoDB(self, logmsg):
        try:
            w = open("/tmp/PosterAutoDB.log", "a+")
            w.write("%s\n" % logmsg)
            w.close()
        except Exception as e:
            print('error logAutoDB 2 ', e)


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
        self.timer.start(50, True)
        # self.timer.callback.append(self.showPoster)
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
        # if what[0] == self.CHANGED_CLEAR:
            # self.instance.hide()
            # return
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
                self.logPoster("Error (service) : " + str(e))
                self.instance.hide()
                return
            if not servicetype:
                self.logPoster("Error service type undefined")
                self.instance.hide()
                return
            try:
                curCanal = "{}-{}".format(self.canal[1], self.canal[2])
                if curCanal == self.oldCanal:
                    return
                self.oldCanal = curCanal
                self.logPoster("Service : {} [{}] : {} : {}".format(servicetype, self.nxts, self.canal[0], self.oldCanal))
                pstrNm = self.path + self.canal[5] + ".jpg"
                # pstrNm = str(pstrNm)
                if os.path.exists(pstrNm):
                    self.timer.start(50, True)
                else:
                    canal = self.canal[:]
                    pdb.put(canal)
                    start_new_thread(self.waitPoster, ())
            except Exception as e:
                self.logPoster("Error (eFile) : " + str(e))
                self.instance.hide()
                return
        else:
            self.instance.hide()
            return


    def showPoster(self):
        self.instance.hide()
        if self.canal[5]:
            pstrNm = self.path + self.canal[5] + ".jpg"
            # pstrNm = str(pstrNm)
            if os.path.exists(pstrNm):
                self.logPoster("[LOAD : showPoster] {}".format(pstrNm))
                self.instance.setPixmap(loadJPG(pstrNm))
                self.instance.setScale(1)
                # self.instance.setScale(2)
                self.instance.show()

    def waitPoster(self):
        self.instance.hide()
        if self.canal[5]:
            pstrNm = self.path + self.canal[5] + ".jpg"
            # pstrNm = str(pstrNm)
            loop = 180
            found = None
            self.logPoster("[LOOP : waitPoster] {}".format(pstrNm))
            while loop >= 0:
                if os.path.exists(pstrNm):
                    if os.path.getsize(pstrNm) > 0:
                        loop = 0
                        found = True
                time.sleep(0.5)
                loop = loop - 1
            if found:
                self.timer.start(20, True)
        return

    def logPoster(self, logmsg):
        try:
            w = open("/tmp/zPoster.log", "a+")
            w.write("%s\n" % logmsg)
            w.close()
        except Exception as e:
            print('logPoster error', e)
