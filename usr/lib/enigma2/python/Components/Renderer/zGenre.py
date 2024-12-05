#!/usr/bin/python
# -*- coding: utf-8 -*-

# edit lululla to 30.07.2022
# channelselections
# <widget render="zGenre" source="ServiceEvent" position="793,703" size="300,438" zPosition="3" transparent="1" />
# infobar
# <widget render="zGenre" source="session.Event_Now" position="54,315" size="300,438" zPosition="22" transparent="1" />
# <widget render="zGenre" source="session.Event_Next" position="54,429" size="300,438" zPosition="22" transparent="1" />
# recode from lululla 2023
from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.config import config
from enigma import (
    ePixmap,
    loadPNG,
)
import re
import json
import os
import sys
from .Converlibr import convtext

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True


def isMountedInRW(mount_point):
    with open("/proc/mounts", "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) > 1 and parts[1] == mount_point:
                return True
    return False


curskin = config.skin.primary_skin.value.replace('/skin.xml', '')
PIC_PATH = '/usr/share/enigma2/%s/genre_pic/' % curskin
found = False
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


class zGenre(Renderer):

    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        if what[0] != self.CHANGED_CLEAR:
            if self.instance:
                self.instance.hide()
            self.delay()

    def delay(self):
        global found
        self.pstrNm = ''
        genreTxt = None
        self.event = self.source.event
        if not self.event:
            return

        if self.event and self.event != 'None' or self.event is not None:
            try:
                if PY3:
                    self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')  # .encode('utf-8')
                else:
                    self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')

                self.evntNm = convtext(self.evnt)
                infos_file = "{}/{}".format(path_folder, self.evntNm)
                if os.path.exists(infos_file):
                    with open(infos_file) as f:
                        genreTxt = json.load(f)['Genre']
                        genreTxt = genreTxt.split(",")[0]
                        print('genreTxt name: ', genreTxt)

                if genreTxt is not None:
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
                                11: ('Original Language', 'Black & White', 'Unpublished', 'Live Broadcast'),
                                12: ('Adventure'),
                                14: ('Fantasy'),
                                16: ('Animation'),
                                18: ('Drama'),
                                27: ('Horror', 'Thriller'),
                                28: ('Action'),
                                35: ('Comedy'),
                                36: ('History'),
                                37: ('Western'),
                                53: ('Thriller', 'Horror'),
                                80: ('Crime'),
                                99: ('Documentary'),
                                878: ('Science Fiction', 'Science', 'Fiction'),
                                9648: ('Mystery'),
                                10402: ('Music'),
                                10751: ('Family'),
                                10752: ('War'),
                                10759: ('Action & Adventure', 'Action', 'Adventure'),
                                10762: ('Kids'),
                                10763: ('News'),
                                10764: ('Reality'),
                                10765: ('Sci-Fi & Fantasy', 'Sci-Fi', 'Fantasy'),
                                10766: ('Soap'),
                                10767: ('Talk'),
                                10768: ('War & Politics '),
                                10770: ('TV Movie')}.get(gData.getLevel1(), "")[gData.getLevel2()]
                    except:
                        pass
                print('Genre Txt 11 : ', genreTxt)
                png = "%s%s.png" % (PIC_PATH, re.sub("[^0-9a-z]+", "_", genreTxt.lower()).replace("__", "_").strip("_"))
                if os.path.exists(png):
                    found = True
                    print('PNG name: ', png)
                    if not PY3:
                        png = png.encode()
                    self.instance.setPixmap(loadPNG(png))
                    self.instance.setScale(1)
                    self.instance.show()

                if not found:
                    try:
                        print('No Found Genre : ', found)
                        return genreTxt
                    except:
                        print('except No Found GenreTxt: ')
                        if self.instance:
                            self.instance.hide()
            except Exception as e:
                print('zGenre error get event: ',  str(e))
                pass
