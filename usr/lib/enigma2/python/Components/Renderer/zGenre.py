#!/usr/bin/python
# -*- coding: utf-8 -*-

# edit lululla to 30.07.2022
# recode from lululla 2023
# channelselections
# <widget render="zGenre" source="ServiceEvent" position="793,703" size="300,438" zPosition="3" transparent="1" />
# infobar
# <widget render="zGenre" source="session.Event_Now" position="54,315" size="300,438" zPosition="22" transparent="1" />
# <widget render="zGenre" source="session.Event_Next" position="54,429" size="300,438" zPosition="22" transparent="1" />

from __future__ import unicode_literals
from Components.Renderer.Renderer import Renderer
from Components.Sources.ServiceEvent import ServiceEvent
from enigma import ePixmap, loadPNG
from Components.config import config
import re
import json
import os
import sys
import unicodedata

PY3 = (sys.version_info[0] == 3)

try:
    unicode = str
    from urllib.parse import quote
except:
    from urllib import quote


curskin = config.skin.primary_skin.value.replace('/skin.xml', '')
PIC_PATH = '/usr/share/enigma2/%s/genre_pic/' % curskin
found = False


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


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            text = REGEX.sub('', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = text.replace('PrimaTv', '').replace(' mag', '')
            text = unicodify(text)
            text = text.lower()
        else:
            text = text
        return text
    except Exception as e:
        print('convtext error: ', e)
        pass


class zGenre(Renderer):

    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        if what[0] != self.CHANGED_CLEAR:
            self.instance.hide()
            self.delay()

    def delay(self):
        global found
        self.pstrNm = ''
        genreTxt = ''
        self.event = self.source.event
        if not self.event:
            return
        if self.event and self.event != 'None' or self.event != None:
            try:
                self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                self.evntNm = convtext(self.evnt)
                infos_file = "{}/{}".format(path_folder, self.evntNm)
                if os.path.exists(infos_file):
                    with open(infos_file) as f:
                        genreTxt = json.load(f)['Genre']
                        genreTxt = genreTxt.split(",")[0]
                        print('genreTxt name: ', genreTxt)
                if genreTxt != '':
                    try:
                        gData = self.event.getGenreData()
                        if gData:
                            genreTxt = {
                                        1: ('N/A', 'Action', 'Thriller', 'Drama', 'Movie', 'Detective', 'Mistery', 'Adventure', 'Science', 'Animation', 'Comedy', 'Serie', 'Romance', 'Serious', 'Adult'),
                                        2: ('News', 'Weather', 'Magazine', 'Docu', 'Disc', 'Documetary'),
                                        3: ('Show', 'Quiz', 'Variety', 'Talk'),
                                        4: ('Sports', 'Special', 'Sports Magazine', 'Football', 'Tennis', 'Team Sports', 'Athletics', 'Motor Sport', 'Water Sport', 'Winter Sport', 'Equestrian', 'Martial Sports'),
                                        5: ("Childrens", "Children", 'entertainment (6-14)', 'entertainment (10-16)', 'Information', 'Cartoon'),
                                        6: ('Music', 'Rock/Pop', 'Classic Music', 'Folk', 'Jazz', 'Musical/Opera', 'Ballet'),
                                        7: ('Arts', 'Performing Arts', 'Fine Arts', 'Religion', 'PopCulture', 'Literature', 'Cinema', 'ExpFilm', 'Press', 'New Media', 'Culture', 'Fashion'),
                                        8: ('Social', 'Magazines', 'Economics', 'Remarkable People'),
                                        9: ('Education', 'Nature/Animals/', 'Technology', 'Medicine', 'Expeditions', 'Social', 'Further Education', 'Languages'),
                                        10: ('Hobbies', 'Travel', 'Handicraft', 'Motoring', 'Fitness', 'Cooking', 'Shopping', 'Gardening'),
                                        11: ('Original Language', 'Black & White', 'Unpublished', 'Live Broadcast')
                                        }.get(gData.getLevel1(), "")[gData.getLevel2()]
                    except:
                        pass
                print('Genre Txt 11 : ', genreTxt)
                png = "%s%s.png" % (PIC_PATH, re.sub("[^0-9a-z]+", "_", genreTxt.lower()).replace("__", "_").strip("_"))
                if os.path.exists(png):
                    found = True
                    print('PNG name: ', png)
                    if PY3:
                        png = png
                    else:
                        png = png.encode()
                    self.instance.setPixmap(loadPNG(png))
                    self.instance.setScale(1)
                    self.instance.show()
                    # return
                if not found:
                    try:
                        print('No Found Genre : ', found)
                        return genreTxt
                    except:
                        print('except No Found GenreTxt: ')
                        self.instance.hide()
            except Exception as e:
                print('error get event: ',  str(e))
                pass
