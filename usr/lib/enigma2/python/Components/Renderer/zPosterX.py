#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021,
# 08.2021(stb lang support),
# 09.2021 mini fixes
# edit by lululla 07.2022
# recode from lululla 2023
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# russian and py3 support by sunriser...
# downloading in the background while zaping...
# by beber...03.2022,
# 03.2022 several enhancements : several renders with one queue thread, google search (incl. molotov for france) + autosearch & autoclean thread ...
# for infobar,
# <widget source="session.Event_Now" render="ZPoster" position="100,100" size="185,278" />
# <widget source="session.Event_Next" render="ZPoster" position="100,100" size="100,150" />
# <widget source="session.Event_Now" render="ZPoster" position="100,100" size="185,278" nexts="2" />
# <widget source="session.CurrentService" render="ZPoster" position="100,100" size="185,278" nexts="3" />

# for ch,
# <widget source="ServiceEvent" render="ZPoster" position="100,100" size="185,278" />
# <widget source="ServiceEvent" render="ZPoster" position="100,100" size="185,278" nexts="2" />

# for epg, event
# <widget source="Event" render="ZPoster" position="100,100" size="185,278" />
# <widget source="Event" render="ZPoster" position="100,100" size="185,278" nexts="2" />
# or put tag -->  path="/media/hdd/poster"
from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.Renderer.zPosterXDownloadThread import zPosterXDownloadThread
from Components.Sources.CurrentService import CurrentService
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent

from Components.config import config
from ServiceReference import ServiceReference
from enigma import (
    ePixmap,
    loadJPG,
    eEPGCache,
    eTimer,
)
import NavigationInstance
import os
import re
import shutil
import socket
import sys
import time


PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    import queue
    import html
    html_parser = html
    from _thread import start_new_thread
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen
    from urllib.parse import quote_plus
else:
    import Queue
    from thread import start_new_thread
    from urllib2 import HTTPError, URLError
    from urllib2 import urlopen
    from urllib import quote_plus
    from HTMLParser import HTMLParser
    html_parser = HTMLParser()


try:
    from urllib import unquote, quote
except ImportError:
    from urllib.parse import unquote, quote


epgcache = eEPGCache.getInstance()
if PY3:
    pdb = queue.LifoQueue()
else:
    pdb = Queue.LifoQueue()


def isMountReadonly(mnt):
    mount_point = ''
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


def isMountedInRW(path):
    testfile = path + '/tmp-rw-test'
    os.system('touch ' + testfile)
    if os.path.exists(testfile):
        os.system('rm -f ' + testfile)
        return True
    return False


cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
noposter = "/usr/share/enigma2/%s/menu/nocover.jpg" % cur_skin

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


epgcache = eEPGCache.getInstance()
apdb = dict()


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass


# SET YOUR PREFERRED BOUQUET FOR AUTOMATIC POSTER GENERATION
# WITH THE NUMBER OF ITEMS EXPECTED (BLANK LINE IN BOUQUET CONSIDERED)
# IF NOT SET OR WRONG FILE THE AUTOMATIC POSTER GENERATION WILL WORK FOR
# THE CHANNELS THAT YOU ARE VIEWING IN THE ENIGMA SESSION

# add lululla
def SearchBouquetTerrestrial():
    import glob
    import codecs
    file = '/etc/enigma2/userbouquet.favourites.tv'
    for file in sorted(glob.glob('/etc/enigma2/*.tv')):
        with codecs.open(file, "r", encoding="utf-8") as f:
            file = f.read()
            x = file.strip().lower()
            if x.find('eeee') != -1:
                if x.find('82000') == -1 and x.find('c0000') == -1:
                    return file
                    break


if SearchBouquetTerrestrial():
    autobouquet_file = SearchBouquetTerrestrial()
else:
    autobouquet_file = '/etc/enigma2/userbouquet.favourites.tv'
# print('autobouquet_file = ', autobouquet_file)
autobouquet_count = 70
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


