#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng
# v1 07.2020, 11.2021
# recode from lululla 2022
# for channellist
# <widget source="ServiceEvent" render="zStarX" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# or
# <widget source="ServiceEvent" render="zStarX" pixmap="xtra/star.png" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# edit lululla 05-2022
# <ePixmap pixmap="oZeta-FHD/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Now" render="zStarX" pixmap="oZeta-FHD/menu/staryellow.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="menu/stargrey.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Next" render="zStarX" pixmap="oZeta-FHD/menu/staryellow.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />

from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
# from Components.Sources.ServiceEvent import ServiceEvent
from Components.VariableValue import VariableValue
from enigma import eSlider
from Components.config import config
from enigma import eTimer
import re
import json
import os
import socket
import sys


global cur_skin, my_cur_skin, tmdb_api
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote
else:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass
print('language: ', lng)


formatImg = 'w185'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
# thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


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


def checkRedirect(url):
    # print("*** check redirect ***")
    import requests
    from requests.adapters import HTTPAdapter, Retry
    hdr = {"User-Agent": "Enigma2 - Enigma2 Plugin"}
    content = ""
    retries = Retry(total=1, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retries)
    http = requests.Session()
    http.mount("http://", adapter)
    http.mount("https://", adapter)
    try:
        r = http.get(url, headers=hdr, timeout=(10, 30), verify=False)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            try:
                content = r.json()
            except Exception as e:
                print(e)
        return content
    except Exception as e:
        print('next ret: ', e)
        return content


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


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


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def transEpis(text):
    text = text.lower() + '+FIN'
    text = text.replace('  ', '+').replace(' ', '+').replace('&', '+').replace(':', '+').replace('_', '+').replace('u.s.', 'us').replace('l.a.', 'la').replace('.', '+').replace('"', '+').replace('(', '+').replace(')', '+').replace('[', '+').replace(']', '+').replace('!', '+').replace('++++', '+').replace('+++', '+').replace('++', '+')
    text = text.replace('+720p+', '++').replace('+1080i+', '+').replace('+1080p+', '++').replace('+dtshd+', '++').replace('+dtsrd+', '++').replace('+dtsd+', '++').replace('+dts+', '++').replace('+dd5+', '++').replace('+5+1+', '++').replace('+3d+', '++').replace('+ac3d+', '++').replace('+ac3+', '++').replace('+avchd+', '++').replace('+avc+', '++').replace('+dubbed+', '++').replace('+subbed+', '++').replace('+stereo+', '++')
    text = text.replace('+x264+', '++').replace('+mpeg2+', '++').replace('+avi+', '++').replace('+xvid+', '++').replace('+blu+', '++').replace('+ray+', '++').replace('+bluray+', '++').replace('+3dbd+', '++').replace('+bd+', '++').replace('+bdrip+', '++').replace('+dvdrip+', '++').replace('+rip+', '++').replace('+hdtv+', '++').replace('+hddvd+', '++')
    text = text.replace('+german+', '++').replace('+ger+', '++').replace('+english+', '++').replace('+eng+', '++').replace('+spanish+', '++').replace('+spa+', '++').replace('+italian+', '++').replace('+ita+', '++').replace('+russian+', '++').replace('+rus+', '++').replace('+dl+', '++').replace('+dc+', '++').replace('+sbs+', '++').replace('+se+', '++').replace('+ws+', '++').replace('+cee+', '++')
    text = text.replace('+remux+', '++').replace('+directors+', '++').replace('+cut+', '++').replace('+uncut+', '++').replace('+extended+', '++').replace('+repack+', '++').replace('+unrated+', '++').replace('+rated+', '++').replace('+retail+', '++').replace('+remastered+', '++').replace('+edition+', '++').replace('+version+', '++')
    text = text.replace('\xc3\x9f', '%C3%9F').replace('\xc3\xa4', '%C3%A4').replace('\xc3\xb6', '%C3%B6').replace('\xc3\xbc', '%C3%BC')
    text = re.sub('\\+tt[0-9]+\\+', '++', text)
    text = re.sub('\\+\\+\\+\\+.*?FIN', '', text)
    text = re.sub('\\+FIN', '', text)
    return text


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            print('original text: ', text)
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
            text = text.lower()
            text = text.replace('studio aperto mag', 'Studio Aperto')
            text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('primatv', '').replace('1^tv', '')
            text = text.replace(' prima pagina', '').replace(' -20.30', '').replace(': parte 2', '').replace(': parte 1', '')
            if text.endswith("the"):
                text.rsplit(" ", 1)[0]
                text = text.rsplit(" ", 1)[0]
                text = "the " + str(text)
                print('the from last to start text: ', text)
            text = text + 'FIN'
            text = re.sub("[^\w\s]", "", text)  # remove .
            text = re.sub(' - [Ss][0-9]+[Ee][0-9]+.*?FIN', '', text)
            text = re.sub('[Ss][0-9]+[Ee][0-9]+.*?FIN', '', text)
            text = re.sub(' - [Ss][0-9] [Ee][0-9]+.*?FIN', '', text)            
            text = re.sub('[Ss][0-9] [Ee][0-9]+.*?FIN', '', text)
            text = text.replace('(', '').replace(')', '')
            print('[()] ', text)
            # print(' - +.*?FIN:INIT ', text)
            text = re.sub(' - +.*?FIN', '', text) 
            # print(' - +.*?FIN:END ', text)
            text = re.sub('FIN', '', text)
            # text = transEpis(text)
            # text = text.replace('+', ' ')
            # print('transEpis text: ', text)
            text = text.replace('(', '').replace(')', '')
            print('[()] ', text)
            text = text.replace('  ', ' ').replace(' - ', ' ').replace(' - "', '')
            # text = REGEX.sub('', text)  # paused
            # # add
            # text = text.replace("\xe2\x80\x93","").replace('\xc2\x86', '').replace('\xc2\x87', '') # replace special
            # # add end
            # # add
            # remove || content at start
            text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            # print('^\|[\w\-\|]*\| text: ', text)
            # # remove () content
            # n = 1  # run at least once
            # while n:
                # text, n = re.subn(r'\([^\(\)]*\)', '', text)
            # print('\([^\(\)]*\) text: ', text)
            # # remove [] content
            # n = 1  # run at least once
            # while n:
                # text, n = re.subn(r'\[[^\[\]]*\]', '', text)
            # print('\[[^\[\]]*\] text: ', text)
            # # add end
            # text = re.sub('\ \(\d+\/\d+\)$', '', text)  # remove episode-number " (xx/xx)" at the end
            # text = re.sub('\ \(\d+\)$', '', text)  # remove episode-number " (xxx)" at the end
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            # print('[-,?!/\.\":] text: ', text)
            # text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            # # add
            # text = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', text)  # modifcare questo (remove space from regex)
            # text = re.sub('\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', text)  # modifcare questo (remove space from regex)
            # print('\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', text)
            # # text = text.replace(' ^`^s', '').replace(' ^`^y','')
            # text = re.sub('\Teil\d+$', '', text)
            # text = re.sub('\Folge\d+$', '', text)
            # # add end
            cleanEvent = re.sub('\ \(\d+\)$', '', text) #remove episode-number " (xxx)" at the end
            cleanEvent = re.sub('\ \(\d+\/\d+\)$', '', cleanEvent) #remove episode-number " (xx/xx)" at the end
            text = re.sub('\!+$', '', cleanEvent)
            # text = unicodify(text)
            text = text.capitalize()
            print('Final text: ', text)
        else:
            text = text
        return text
    except Exception as e:
        print('convtext error: ', e)
        pass


