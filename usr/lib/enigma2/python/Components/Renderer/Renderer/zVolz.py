#!/usr/bin/python
# -*- coding: utf-8 -*-

# <screen name="Volume" position="1550,60" size="150,135" zPosition="10" backgroundColor="transparent" title="Volume" flags="wfNoBorder">
# <ePixmap position="3,0" size="150,135" pixmap="volume/volon.png" transparent="1" zPosition="-1" />
# <widget source="global.CurrentTime" render="zVolz" path="/volume/" zPosition="5" position="0,1" size="150,135" alphatest="blend" transparent="1" />
# <widget name="VolumeText" position="44,104" size="60,30" font="Regular; 32" foregroundColor="ltbluette" backgroundColor="background" halign="center" valign="center" transparent="1" zPosition="20" />
# </screen>
# init from lululla 2023
# by Lululla  @
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadPNG
from enigma import eDVBVolumecontrol
from Components.config import config
import sys
import os

PY3 = (sys.version_info[0] == 3)
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


class zVolz(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.pth = "/volume/"
        self.vol_timer = eTimer()
        self.vol_timer.callback.append(self.pollme)

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value,) in self.skinAttributes:
            if attrib == "path":
                self.pth = value
            attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.suspended:
            value = str(eDVBVolumecontrol.getInstance().getVolume())
            png = ('/usr/share/enigma2/' + cur_skin + self.pth + value + '.png')
            if PY3:
                png = png
            else:
                png = png.encode()
            if os.path.exists(png):
                self.instance.setPixmap(loadPNG(png))

    def pollme(self):
        self.changed(None)
        return

    def onShow(self):
        self.suspended = False
        self.vol_timer.start(200)

    def onHide(self):
        self.suspended = True
        self.vol_timer.stop()