try:
    folder_size = sum([sum(map(lambda fname: os.path.getsize(os.path.join(path_folder, fname)), files)) for folder_p, folders, files in os.walk(path_folder)])
    ozposter = "%0.f" % (folder_size / (1024 * 1024.0))
    if ozposter >= "5":
        shutil.rmtree(path_folder)
except:
    pass


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


REGEX = re.compile(
    r'[\(\[].*?[\)\]]|'                    # Parentesi tonde o quadre
    r':?\s?odc\.\d+|'                      # odc. con o senza numero prima
    r'\d+\s?:?\s?odc\.\d+|'                # numero con odc.
    r'[:!]|'                               # due punti o punto esclamativo
    r'\s-\s.*|'                            # trattino con testo successivo
    r',|'                                  # virgola
    r'/.*|'                                # tutto dopo uno slash
    r'\|\s?\d+\+|'                         # | seguito da numero e +
    r'\d+\+|'                              # numero seguito da +
    r'\s\*\d{4}\Z|'                        # * seguito da un anno a 4 cifre
    r'[\(\[\|].*?[\)\]\|]|'                # Parentesi tonde, quadre o pipe
    r'(?:\"[\.|\,]?\s.*|\"|'               # Testo tra virgolette
    r'\.\s.+)|'                            # Punto seguito da testo
    r'Премьера\.\s|'                       # Specifico per il russo
    r'[хмтдХМТД]/[фс]\s|'                  # Pattern per il russo con /ф o /с
    r'\s[сС](?:езон|ерия|-н|-я)\s.*|'      # Stagione o episodio in russo
    r'\s\d{1,3}\s[чсЧС]\.?\s.*|'           # numero di parte/episodio in russo
    r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'         # numero di parte/episodio in russo con punto
    r'\s[чсЧС]\.?\s\d{1,3}.*|'             # Parte/Episodio in russo
    r'\d{1,3}-(?:я|й)\s?с-н.*',            # Finale con numero e suffisso russo
    re.DOTALL)


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


def remove_accents(string):
    import unicodedata
    if PY3 is False:
        if type(string) is not unicode:
            string = unicode(string, encoding='utf-8')
    # Normalizza la stringa usando Unicode NFD (Normalization Form D)
    string = unicodedata.normalize('NFD', string)
    # Rimuove i segni diacritici (accents) lasciando solo i caratteri base
    string = re.sub(r'[\u0300-\u036f]', '', string)
    return string


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def str_encode(text, encoding="utf8"):
    if not PY3:
        if isinstance(text, unicode):
            return text.encode(encoding)
    return text


def cutName(eventName=""):
    if eventName:
        eventName = eventName.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '').replace(' | ', '')
        eventName = eventName.replace('(18+)', '').replace('18+', '').replace('(16+)', '').replace('16+', '').replace('(12+)', '')
        eventName = eventName.replace('12+', '').replace('(7+)', '').replace('7+', '').replace('(6+)', '').replace('6+', '')
        eventName = eventName.replace('(0+)', '').replace('0+', '').replace('+', '')
        eventName = eventName.replace('episode', '')
        eventName = eventName.replace('مسلسل', '')
        eventName = eventName.replace('فيلم وثائقى', '')
        eventName = eventName.replace('حفل', '')
        return eventName
    return ""


def getCleanTitle(eventitle=""):
    # save_name = re.sub('\\(\d+\)$', '', eventitle)
    # save_name = re.sub('\\(\d+\/\d+\)$', '', save_name)  # remove episode-number " (xx/xx)" at the end
    # # save_name = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', save_name)
    save_name = eventitle.replace(' ^`^s', '').replace(' ^`^y', '')
    return save_name


def dataenc(data):
    if PY3:
        data = data.decode("utf-8")
    else:
        data = data.encode("utf-8")
    return data


