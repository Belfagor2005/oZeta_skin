#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020
# file for skin MetriXconfluencExp by sunriser 07.2021
# <widget render="zParental" source="session.Event_Now" position="315,874" size="50,50" zPosition="3" transparent="1" alphatest="blend"/>
from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.config import config
from enigma import ePixmap, eTimer, loadPNG
import json
import re
import os

curskin = config.skin.primary_skin.value.replace('/skin.xml', '')
pratePath = '/usr/share/enigma2/%s/parental' % curskin
print('patch fsk', pratePath)


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


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cleantitle(text=''):
    try:
        print('zStarX text ->>> ', text)
        if text != '' or text is not None or text != 'None':
            text = REGEX.sub('', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = unicodify(text)
            text = text.lower()
            print('zStarX text <<<- ', text)
        else:
            text = str(text)
            print('zStarX text <<<->>> ', text)
        return text
    except Exception as e:
        print('cleantitle error: ', e)
        pass


class zParental(Renderer):

    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        try:
            if not self.instance:
                return
            if what[0] == self.CHANGED_CLEAR:
                self.instance.hide()
            if what[0] != self.CHANGED_CLEAR:
                self.delay()
        except:
            pass

    def showParental(self):
        self.event = self.source.event
        if not self.event:
            return
        fd = "{}\n{}\n{}".format(self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
        try:
            pattern = ["\d{1,2}\+"]
            for i in pattern:
                age = re.search(i, fd)
                if age:
                    cert = re.sub("\+", "", age.group()).strip()
                else:
                    try:
                        # eventNm = REGEX.sub("", self.event.getEventName())
                        # eventNm = eventNm.replace('ё', 'е').strip()
                        # infos_file = "{}{}.json".format(path_folder, eventNm)

                        self.evnt = self.event.getEventName().encode('utf-8')
                        self.evntNm = cleantitle(self.evnt)
                        print('clean zInfoEvents: ', self.evntNm)
                        infos_file = "{}/{}".format(path_folder, self.evntNm)

                        if infos_file:
                            with open(infos_file) as f:
                                age = json.load(f)['Rated']
                                cert = {
                                        "TV-G": "0",
                                        "G": "0",
                                        "TV-Y7": "6",
                                        "TV-Y": "6",
                                        "TV-10": "10",
                                        "TV-12": "12",
                                        "TV-14": "14",
                                        "TV-PG": "16",
                                        "PG-13": "16",
                                        "PG": "16",
                                        "TV-MA": "18",
                                        "R": "18",
                                        "N/A": "UN",
                                        "Not Rated": "UN",
                                        "Unrated": "UN",
                                        "": "UN",
                                        "Passed": "UN", }.get(age)
                    except:
                        pass
                if cert:
                    self.instance.setPixmap(loadPNG(os.path.join(pratePath, "FSK_{}.png".format(cert))))
                    self.instance.show()
                else:
                    self.instance.hide()
        except:
            self.instance.hide()

    def delay(self):
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.showParental)
        except:
            self.timer.callback.append(self.showParental)
        self.timer.start(50, True)