class zStarX(VariableValue, Renderer):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.__start = 0
        self.__end = 100
        self.text = ''
        self.timer30 = eTimer()

    GUI_WIDGET = eSlider

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            print('zstar event A what[0] == self.CHANGED_CLEAR')
            (self.range, self.value) = ((0, 1), 0)
            return
        if what[0] != self.CHANGED_CLEAR:
            print('zstar event B what[0] != self.CHANGED_CLEAR')
            if self.instance:
                self.instance.hide()
            try:
                self.timer30.callback.append(self.infos)
            except:
                self.timer30_conn = self.timer30.timeout.connect(self.infos)
            self.timer30.start(50, True)

    def infos(self):
        try:
            rtng = 0
            range = 0
            value = 0
            ImdbRating = "0"
            ids = None
            data = ''
            self.event = self.source.event
            if self.event and self.event != 'None' or self.event is not None:  # and self.instance:
                if PY3:
                    self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')  # .encode('utf-8')
                else:
                    self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                self.evntNm = convtext(self.evnt)
                dwn_infos = "{}/{}".format(path_folder, self.evntNm)
                if not os.path.exists(dwn_infos):
                        OnclearMem()
                        '''
                        try:
                            url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(str(tmdb_api), self.evntNm)
                            if PY3:
                                url = url.encode()
                            url = checkRedirect(url)
                            print('url1:', url)
                            ids = url['results'][0]['id']
                            print('url1 ids:', ids)
                        except:
                        '''
                        try:
                            url = 'http://api.themoviedb.org/3/search/multi?api_key={}&query={}'.format(str(tmdb_api), self.evntNm)
                            if PY3:
                                url = url.encode()
                            url = checkRedirect(url)
                            print('url2:', url)
                            ids = url['results'][0]['id']
                            print('url2 ids:', ids)
                        except Exception as e:
                            print('Exception no ids in zstar ', e)

                        if ids is not None:
                            try:
                                data = 'https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), str(tmdb_api), str(lng))  # &language=" + str(language)
                                if PY3:
                                    import six
                                    data = six.ensure_str(data)
                                print('zstar pass ids Else: ')
                                if data:
                                    data = json.load(urlopen(data))
                                    open(dwn_infos, "w").write(json.dumps(data))
                                else:
                                    data = 'https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), str(tmdb_api), str(lng))  # &language=" + str(language)
                                    if PY3:
                                        import six
                                        data = six.ensure_str(data)
                                    print('zstar pass ids Else: ')
                                    if data:
                                        data = json.load(urlopen(data))
                                        open(dwn_infos, "w").write(json.dumps(data))

                            except Exception as e:
                                print('pass Exception:', e)
                # if os.path.exists(dwn_infos):
                else:
                    try:
                        if not PY3:
                            myFile = open(("%s/%s" % (path_folder, self.evntNm)), 'r')
                            myObject = myFile.read()
                            u = myObject.decode('utf-8-sig')
                            data = u.encode('utf-8')
                            # data.encoding
                            # data.close()
                            data = json.loads(myObject, 'utf-8')
                        else:
                            with open(dwn_infos) as f:
                                data = json.load(f)
                        ImdbRating = ''
                        if "vote_average" in data:
                            ImdbRating = data['vote_average']
                        elif "imdbRating" in data:
                            ImdbRating = data['imdbRating']
                        else:
                            ImdbRating = '0'
                        print('zstar ImdbRating: ', ImdbRating)
                        if ImdbRating and ImdbRating != '0':
                            rtng = int(10 * (float(ImdbRating)))
                        else:
                            rtng = 0
                        range = 100
                        value = rtng
                        (self.range, self.value) = ((0, range), value)
                        self.instance.show()
                    except Exception as e:
                        print('ImdbRating Exception: ', e)
        except Exception as e:
            print('zstar passImdbRating: ', e)

    def postWidgetCreate(self, instance):
        instance.setRange(self.__start, self.__end)

    def setRange(self, range):
        (self.__start, self.__end) = range
        if self.instance is not None:
            self.instance.setRange(self.__start, self.__end)

    def getRange(self):
        return self.__start, self.__end

    range = property(getRange, setRange)