def convtext(text=''):
    try:
        if text is None:
            print('return None original text: ', type(text))
            return  # Esci dalla funzione se text è None
        if text == '':
            print('text is an empty string')
        else:
            print('original text: ', text)
            text = text.lower()
            print('lowercased text: ', text)
            text = remove_accents(text)
            print('remove_accents text: ', text)

            # #
            text = cutName(text)
            text = getCleanTitle(text)
            # #
            if text.endswith("the"):
                text = "the " + text[:-4]
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
            text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('primatv', '').replace('1^tv', '')
            text = text.replace('prima visione', '').replace('1^ tv', '').replace('((', '(').replace('))', ')')
            text = text.replace('live:', '').replace(' - prima tv', '')
            if 'giochi olimpici parigi' in text:
                text = 'olimpiadi di parigi'
            if 'bruno barbieri' in text:
                text = text.replace('bruno barbieri', 'brunobarbierix')
            if "anni '60" in text:
                text = "anni 60"
            if 'tg regione' in text:
                text = 'tg3'
            if 'studio aperto' in text:
                text = 'studio aperto'
            if 'josephine ange gardien' in text:
                text = 'josephine ange gardien'
            if 'elementary' in text:
                text = 'elementary'
            if 'squadra speciale cobra 11' in text:
                text = 'squadra speciale cobra 11'
            if 'criminal minds' in text:
                text = 'criminal minds'
            if 'i delitti del barlume' in text:
                text = 'i delitti del barlume'
            if 'senza traccia' in text:
                text = 'senza traccia'
            if 'hudson e rex' in text:
                text = 'hudson e rex'
            if 'ben-hur' in text:
                text = 'ben-hur'
            if 'la7' in text:
                text = 'la7'
            if 'skytg24' in text:
                text = 'skytg24'
            # remove xx: at start
            text = re.sub(r'^\w{2}:', '', text)
            # remove xx|xx at start
            text = re.sub(r'^\w{2}\|\w{2}\s', '', text)
            # remove xx - at start
            text = re.sub(r'^.{2}\+? ?- ?', '', text)
            # remove all leading content between and including ||
            text = re.sub(r'^\|\|.*?\|\|', '', text)
            text = re.sub(r'^\|.*?\|', '', text)
            # remove everything left between pipes.
            text = re.sub(r'\|.*?\|', '', text)
            # remove all content between and including () multiple times
            text = re.sub(r'\(\(.*?\)\)|\(.*?\)', '', text)
            # remove all content between and including [] multiple times
            text = re.sub(r'\[\[.*?\]\]|\[.*?\]', '', text)
            # remove episode number in arabic series
            text = re.sub(r' +ح', '', text)
            # remove season number in arabic series
            text = re.sub(r' +ج', '', text)
            # remove season number in arabic series
            text = re.sub(r' +م', '', text)
            # List of bad strings to remove
            bad_strings = [
                "ae|", "al|", "ar|", "at|", "ba|", "be|", "bg|", "br|", "cg|", "ch|", "cz|", "da|", "de|", "dk|",
                "ee|", "en|", "es|", "eu|", "ex-yu|", "fi|", "fr|", "gr|", "hr|", "hu|", "in|", "ir|", "it|", "lt|",
                "mk|", "mx|", "nl|", "no|", "pl|", "pt|", "ro|", "rs|", "ru|", "se|", "si|", "sk|", "sp|", "tr|",
                "uk|", "us|", "yu|",
                "1080p", "1080p-dual-lat-cine-calidad.com", "1080p-dual-lat-cine-calidad.com-1",
                "1080p-dual-lat-cinecalidad.mx", "1080p-lat-cine-calidad.com", "1080p-lat-cine-calidad.com-1",
                "1080p-lat-cinecalidad.mx", "1080p.dual.lat.cine-calidad.com", "3d", "'", "#", "(", ")", "-", "[]", "/",
                "4k", "720p", "aac", "blueray", "ex-yu:", "fhd", "hd", "hdrip", "hindi", "imdb", "multi:", "multi-audio",
                "multi-sub", "multi-subs", "multisub", "ozlem", "sd", "top250", "u-", "uhd", "vod", "x264"
            ]

            # Remove numbers from 1900 to 2030
            bad_strings.extend(map(str, range(1900, 2030)))
            # Construct a regex pattern to match any of the bad strings
            bad_strings_pattern = re.compile('|'.join(map(re.escape, bad_strings)))
            # Remove bad strings using regex pattern
            text = bad_strings_pattern.sub('', text)
            # List of bad suffixes to remove
            bad_suffix = [
                " al", " ar", " ba", " da", " de", " en", " es", " eu", " ex-yu", " fi", " fr", " gr", " hr", " mk",
                " nl", " no", " pl", " pt", " ro", " rs", " ru", " si", " swe", " sw", " tr", " uk", " yu"
            ]
            # Construct a regex pattern to match any of the bad suffixes at the end of the string
            bad_suffix_pattern = re.compile(r'(' + '|'.join(map(re.escape, bad_suffix)) + r')$')
            # Remove bad suffixes using regex pattern
            text = bad_suffix_pattern.sub('', text)
            # Replace ".", "_", "'" with " "
            text = re.sub(r'[._\']', ' ', text)
            # recoded lulu
            text = text + 'FIN'
            '''
            if re.search(r'[Ss][0-9][Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9][Ee][0-9]+.*?FIN', '', text)
            if re.search(r'[Ss][0-9] [Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9] [Ee][0-9]+.*?FIN', '', text)
            '''
            text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
            text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
            text = re.sub(r'(\d+)+.*?FIN', '', text)
            text = text.partition("(")[0] + 'FIN'
            text = re.sub(r"\\s\d+", "", text)
            text = text.partition("(")[0]
            # text = text.partition(":")[0]  # not work on csi: new york (only-->  csi)
            text = text.partition(" -")[0]
            text = re.sub(' - +.+?FIN', '', text)  # all episodes and series ????
            text = re.sub('FIN', '', text)
            text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            # recoded  end
            text = text.strip(' -')
            # forced
            text = text.replace('XXXXXX', '60')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = quote(text, safe="")
            print('text safe: ', text)
        return unquote(text).capitalize()
    except Exception as e:
        print('convtext error: ', e)
        pass


class PosterDB(zPosterXDownloadThread):
    def __init__(self):
        zPosterXDownloadThread.__init__(self)
        self.logdbg = None
        self.pstcanal = None

    def run(self):
        self.logDB("[QUEUE] : Initialized")
        while True:
            canal = pdb.get()
            self.logDB("[QUEUE] : {} : {}-{} ({})".format(canal[0], canal[1], canal[2], canal[5]))
            self.pstcanal = convtext(canal[5])
            if self.pstcanal != 'None' or self.pstcanal is not None:
                dwn_poster = path_folder + '/' + self.pstcanal + ".jpg"
                if os.path.exists(dwn_poster):
                    os.utime(dwn_poster, (time.time(), time.time()))
                # if lng == "fr":
                    # if not os.path.exists(dwn_poster):
                        # val, log = self.search_molotov_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                        # self.logDB(log)
                    # if not os.path.exists(dwn_poster):
                        # val, log = self.search_programmetv_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                        # self.logDB(log)
                if not os.path.exists(dwn_poster):
                    val, log = self.search_tmdb(dwn_poster, self.pstcanal, canal[4], canal[3])
                    self.logDB(log)
                elif not os.path.exists(dwn_poster):
                    val, log = self.search_tvdb(dwn_poster, self.pstcanal, canal[4], canal[3])
                    self.logDB(log)
                elif not os.path.exists(dwn_poster):
                    val, log = self.search_fanart(dwn_poster, self.pstcanal, canal[4], canal[3])
                    self.logDB(log)
                elif not os.path.exists(dwn_poster):
                    val, log = self.search_imdb(dwn_poster, self.pstcanal, canal[4], canal[3])
                    self.logDB(log)
                elif not os.path.exists(dwn_poster):
                    val, log = self.search_google(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                    self.logDB(log)
                pdb.task_done()

    def logDB(self, logmsg):
        import traceback
        try:
            with open("/tmp/PosterDB.log", "a") as w:
                w.write("%s\n" % logmsg)
        except Exception as e:
            print('logDB error:', str(e))
            traceback.print_exc()


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
            self.pstcanal = None
            # AUTO ADD NEW FILES - 1440 (24 hours ahead)
            for service in apdb.values():
                try:
                    events = epgcache.lookupEvent(['IBDCTESX', (service, 0, -1, 1440)])
                    newfd = 0
                    newcn = None
                    for evt in events:
                        self.logAutoDB("[AutoDB] evt {} events ({})".format(evt, events))
                        canal = [None, None, None, None, None, None]
                        if PY3:
                            canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                        else:
                            canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                        if evt[1] is None or evt[4] is None or evt[5] is None or evt[6] is None:
                            self.logAutoDB("[AutoDB] *** missing epg for {}".format(canal[0]))
                        else:
                            canal[1] = evt[1]
                            canal[2] = evt[4]
                            canal[3] = evt[5]
                            canal[4] = evt[6]
                            canal[5] = canal[2]
                            self.pstcanal = convtext(canal[5])
                            # if self.pstcanal is not None:
                            self.pstrNm = path_folder + '/' + self.pstcanal + ".jpg"
                            self.pstcanal = str(self.pstrNm)
                            dwn_poster = self.pstcanal
                            if os.path.join(path_folder, dwn_poster):
                                os.utime(dwn_poster, (time.time(), time.time()))
                            # if lng == "fr":
                                # if not os.path.exists(dwn_poster):
                                    # val, log = self.search_molotov_google(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                                    # if val and log.find("SUCCESS"):
                                        # newfd += 1
                                # if not os.path.exists(dwn_poster):
                                    # val, log = self.search_programmetv_google(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                                    # if val and log.find("SUCCESS"):
                                        # newfd += 1
                            if not os.path.exists(dwn_poster):
                                val, log = self.search_tmdb(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            elif not os.path.exists(dwn_poster):
                                val, log = self.search_tvdb(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            elif not os.path.exists(dwn_poster):
                                val, log = self.search_fanart(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            elif not os.path.exists(dwn_poster):
                                val, log = self.search_imdb(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            elif not os.path.exists(dwn_poster):
                                val, log = self.search_google(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                                if val and log.find("SUCCESS"):
                                    newfd += 1
                            newcn = canal[0]
                        self.logAutoDB("[AutoDB] {} new file(s) added ({})".format(newfd, newcn))
                except Exception as e:
                    self.logAutoDB("[AutoDB] *** service error ({})".format(e))
            # AUTO REMOVE OLD FILES
            now_tm = time.time()
            emptyfd = 0
            oldfd = 0
            for f in os.listdir(path_folder):
                diff_tm = now_tm - os.path.getmtime(path_folder + '/' + f)
                if diff_tm > 120 and os.path.getsize(path_folder + '/' + f) == 0:  # Detect empty files > 2 minutes
                    os.remove(path_folder + '/' + f)
                    emptyfd += 1
                if diff_tm > 31536000:  # Detect old files > 365 days old
                    os.remove(path_folder + '/' + f)
                    oldfd = oldfd + 1
            self.logAutoDB("[AutoDB] {} old file(s) removed".format(oldfd))
            self.logAutoDB("[AutoDB] {} empty file(s) removed".format(emptyfd))
            self.logAutoDB("[AutoDB] *** Stopping ***")

    def logAutoDB(self, logmsg):
        import traceback
        try:
            with open("/tmp/PosterAutoDB.log", "a") as w:
                w.write("%s\n" % logmsg)
        except Exception as e:
            print('logAutoDB error', str(e))
            traceback.print_exc()


threadAutoDB = PosterAutoDB()
threadAutoDB.start()


class zPosterX(Renderer):
    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        self.nxts = 0
        self.path = path_folder  # + '/'
        self.canal = [None, None, None, None, None, None]
        self.oldCanal = None
        self.logdbg = None
        self.pstcanal = None
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.showPoster)
        except:
            self.timer.callback.append(self.showPoster)
        self.timer.start(10, True)

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
            if self.instance:
                self.instance.hide()
            return
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
                        if PY3:
                            self.canal[2] = self.source.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                        else:
                            self.canal[2] = self.source.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                        self.canal[3] = self.source.event.getExtendedDescription()
                        self.canal[4] = self.source.event.getShortDescription()
                        self.canal[5] = self.canal[2]
                    servicetype = "Event"
                if service is not None:
                    events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
                    if PY3:
                        self.canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')  # .encode('utf-8')
                    else:
                        self.canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                    self.canal[1] = events[self.nxts][1]
                    self.canal[2] = events[self.nxts][4]
                    self.canal[3] = events[self.nxts][5]
                    self.canal[4] = events[self.nxts][6]
                    self.canal[5] = self.canal[2]
                    if not autobouquet_file:
                        if self.canal[0] not in apdb:
                            apdb[self.canal[0]] = service.toString()
            except Exception as e:
                self.logPoster("Error (service) : " + str(e))
                if self.instance:
                    self.instance.hide()
                return
            if not servicetype or servicetype is None:
                self.logPoster("Error service type undefined")
                if self.instance:
                    self.instance.hide()
                return
            try:
                curCanal = "{}-{}".format(self.canal[1], self.canal[2])
                if curCanal == self.oldCanal:
                    return
                self.oldCanal = curCanal
                self.logPoster("Service: {} [{}] : {} : {}".format(servicetype, self.nxts, self.canal[0], self.oldCanal))
                self.pstcanal = convtext(self.canal[5])
                if self.pstcanal is not None:
                    self.pstrNm = self.path + '/' + str(self.pstcanal) + ".jpg"
                    self.pstcanal = str(self.pstrNm)
                if os.path.exists(self.pstcanal):
                    self.timer.start(10, True)
                else:
                    canal = self.canal[:]
                    pdb.put(canal)
                    start_new_thread(self.waitPoster, ())
            except Exception as e:
                self.logPoster("Error (eFile): " + str(e))
                if self.instance:
                    self.instance.hide()
                return

    def showPoster(self):
        if self.instance:
            self.instance.hide()
        if self.canal[5]:
            if self.pstcanal is not None and not os.path.exists(self.pstcanal):
                self.pstcanal = convtext(self.canal[5])
                if self.pstcanal is not None:
                    self.pstrNm = self.path + '/' + str(self.pstcanal) + ".jpg"
                    self.pstcanal = str(self.pstrNm)
                else:
                    print('showPoster----')
                    self.pstcanal = noposter
            if os.path.exists(self.pstcanal):
                print('showPoster----')
                self.logPoster("[LOAD : showPoster] {}".format(self.pstcanal))
                self.instance.setPixmap(loadJPG(self.pstcanal))
                self.instance.setScale(1)
                self.instance.show()

    def waitPoster(self):
        if self.instance:
            self.instance.hide()
        if self.canal[5]:
            if self.pstcanal is not None and not os.path.exists(self.pstcanal):
                self.pstcanal = convtext(self.canal[5])
                if self.pstcanal is not None:
                    self.pstrNm = self.path + '/' + str(self.pstcanal) + ".jpg"
                    self.pstcanal = str(self.pstrNm)
            loop = 180
            found = None
            self.logPoster("[LOOP: waitPoster] {}".format(self.pstcanal))
            while loop >= 0:
                if self.pstcanal is not None and os.path.exists(self.pstcanal):
                    loop = 0
                    found = True
                time.sleep(0.5)
                loop = loop - 1
            if found:
                self.timer.start(20, True)

    def logPoster(self, logmsg):
        import traceback
        try:
            with open("/tmp/logPosterXx.log", "a") as w:
                w.write("%s\n" % logmsg)
        except Exception as e:
            print('logPoster error:', str(e))
            traceback.print_exc()
