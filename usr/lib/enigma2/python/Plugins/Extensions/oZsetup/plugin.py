#!/usr/bin/python
# -*- coding: utf-8 -*-

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#  Lululla coder and MMark skinner 2022.07.20
#  NOT REMOVE DISCLAIMER!!!
from __future__ import absolute_import
from . import _
from .addons import Uri
from .addons.Utils import RequestAgent
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import configfile
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigOnOff
from Components.config import ConfigSubsection, getConfigListEntry
from Components.config import ConfigSelection, ConfigText
from Components.config import NoSave, ConfigNothing, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import fileExists
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename
from enigma import ePicLoad, loadPic, eTimer
import os
import sys
import time
import re

global my_cur_skin, zaddon
PY3 = sys.version_info.major >= 3
thisdir = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('oZsetup'))
my__skin = config.skin.primary_skin.value.replace('/skin.xml', '')
cur_skin = 'oZeta-FHD'
if str(my__skin) == 'oZeta-FHD':
    my__skin = 'oZeta-FHD'
OAWeather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('OAWeather'))
weatherz = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('WeatherPlugin'))
theweather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TheWeather'))
SkinSelectorD = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('SystemPlugins/SkinSelector'))
SkinSelectorE = '/usr/lib/enigma2/python/Screens/SkinSelector.pyo'
SkinSelectorF = '/usr/lib/enigma2/python/Screens/SkinSelector.pyc'
zaddon = False
zaddons = os.path.join(thisdir, 'addons')
if os.path.exists(zaddons):
    zaddon = True
my_cur_skin = False
_firstStartZ = True
mvi = '/usr/share/'
tmdb_skin = "%senigma2/%s/apikey" % (mvi, cur_skin)
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_skin = "%senigma2/%s/omdbkey" % (mvi, cur_skin)
omdb_api = "cb1d9f55"
visual_skin = "/etc/enigma2/VisualWeather/apikey.txt"
visual_api = "5KAUFAYCDLUYVQPNXPN3K24V5"
thetvdb_skin = "%senigma2/%s/thetvdbkey" % (mvi, cur_skin)
thetvdbkey = 'D19315B88B2DE21F'
welcome = 'WELCOME Z USER\nfrom\nLululla and Mmark'
tarfile = '/tmp/download.tar'
#  -----------------

XStreamity = False
if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/XStreamity'):
    XStreamity = True

try:
    if my_cur_skin is False:
        if fileExists(tmdb_skin):
            with open(tmdb_skin, "r") as f:
                tmdb_api = f.read()
        if fileExists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
        if fileExists(visual_skin):
            with open(visual_skin, "r") as f:
                visual_api = f.read()
        if fileExists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
        my_cur_skin = True
except:
    my_cur_skin = False
    pass

Uri.imagevers()
#  config section - ===========
version = '3.0'
descplug = 'Customization tool for oZeta Skin v.%s' % version
plugindesc = 'Manage your oZeta Skin v.%s' % version
iconpic = 'plugin.png'
sample = mvi + 'enigma2/' + cur_skin + '/zSetup/zSample'
config.ozeta = ConfigSubsection()
ozetamenupredefinedlist = []
ozetainfobarpredefinedlist = []
ozetainfobarsecpredefinedlist = []
ozetachannelselectionpredefinedlist = []
ozetavolumepredefinedlist = []
ozetaradiopredefinedlist = []
ozetamediaplayerpredefinedlist = []
ozetaeventviewpredefinedlist = []
ozetapluginspredefinedlist = []
ozetaalogopredefinedlist = []
ozetablogopredefinedlist = []
ozetamvipredefinedlist = []

config.ozeta.actapi = NoSave(ConfigOnOff(default=False))
config.ozeta.data = NoSave(ConfigOnOff(default=False))
config.ozeta.api = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.txtapi = ConfigText(default=tmdb_api, visible_width=50, fixed_size=False)
config.ozeta.data2 = NoSave(ConfigOnOff(default=False))
config.ozeta.api2 = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.txtapi2 = ConfigText(default=omdb_api, visible_width=50, fixed_size=False)
config.ozeta.data3 = NoSave(ConfigOnOff(default=False))
config.ozeta.api3 = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.txtapi3 = ConfigText(default=visual_api, visible_width=50, fixed_size=False)
config.ozeta.data4 = NoSave(ConfigOnOff(default=False))
config.ozeta.api4 = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.txtapi4 = ConfigText(default=thetvdbkey, visible_width=50, fixed_size=False)
config.ozeta.mmpicons = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.update = NoSave(ConfigOnOff(default=False))
config.ozeta.upfind = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.upconponent = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.options = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.zweather = NoSave(ConfigOnOff(default=False))
config.ozeta.weather = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.oaweather = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.theweather = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.city = ConfigText(default='', visible_width=50, fixed_size=False)
config.ozeta.FirstMenuFHD = ConfigSelection(default='Menu Default', choices=ozetamenupredefinedlist)
config.ozeta.FirstInfobarFHD = ConfigSelection(default='InfoBar Default', choices=ozetainfobarpredefinedlist)
config.ozeta.SecondInfobarFHD = ConfigSelection(default='SecondInfoBar Default', choices=ozetainfobarsecpredefinedlist)
config.ozeta.ChannSelectorFHD = ConfigSelection(default='Channel Default', choices=ozetachannelselectionpredefinedlist)
config.ozeta.VolumeFHD = ConfigSelection(default='Volume Default', choices=ozetavolumepredefinedlist)
config.ozeta.RadioFHD = ConfigSelection(default='RadioInfoBar Default', choices=ozetaradiopredefinedlist)
config.ozeta.MediaPlayerFHD = ConfigSelection(default='MediaPlayer Default', choices=ozetamediaplayerpredefinedlist)
config.ozeta.EventviewFHD = ConfigSelection(default='Eventview Default', choices=ozetaeventviewpredefinedlist)
config.ozeta.PluginsFHD = ConfigSelection(default='PluginBrowser Default', choices=ozetapluginspredefinedlist)
config.ozeta.LogoaFHD = ConfigSelection(default='TopLogo Default', choices=ozetaalogopredefinedlist)
config.ozeta.LogobFHD = ConfigSelection(default='BottomLogo Default', choices=ozetablogopredefinedlist)
config.ozeta.Logoboth = ConfigSelection(default='Bootlogo Default', choices=ozetamvipredefinedlist)
config.ozeta.XStreamity = NoSave(ConfigSelection(['-> Ok']))
config.ozeta.fake = NoSave(ConfigNothing())

#  parameters - =============
try:
    f = os.listdir('%s/' % sample)
except:
    f = []
if f:
    for line in f:
        # print('file line ', line)
        parts = line.split()
        ozetaline = parts[0][:-4]
        # print("********** Find %s" % ozetaline)
        if 'menu_' in ozetaline:
            ozetamenu = ozetaline[5:].replace("-", " ")
            ozetamenupredefinedlist.append(ozetamenu)
        if 'bootlogo_' in ozetaline:
            ozetabootlogo = ozetaline[9:].replace("-", " ")
            ozetamvipredefinedlist.append(ozetabootlogo)
        if 'infobar_' in ozetaline:
            ozetainfobar = ozetaline[8:].replace("-", " ")
            ozetainfobarpredefinedlist.append(ozetainfobar)
        if 'second_' in ozetaline:
            ozetasecinfobar = ozetaline[7:].replace("-", " ")
            ozetainfobarsecpredefinedlist.append(ozetasecinfobar)
        if 'channel_' in ozetaline:
            ozetachannelselection = ozetaline[8:].replace("-", " ")
            ozetachannelselectionpredefinedlist.append(ozetachannelselection)
        if 'volume_' in ozetaline:
            ozetavolume = ozetaline[7:].replace("-", " ")
            ozetavolumepredefinedlist.append(ozetavolume)
        if 'radio_' in ozetaline:
            ozetaradio = ozetaline[6:].replace("-", " ")
            ozetaradiopredefinedlist.append(ozetaradio)
        if 'mediaplayer_' in ozetaline:
            ozetamediaplayer = ozetaline[12:].replace("-", " ")
            ozetamediaplayerpredefinedlist.append(ozetamediaplayer)
        if 'eventview_' in ozetaline:
            ozetaeventview = ozetaline[10:].replace("-", " ")
            ozetaeventviewpredefinedlist.append(ozetaeventview)
        if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
            if 'plugins_' in ozetaline:
                ozetaplugins = ozetaline[8:].replace("-", " ")
                ozetapluginspredefinedlist.append(ozetaplugins)
        if 'alogo_' in ozetaline:
            ozetalogo = ozetaline[6:].replace("-", " ")
            ozetaalogopredefinedlist.append(ozetalogo)
        if 'blogo_' in ozetaline:
            ozetalogob = ozetaline[6:].replace("-", " ")
            ozetablogopredefinedlist.append(ozetalogob)
    ozetamenupredefinedlist.sort()
    ozetainfobarpredefinedlist.sort()
    ozetainfobarsecpredefinedlist.sort()
    ozetachannelselectionpredefinedlist.sort()
    ozetavolumepredefinedlist.sort()
    ozetaradiopredefinedlist.sort()
    ozetamediaplayerpredefinedlist.sort()
    ozetaeventviewpredefinedlist.sort()
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
        ozetapluginspredefinedlist.sort()
    ozetamvipredefinedlist.sort()
    ozetaalogopredefinedlist.sort()
    ozetablogopredefinedlist.sort()
    if ozetamenupredefinedlist and 'Menu Default' in ozetamenupredefinedlist:
        config.ozeta.FirstMenuFHD = ConfigSelection(default='Menu Default', choices=ozetamenupredefinedlist)
    else:
        config.ozeta.FirstMenuFHD = ConfigSelection(choices=ozetamenupredefinedlist)
    if ozetainfobarpredefinedlist and 'InfoBar Default' in ozetainfobarpredefinedlist:
        config.ozeta.FirstInfobarFHD = ConfigSelection(default='InfoBar Default', choices=ozetainfobarpredefinedlist)
    else:
        config.ozeta.FirstInfobarFHD = ConfigSelection(choices=ozetainfobarpredefinedlist)
    if ozetainfobarsecpredefinedlist and 'SecondInfoBar Default' in ozetainfobarsecpredefinedlist:
        config.ozeta.SecondInfobarFHD = ConfigSelection(default='SecondInfoBar Default', choices=ozetainfobarsecpredefinedlist)
    else:
        config.ozeta.SecondInfobarFHD = ConfigSelection(choices=ozetainfobarsecpredefinedlist)
    if ozetachannelselectionpredefinedlist and 'Channel Default' in ozetachannelselectionpredefinedlist:
        config.ozeta.ChannSelectorFHD = ConfigSelection(default='Channel Default', choices=ozetachannelselectionpredefinedlist)
    else:
        config.ozeta.ChannSelectorFHD = ConfigSelection(choices=ozetachannelselectionpredefinedlist)
    if ozetavolumepredefinedlist and 'Volume Default' in ozetavolumepredefinedlist:
        config.ozeta.VolumeFHD = ConfigSelection(default='Volume Default', choices=ozetavolumepredefinedlist)
    else:
        config.ozeta.VolumeFHD = ConfigSelection(choices=ozetavolumepredefinedlist)
    if ozetaradiopredefinedlist and 'RadioInfoBar Default' in ozetaradiopredefinedlist:
        config.ozeta.RadioFHD = ConfigSelection(default='RadioInfoBar Default', choices=ozetaradiopredefinedlist)
    else:
        config.ozeta.RadioFHD = ConfigSelection(choices=ozetaradiopredefinedlist)
    if ozetamediaplayerpredefinedlist and 'MediaPlayer Default' in ozetamediaplayerpredefinedlist:
        config.ozeta.MediaPlayerFHD = ConfigSelection(default='MediaPlayer Default', choices=ozetamediaplayerpredefinedlist)
    else:
        config.ozeta.MediaPlayerFHD = ConfigSelection(choices=ozetamediaplayerpredefinedlist)
    if ozetaeventviewpredefinedlist and 'Eventview Default' in ozetaeventviewpredefinedlist:
        config.ozeta.EventviewFHD = ConfigSelection(default='Eventview Default', choices=ozetaeventviewpredefinedlist)
    else:
        config.ozeta.EventviewFHD = ConfigSelection(choices=ozetaeventviewpredefinedlist)
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
        if ozetapluginspredefinedlist and 'PluginBrowser Default' in ozetapluginspredefinedlist:
            config.ozeta.PluginsFHD = ConfigSelection(default='PluginBrowser Default', choices=ozetapluginspredefinedlist)
        else:
            config.ozeta.PluginsFHD = ConfigSelection(choices=ozetapluginspredefinedlist)
    if ozetaalogopredefinedlist and 'TopLogo Default' in ozetaalogopredefinedlist:
        config.ozeta.LogoaFHD = ConfigSelection(default='TopLogo Default', choices=ozetaalogopredefinedlist)
    else:
        config.ozeta.LogoaFHD = ConfigSelection(choices=ozetaalogopredefinedlist)
    if ozetablogopredefinedlist and 'BottomLogo Default' in ozetablogopredefinedlist:
        config.ozeta.LogobFHD = ConfigSelection(default='BottomLogo Default', choices=ozetablogopredefinedlist)
    else:
        config.ozeta.LogobFHD = ConfigSelection(choices=ozetablogopredefinedlist)
    if ozetamvipredefinedlist and 'Bootlogo Default' in ozetamvipredefinedlist:
        config.ozeta.Logoboth = ConfigSelection(default='Bootlogo Default', choices=ozetamvipredefinedlist)
    else:
        config.ozeta.Logoboth = ConfigSelection(choices=ozetamvipredefinedlist)


def fakeconfig(name):
    retr = [
            ['OZETA SKIN PARTS SETUP'],
            ['OZETA SKIN: INSTALLED BUT NOT ACTIVE'],
            ['SKIN PARTS SETUP'],
            ['SERVER API KEY SETUP'],
            ['WEATHER BOX SETUP'],
            ['MISC SETUP'],
            ['API KEY SETUP:'],
            ['TMDB API:'],
            ['OMDB API:'],
            ['THETVDB API:'],
            ['WEATHER:'],
            # ['Install or Update oZeta Skin:'],
            # ['Install/Update/Restore oZeta Skin'],
            # ['Install Options Developer'],
            ['Update Conponent Skin'],
            ['--Load TMDB Apikey'],
            # ['--Set TMDB Apikey'],
            ['--Load OMDB Apikey'],
            # ['--Set OMDB Apikey'],
            ['-Load THETVDB Apikey'],
            # ['--Set THETVDB Apikey'],
            ['Install'],
            ['VisualWeather Plugin API:'],
            ['--Load VISUALWEATHER Apikey'],
            # ['--Set VISUALWEATHER Apikey'],
            ['Install or Open mmPicons Plugin'],
          ]
    for nname in retr:
        if nname[0] in str(name):
            return True
    return False


def localreturn(name):
    retr = [
        ["omdb", "omdb"],
        ["tmdb", "tmdb"],
        ["thetvdb", "thetvdb"],
        ["oaweather ", "oaweather"],
        ["weather", "weather"],
        ["autoupdate", "autoupdate"],
        ["update", "update"],
        ["ok", "ok"],
        ["mmpicons", "mmpicons"],
        ["xstreamity", "xstreamity"],
        ["bootlogo", "bootlogo"],
        ["setup", "setup"],
        ["options", "options"],
        ["preview", "preview"],
        ["tmdb api:", "tmdb api:"],
        ["omdb api:", "omdb api:"],
        ["visualweather api:", "visualweather api:"],
    ]
    for nname in retr:
        if nname[0] in str(name).lower():
            return True
    return False


class oZsetup(ConfigListScreen, Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        global _session
        _session = session
        self.session = session
        skin = os.path.join(thisdir, 'skin/oZsetup.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('oZeta Skin Setup')
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.skinFileTmp = '%senigma2/%s/zSkin/skin_infochannel.tmp' % (mvi, cur_skin)
        self.skinFile = '%senigma2/%s/zSkin/skin_infochannel.xml' % (mvi, cur_skin)
        self.chooseFile = '%s/' % sample
        self.getImg = Uri.imagevers()
        self['Preview'] = Pixmap()
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Save'))
        self['key_yellow'] = Label('')
        if str(my__skin) == 'oZeta-FHD':
            self['key_yellow'] = Label(_('Preview'))
            self['key_blue'] = Label(_('Restart'))
        # self["key_blue"] = StaticText(self.getSkinSelector() is not None and "Skin" or "")
        # self["key_blue"] = Label('Skin')
        # if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
        # self["key_blue"].hide()
        self["HelpWindow"] = Pixmap()
        self["HelpWindow"].hide()
        self["VKeyIcon"] = Pixmap()
        self["VKeyIcon"].hide()
        self['status'] = StaticText()
        self['description'] = Label("SELECT YOUR CHOICE")
        self['author'] = Label('by Lululla')
        self['image'] = Label('')
        self['city'] = Label('')

        self.PicLoad = ePicLoad()
        self.Scale = AVSwitch().getFramebufferScale()
        try:
            self.PicLoad.PictureData.get().append(self.DecodePicture)
        except:
            self.PicLoad_conn = self.PicLoad.PictureData.connect(self.DecodePicture)
        self['actions'] = ActionMap([
            'DirectionActions',
            'EPGSelectActions',
            'MenuActions',
            'NumberActions',
            'OkCancelActions',
            'HelpActions',
            'InfoActions',
            'VirtualKeyboardActions',
            'HotkeyActions',
        ], {
            'left': self.keyLeft,
            'down': self.keyDown,
            'up': self.keyUp,
            'right': self.keyRight,
            'red': self.zExit,
            'green': self.zSave,
            'InfoPressed': self.zHelp,
            'info': self.zHelp,
            'displayHelp': self.zHelp,
            # 'EPGPressed': self.zHelp,
            'yellow': self.ShowPictureFull,
            # 'blue': self.getSkinSelector,
            # 'blue': self.keyOpenSkinselector,
            'blue': self.restrt,
            'menu': self.KeyMenu,
            'showVirtualKeyboard': self.KeyText,
            'ok': self.keyRun,
            '0': self.zDefault,
            '5': self.answercheck,
            'yellowlong': self.answercheck,
            'yellow_long': self.answercheck,
            'cancel': self.zExit}, -2)
        self.createSetup()
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)
        self.current_skin = config.skin.primary_skin.value
        self.onFirstExecBegin.append(self.check_dependencies)
        self.onLayoutFinish.append(self.__layoutFinished)
        self.onLayoutFinish.append(self.UpdatePicture)

    def restrt(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.restrt, MessageBox, _("This operation restart Gui\nDo you really want to continue?"))
        else:
            self.session.open(TryQuitMainloop, 3)

    def passs(self, foo):
        pass

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def check_dependencies(self):
        dependencies = True
        try:
            import requests
        except Exception as e:
            print("**** missing dependencies ***")
            print(e)
            dependencies = False
        if dependencies is False:
            os.chmod("/usr/lib/enigma2/python/Plugins/Extensions/oZsetup/dependencies.sh", 0o0755)
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/oZsetup/dependencies.sh"
            self.session.openWithCallback(self.layoutFinished, Console, title="Checking Python Dependencies", cmdlist=[cmd1], closeOnSuccess=False)
        else:
            if str(my__skin) != 'oZeta-FHD' and os.path.exists('/usr/share/enigma2/oZeta-FHD'):
                text = _("ATTENTION!!\nThe Skin is already installed:\nto activate you must choose from:\nmenu-setup-system-skin\nand select it!\nNow you can only update the installation.")
                self.msg = self.session.openWithCallback(self.passs, MessageBox, text, MessageBox.TYPE_INFO, timeout=5)
            self.layoutFinished()

    def layoutFinished(self):
        if os.path.isdir(weatherz):
            self.UpdateComponents()
        self.createSetup()
        self.zXml()
        # self.UpdatePicture()
        self['image'].setText("%s" % Uri.imagevers())
        self['city'].setText("%s" % str(config.ozeta.city.value))
        self.setTitle(self.setup_title)

    def getSkinSelector(self):
        try:
            SkinSelector = None
            SkinSelectorD = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('SystemPlugins/SkinSelector'))
            SkinSelectorE = '/usr/lib/enigma2/python/Screens/SkinSelector.pyo'
            SkinSelectorF = '/usr/lib/enigma2/python/Screens/SkinSelector.pyc'
            if os.path.exists(SkinSelectorD):
                from Plugins.SystemPlugins.SkinSelector.plugin import SkinSelector
                return SkinSelector
            elif os.path.exists(SkinSelectorE) or os.path.exists(SkinSelectorF):
                from Screens.SkinSelector import SkinSelector
                return SkinSelector
        except Exception as e:
            print(e)

    def keyOpenSkinselector(self):
        try:
            if self.getSkinSelector() is not None:
                self.session.openWithCallback(self.restoreCurrentSkin, self.getSkinSelector())
        except Exception as e:
            print(e)

    def restoreCurrentSkin(self, SkinSelector):
        try:
            print("[oZeta] restore current skin")
            config.skin.primary_skin.value = self.current_skin
            config.skin.primary_skin.save()
        except Exception as e:
            print(e)

    def answercheck(self, answer=None):
        if str(cur_skin) == 'oZeta-FHD':
            if answer is None:
                self.session.openWithCallback(self.answercheck, MessageBox, _("This operation checks if the skin has its components (is not sure)..\nDo you really want to continue?"))
            else:
                if zaddon is True:
                    from .addons import checkskin
                    self.check_module = eTimer()
                    check = checkskin.check_module_skin()
                    try:
                        self.check_module_conn = self.check_module.timeout.connect(check)
                    except:
                        self.check_module.callback.append(check)
                    self.check_module.start(100, True)
                    self.openVi()

    def openVi(self):
        from .addons.type_utils import zEditor
        user_log = '/tmp/debug_my_skin.log'
        if fileExists(user_log):
            self.session.open(zEditor, user_log)

    def _space(self):
        self.list.append(getConfigListEntry(" ", config.ozeta.fake, False))

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        # char = 120
        # tab = " " * 9
        # sep = "-"
        try:
            if str(my__skin) != 'oZeta-FHD' and os.path.exists('/usr/share/enigma2/oZeta-FHD'):
                self.list.append(getConfigListEntry(_("OZETA SKIN: INSTALLED BUT NOT ACTIVE")))
            if str(my__skin) == 'oZeta-FHD':
                self.list.append(getConfigListEntry(("OZETA SKIN PARTS SETUP")))
                self.list.append(getConfigListEntry("Install or Update oZeta Skin:", config.ozeta.update, _("Install or Autoupdate oZeta Plugin & Skin on both")))
                if config.ozeta.update.value is True:
                    self.list.append(getConfigListEntry("Install/Update/Restore oZeta Skin", config.ozeta.upfind, _("Install/Update/Restore Stable Version oZeta Skin\nPress OK")))
                    self.list.append(getConfigListEntry("Install/Update Options Developer", config.ozeta.options, _("Install Test Options oZeta Skin\nPress OK")))
                    self.list.append(getConfigListEntry("Update Conponent Skin", config.ozeta.upconponent, _("Check for Upgradable Conponent Skin\nPress OK")))
                # self.list.append(getConfigListEntry(section + tab + sep * (char - len(section) - len(tab)), config.ozeta.fake, _("SKIN SETUP SECTION")))
                if ozetamenupredefinedlist:
                    self.list.append(getConfigListEntry('Menu:', config.ozeta.FirstMenuFHD, _("Settings Menu Image Panel")))
                if ozetainfobarpredefinedlist:
                    self.list.append(getConfigListEntry('Infobar:', config.ozeta.FirstInfobarFHD, _("Settings Infobar Panels")))
                if ozetainfobarsecpredefinedlist:
                    self.list.append(getConfigListEntry('Second Infobar:', config.ozeta.SecondInfobarFHD, _("Settings SecInfobar Panels")))
                if ozetachannelselectionpredefinedlist:
                    self.list.append(getConfigListEntry('Channel Selection:', config.ozeta.ChannSelectorFHD, _("Settings Channel Panels")))
                if ozetavolumepredefinedlist:
                    self.list.append(getConfigListEntry('Volume Panel:', config.ozeta.VolumeFHD, _("Settings Volume Panels")))
                if ozetaradiopredefinedlist:
                    self.list.append(getConfigListEntry('Radio Panel:', config.ozeta.RadioFHD, _("Settings Radio Panels")))
                if ozetamediaplayerpredefinedlist:
                    self.list.append(getConfigListEntry('MediaPlayer Panel:', config.ozeta.MediaPlayerFHD, _("Settings MediaPlayer Panels")))
                if ozetaeventviewpredefinedlist:
                    self.list.append(getConfigListEntry('Eventview Panel:', config.ozeta.EventviewFHD, _("Settings Eventview Panels")))
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                    if ozetapluginspredefinedlist:
                        self.list.append(getConfigListEntry('PluginBrowser Panel:', config.ozeta.PluginsFHD, _("Settings PluginBrowser Panels")))
                if ozetaalogopredefinedlist:
                    self.list.append(getConfigListEntry('Logo Image Top:', config.ozeta.LogoaFHD, _("Settings Logo Image Top")))
                if ozetablogopredefinedlist:
                    self.list.append(getConfigListEntry('Logo Image Bottom:', config.ozeta.LogobFHD, _("Settings Logo Image Bottom")))
                if ozetamvipredefinedlist:
                    self.list.append(getConfigListEntry('Bootlogo Image:', config.ozeta.Logoboth, _("Settings Bootlogo Image\nPress Ok for change")))

                self.list.append(getConfigListEntry(("SERVER API KEY SETUP")))
                self.list.append(getConfigListEntry("API KEY SETUP:", config.ozeta.actapi, _("Settings oZeta Apikey Server")))
                if config.ozeta.actapi.value is True:
                    self.list.append(getConfigListEntry("TMDB API:", config.ozeta.data, _("Settings TMDB ApiKey")))
                    if config.ozeta.data.value is True:
                        self.list.append(getConfigListEntry("--Load TMDB Apikey", config.ozeta.api, _("Load TMDB Apikey from /tmp/apikey.txt")))
                        self.list.append(getConfigListEntry("--Set TMDB Apikey", config.ozeta.txtapi, _("Signup on TMDB and input free personal ApiKey")))
                    self.list.append(getConfigListEntry("OMDB API:", config.ozeta.data2, _("Settings OMDB APIKEY")))
                    if config.ozeta.data2.value is True:
                        self.list.append(getConfigListEntry("--Load OMDB Apikey", config.ozeta.api2, _("Load OMDB Apikey from /tmp/omdbkey.txt")))
                        self.list.append(getConfigListEntry("--Set OMDB Apikey", config.ozeta.txtapi2, _("Signup on OMDB and input free personal ApiKey")))
                    self.list.append(getConfigListEntry("THETVDB API:", config.ozeta.data4, _("Settings THETVDB APIKEY")))
                    if config.ozeta.data4.value is True:
                        self.list.append(getConfigListEntry("--Load THETVDB Apikey", config.ozeta.api4, _("Load THETVDB Apikey from /tmp/thetvdbkey.txt")))
                        self.list.append(getConfigListEntry("--Set THETVDB Apikey", config.ozeta.txtapi4, _("Signup on THETVDB and input free personal ApiKey")))

            self.list.append(getConfigListEntry(("WEATHER BOX SETUP")))
            self.list.append(getConfigListEntry("WEATHER:", config.ozeta.zweather, _("Settings oZeta Weather")))
            if config.ozeta.zweather.value is True:
                # if os.path.isdir(OAWeather):
                self.list.append(getConfigListEntry("Install or Open OAWeather Plugin", config.ozeta.oaweather, _("Install or Open OAWeather Plugin\nPress OK")))
                self.list.append(getConfigListEntry("Install or Open Weather Plugin", config.ozeta.weather, _("Install or Open Weather Plugin\nPress OK")))
                self.list.append(getConfigListEntry("Install or Open TheWeather Plugin", config.ozeta.theweather, _("Install or Open TheWeather Plugin\nPress OK")))
                if os.path.isdir(weatherz):
                    self.list.append(getConfigListEntry("--Setting Weather City", config.ozeta.city, _("Settings City Weather Plugin")))

                VisualWeather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('VisualWeather'))
                if os.path.isdir(VisualWeather):
                    self.list.append(getConfigListEntry("VisualWeather Plugin API:", config.ozeta.data3, _("Settings VISUALWEATHER APIKEY")))
                    if config.ozeta.data3.value is True:
                        self.list.append(getConfigListEntry("--Load VISUALWEATHER Apikey", config.ozeta.api3, _("Load VISUALWEATHER Apikey from /etc/enigma2/VisualWeather/apikey.txt")))
                        self.list.append(getConfigListEntry("--Set VISUALWEATHER Apikey", config.ozeta.txtapi3, _("Signup on www.visualcrossing.com and input free personal ApiKey")))

            self.list.append(getConfigListEntry(("MISC SETUP")))
            self.list.append(getConfigListEntry("Install or Open mmPicons Plugin", config.ozeta.mmpicons, _("Install or Open mmPicons Plugin\nPress OK")))
            if XStreamity is True:
                self.list.append(getConfigListEntry('Install Skin Zeta for XStreamity Plugin (only FHD)', config.ozeta.XStreamity, _("Install Skin Zeta for XStreamity Plugin (only FHD)\nPress Ok")))

            self["config"].list = self.list
            self["config"].l.setList(self.list)
            # self.handleInputHelpers()
        except KeyError:
            print("keyError")

    def setInfo(self):
        try:
            sel = self['config'].getCurrent()[2]
            if sel:
                self['description'].setText(str(sel))
            else:
                self['description'].setText(_('SELECT YOUR CHOICE'))
            return
        except Exception as e:
            print("Error setInfo ", e)

    def handleInputHelpers(self):
        from enigma import ePoint
        currConfig = self["config"].getCurrent()
        if currConfig is not None:
            if isinstance(currConfig[1], ConfigText):
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(True)
                    except:
                        pass
                    try:
                        self["virtualKeyBoardActions"].setEnabled(True)
                    except:
                        pass
                    self["VKeyIcon"].show()

                if "HelpWindow" in self and currConfig[1].help_window and currConfig[1].help_window.instance is not None:
                    helpwindowpos = self["HelpWindow"].getPosition()
                    currConfig[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))
            else:
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(False)
                    except:
                        pass
                    try:
                        self["virtualKeyBoardActions"].setEnabled(False)
                    except:
                        pass
                    self["VKeyIcon"].hide()

    # def selectionChanged(self):
        # self['status'].setText(self['config'].getCurrent()[0])

    def changedEntry(self):
        self.item = self["config"].getCurrent()
        for x in self.onChangedEntry:
            x()

        try:
            if isinstance(self["config"].getCurrent()[1], ConfigYesNo) or isinstance(self["config"].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass

    def getCurrentEntry(self):
        return self["config"].getCurrent() and self["config"].getCurrent()[0] or ""

    def getCurrentValue(self):
        return self["config"].getCurrent() and str(self["config"].getCurrent()[1].getText()) or ""

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def keyRun(self):
        sel = self["config"].getCurrent()[1]
        if sel and sel == config.ozeta.api:
            self.keyApi()
        if sel and sel == config.ozeta.txtapi:
            self.KeyText()
        if sel and sel == config.ozeta.api2:
            self.keyApi2()
        if sel and sel == config.ozeta.txtapi2:
            self.KeyText()
        if sel and sel == config.ozeta.api3:
            self.keyApi3()
        if sel and sel == config.ozeta.txtapi3:
            self.KeyText()
        if sel and sel == config.ozeta.api4:
            self.keyApi4()
        if sel and sel == config.ozeta.txtapi4:
            self.KeyText()
        if sel and sel == config.ozeta.mmpicons:
            self.mmWaitReload()
        if sel and sel == config.ozeta.options:
            self.upOptions()
        if sel and sel == config.ozeta.upfind:
            self.zWaitReload()
        if sel and sel == config.ozeta.upconponent:
            self.zUpConponent()
        if sel and sel == config.ozeta.XStreamity:
            self.zXStreamity()
        if sel and sel == config.ozeta.Logoboth:
            self.zLogoboth(None)
        if sel and sel == config.ozeta.weather:
            self.KeyMenu()
        if sel and sel == config.ozeta.oaweather:
            self.KeyMenu2()
        if sel and sel == config.ozeta.theweather:
            self.KeyMenu3()
        if sel and sel == config.ozeta.city:
            self.KeyText()
        else:
            return
        return

    def zXStreamity(self, answer=None):
        if XStreamity is True:
            if answer is None:
                self.session.openWithCallback(self.zXStreamity, MessageBox, _('Install Skin Zeta for XStreamity Plugin (only FHD)\nDo you really want to install now?'))
            elif answer:
                try:
                    Options = self.session.openWithCallback(Uri.zXStreamop, MessageBox, _('Install Skin Zeta for XStreamity Plugin (only FHD)...\nPlease Wait'), MessageBox.TYPE_INFO, timeout=4)
                    Options.setTitle(_('Install Skin Zeta for XStreamity Plugin'))
                    print('Install Skin Zeta for XStreamity Plugin - Done!!!')
                    self.createSetup()
                except Exception as e:
                    print('error zXStreamity ', e)
        else:
            self.session.open(MessageBox, _("Missing XStreamity Plugins!"), MessageBox.TYPE_INFO, timeout=4)

    def zLogoboth(self, answer=None):
        sel4 = self['config'].getCurrent()[1].value
        print('sel4-- ', sel4)
        sel4 = sel4.replace(" ", "-")
        filemvi = self.chooseFile + 'bootlogo_' + sel4 + '.mvi'
        origmvi = self.chooseFile + 'bootlogo_Original-Bootlogo.mvi'
        print('filemvi ', filemvi)
        if answer is None:
            self.session.openWithCallback(self.zLogoboth, MessageBox, _("Do you really want to change Bootlogo image?"))
        elif answer:
            print('answer True')
            if filemvi == origmvi:
                os.remove('%s%s' % (mvi, 'default_bootlogo.mvi'))
            if fileExists('%s%s' % (mvi, 'default_bootlogo.mvi')):
                # overwrite
                cmdz = 'cp -rf %s %sbootlogo.mvi > /dev/null 2>&1' % (filemvi, mvi)
                os.system(cmdz)
                self.session.open(MessageBox, _('Bootlogo changed and backup to default_bootlogo.mvi!'), MessageBox.TYPE_INFO, timeout=5)
            else:
                if fileExists('%sbootlogo.mvi' % mvi):
                    cmdk = 'cp -rf %sbootlogo.mvi %sdefault_bootlogo.mvi > /dev/null 2>&1' % (mvi, mvi)
                    # print('file moved to default_bootlogo.mvi ', cmdk)
                    os.system(cmdk)
                    # copy original mvi to zsetup only the first time
                    if not fileExists(origmvi):
                        cmdk = 'cp -rf %sbootlogo.mvi %s > /dev/null 2>&1' % (mvi, origmvi)
                        # print('file moved to bootlogo_Original-Bootlogo.mvi ', cmdk)
                        os.system(cmdk)
                    # overwrite
                    cmdz = 'cp -rf %s %sbootlogo.mvi > /dev/null 2>&1' % (filemvi, mvi)
                    # print('apply bootlogo ', cmdz)
                    os.system(cmdz)
                    self.session.open(MessageBox, _('Bootlogo changed!\nRestart Gui please'), MessageBox.TYPE_INFO, timeout=5)

    def zHelp(self):
        self.session.open(ozHelp)

    def ShowPictureFull(self):
        try:
            self.path = self.GetPicturePath()
            if fileExists(self.path):
                self.session.open(ShowPictureFullX, self.path)
        except:
            return

    def zXml(self):
        self['author'].setText(welcome)
        sel1 = self['config'].getCurrent()[1].value  # InfoBar-Meteo
        selx = self['config'].getCurrent()[0]

        if localreturn(selx):
            return
        sel2 = sel1.lower()  # .replace(" ", "-")
        global filexml
        if 'menu' in sel2:
            filexml = self.chooseFile + 'menu_' + sel1
        if 'infobar' in sel2:
            filexml = self.chooseFile + 'infobar_' + sel1
        if 'Second Infobar:' in selx:
            filexml = self.chooseFile + 'second_' + sel1
        if 'channel' in sel2:
            filexml = self.chooseFile + 'channel_' + sel1
        if 'radio' in sel2:
            filexml = self.chooseFile + 'radio_' + sel1
        if 'mediaplayer' in sel2:
            filexml = self.chooseFile + 'mediaplayer_' + sel1
        if 'eventview' in sel2:
            filexml = self.chooseFile + 'eventview_' + sel1
        if 'plugins' in sel2:
            filexml = self.chooseFile + 'plugins_' + sel1
        if 'bottom' in sel2:
            filexml = self.chooseFile + 'blogo_' + sel1
        if 'top' in sel2:
            filexml = self.chooseFile + 'alogo_' + sel1
        if 'volume' in sel2:
            filexml = self.chooseFile + 'volume_' + sel1

        filexml = filexml.replace(" ", "-") + '.xml'
        # print('===========filexml========== ', filexml)
        #  <!-- Author mmark Infobar + Crypt + Cover + DataChannel + IP -->
        if fileExists(filexml):
            print('===========filexml========== ', filexml)
            with open(filexml, 'r') as openFile:
                for x in openFile:
                    y = x.find('Author')
                    if y >= 0:
                        x = x.replace('<!-- ', '').replace(' -->', '').replace('+', '\n')
                        x = x.strip()
                        break
                print('xxxx author:', x)
                self['author'].setText(x)
        else:
            try:
                self['author'].setText(welcome)
                cpr = Uri.get_cpyright()
                self['description'].setText(cpr)
            except Exception as e:
                print(e)
                self['author'].setText(welcome)
                self['description'].setText('-')
        return

    def GetPicturePath(self):
        PicturePath = '%sbasefile/default.jpg' % thisdir
        sel = self["config"].getCurrent()[1]
        sel3 = self['config'].getCurrent()[1].value
        xxxx = self["config"].getCurrent()[0]
        # print('sel3: ', str(sel3))
        # print(type(sel3))
        returnValue = '%sbasefile/default.jpg' % thisdir
        try:
            # if '1' in str(sel3) and 'style' in xxxx.lower():
                # PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style1'))
                # return PicturePath
            # if '2' in str(sel3) and 'style' in xxxx.lower():
                # PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style2'))
                # return PicturePath
            # if '3' in str(sel3) and 'style' in xxxx.lower():
                # PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style3'))
                # return PicturePath
            # if '4' in str(sel3) and 'style' in xxxx.lower():
                # PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style4'))
                # return PicturePath
            # if '5' in str(sel3) and 'style' in xxxx.lower():
                # PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style5'))
                # return PicturePath
            # if '6' in str(sel3) and 'style' in xxxx.lower():
                # PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style6'))
                # return PicturePath
            if 'tmdb api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'tmdb'))
                return PicturePath
            if 'omdb api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'omdb'))
                return PicturePath
            if 'thetvdb api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'thetvdb'))
                return PicturePath
            if 'visualweather plugin api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'visualweather'))
                return PicturePath

            c = ['setup', 'autoupdate', ' weather', 'oaweather']
            if xxxx.lower() in c:
                PicturePath = '%sbasefile/default.jpg' % thisdir
                return PicturePath

            if sel and sel == config.ozeta.data:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'tmdb'))
            if sel and sel == config.ozeta.data2:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'omdb'))
            if sel and sel == config.ozeta.data3:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'visualweather'))
            if sel and sel == config.ozeta.data4:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'thetvdb'))
            if sel and sel == config.ozeta.mmpicons:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'mmPicons'))
            if sel and sel == config.ozeta.api:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey'))
            if sel and sel == config.ozeta.txtapi:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozeta.api2:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey2'))
            if sel and sel == config.ozeta.txtapi2:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozeta.api3:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey3'))
            if sel and sel == config.ozeta.txtapi3:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozeta.api4:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey4'))
            if sel and sel == config.ozeta.txtapi4:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozeta.XStreamity:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'xstreamity'))
            if sel3 is not None or sel3 != '' or sel3 != 'None':
                returnValue = str(sel3).replace(" ", "-")
            if fileExists('%senigma2/%s/zSetup/zPreview/%s.jpg' % (mvi, cur_skin, returnValue)):
                PicturePath = '%senigma2/%s/zSetup/zPreview/%s.jpg' % (mvi, cur_skin, returnValue)
            else:
                return '%sbasefile/default.jpg' % thisdir
        except Exception as e:
            print(e)
        return PicturePath

    def UpdatePicture(self):
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self, data=None):
        if self["Preview"].instance:
            width = 700
            height = 394
            self.PicLoad.setPara([width, height, self.Scale[0], self.Scale[1], 0, 1, "FF000000"])
            if self.PicLoad.startDecode(self.GetPicturePath()):
                self.PicLoad = ePicLoad()
                try:
                    self.PicLoad.PictureData.get().append(self.DecodePicture)
                except:
                    self.PicLoad_conn = self.PicLoad.PictureData.connect(self.DecodePicture)
            return

    def DecodePicture(self, PicInfo=None):
        ptr = self.PicLoad.getData()
        if ptr is not None:
            self["Preview"].instance.setPixmap(ptr)
            self["Preview"].instance.show()
        return

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()
        self.zXml()
        self.ShowPicture()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()
        self.zXml()
        self.ShowPicture()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.createSetup()
        self.zXml()
        self.ShowPicture()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.createSetup()
        self.zXml()
        self.ShowPicture()

    def zSave(self):
        if str(cur_skin) == 'oZeta-FHD':
            asd = str(self.chooseFile)
            menu = []
            menu.append(asd + 'menu_' + str(config.ozeta.FirstMenuFHD.value))
            menu.append(asd + 'infobar_' + str(config.ozeta.FirstInfobarFHD.value))
            menu.append(asd + 'second_' + str(config.ozeta.SecondInfobarFHD.value))
            menu.append(asd + 'channel_' + str(config.ozeta.ChannSelectorFHD.value))
            menu.append(asd + 'volume_' + str(config.ozeta.VolumeFHD.value))
            menu.append(asd + 'radio_' + str(config.ozeta.RadioFHD.value))
            menu.append(asd + 'mediaplayer_' + str(config.ozeta.MediaPlayerFHD.value))
            menu.append(asd + 'eventview_' + str(config.ozeta.EventviewFHD.value))
            if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                menu.append(asd + 'plugins_' + str(config.ozeta.PluginsFHD.value))
            menu.append(asd + 'alogo_' + str(config.ozeta.LogoaFHD.value))
            menu.append(asd + 'blogo_' + str(config.ozeta.LogobFHD.value))
            print('menu list=', menu)
            init_file = '%s/basefile/init' % thisdir
            file_lines = ''
            try:
                skFile = open(init_file, 'r')
                file_lines = skFile.read()
                skFile.close()
                skFilew = open(self.skinFileTmp, 'w')
                skFilew.write(str(file_lines) + '\n')
                for f in menu:
                    f = f.replace(" ", "-") + '.xml'
                    if fileExists(f):
                        with open(f, 'r') as e:
                            fpage = e.read()
                            fpage = fpage.replace("[", "").replace("]", "")
                            skFilew.write(fpage)
                skFilew.write('\n</skin>\n')
                skFilew.close()
                if fileExists(self.skinFile):
                    os.remove(self.skinFile)
                    print("********** Removed %s" % self.skinFile)
                os.rename(self.skinFileTmp, self.skinFile)
                self.saveall()
                self.session.open(MessageBox, _('Successfully creating Skin!'), MessageBox.TYPE_INFO, timeout=5)
            except Exception as e:
                print(e)
                self.session.open(MessageBox, _('Error creating Skin!\nError %s' % e), MessageBox.TYPE_ERROR, timeout=5)

    def saveall(self):
        try:
            # if self["config"].isChanged():
                # for x in self["config"].list:
                    # if fakeconfig(x):
                        # print('fake:', fakeconfig(x))
                        # print('xxxx:', x)
                        # continue
                    # # print('zzzz:', x)
                    # x[1].save()
                # config.ozeta.txtapi.save()
                # config.ozetanss.save()
                # configfile.save()
                # ######### recover try
                # config.ozeta.txtapi2.save()
                # config.ozeta.txtapi3.save()
                # config.ozeta.txtapi4.save()
                # config.ozeta.zweather.save()
                config.ozeta.city.save()
                config.ozeta.FirstMenuFHD.save()
                config.ozeta.FirstInfobarFHD.save()
                config.ozeta.SecondInfobarFHD.save()
                config.ozeta.ChannSelectorFHD.save()
                config.ozeta.VolumeFHD.save()
                config.ozeta.RadioFHD.save()
                config.ozeta.MediaPlayerFHD.save()
                config.ozeta.EventviewFHD.save()
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                    config.ozeta.PluginsFHD.save()
                config.ozeta.LogoaFHD.save()
                config.ozeta.LogobFHD.save()
                # config.ozeta.Logoboth.save()
        except Exception as e:
            print('error save:', e)

# region options
    def zWaitReload(self):
        self.Timer = eTimer()
        try:
            self.Timer.callback.append(self.zUpdate)
        except:
            self.Timer_conn = self.Timer.timeout.connect(self.zUpdate)
        self.Timer.start(1000, 1)
        self.createSetup()

    def upOptions(self):
        self.Timer = eTimer()
        try:
            self.Timer.callback.append(self.zOptions)
        except:
            self.Timer_conn = self.Timer.timeout.connect(self.zOptions)
        self.Timer.start(1000, 1)
        self.createSetup()

    def mmWaitReload(self):
        self.Timer = eTimer()
        try:
            self.Timer.callback.append(self.zMMpicons)
        except:
            self.Timer_conn = self.Timer.timeout.connect(self.zMMpicons)
        self.Timer.start(1000, 1)
        self.createSetup()

    def KeyText(self):
        from Screens.VirtualKeyBoard import VirtualKeyBoard
        sel = self["config"].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self["config"].getCurrent()[1].value = callback
            self["config"].invalidate(self["config"].getCurrent())
        return

    def keyApi(self, answer=None):
        api = "/tmp/apikey.txt"
        if answer is None:
            if fileExists(api) and os.stat(api).st_size > 0:
                self.session.openWithCallback(self.keyApi, MessageBox, _("Import Api Key TMDB from /tmp/apikey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api) and os.stat(api).st_size > 0:
                with open(api, 'r') as f:
                    fpage = f.readline()
                    with open(tmdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozeta.txtapi.setValue(str(fpage))
                    config.ozeta.txtapi.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("TMDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        return

    def keyApi2(self, answer=None):
        api2 = "/tmp/omdbkey.txt"
        if answer is None:
            if fileExists(api2) and os.stat(api2).st_size > 0:
                self.session.openWithCallback(self.keyApi2, MessageBox, _("Import Api Key OMDB from /tmp/omdbkey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api2) and os.stat(api2).st_size > 0:
                with open(api2, 'r') as f:
                    fpage = f.readline()
                    with open(omdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozeta.txtapi2.setValue(str(fpage))
                    config.ozeta.txtapi2.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("OMDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        return

    def keyApi3(self, answer=None):
        api3 = "/etc/enigma2/VisualWeather/apikey.txt"
        if answer is None:
            if fileExists(api3) and os.stat(api3).st_size > 0:
                self.session.openWithCallback(self.keyApi3, MessageBox, _("Import Api Key VISUALWEATHER from /etc/enigma2/VisualWeather/apikey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api3), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api3) and os.stat(api3).st_size > 0:
                with open(api3, 'r') as f:
                    fpage = f.readline()
                    with open(visual_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozeta.txtapi3.setValue(str(fpage))
                    config.ozeta.txtapi3.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("VISUALWEATHER ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api3), MessageBox.TYPE_INFO, timeout=4)
        return

    def keyApi4(self, answer=None):
        api4 = "/tmp/thetvdbkey.txt"
        if answer is None:
            if fileExists(api4) and os.stat(api4).st_size > 0:
                self.session.openWithCallback(self.keyapi4, MessageBox, _("Import Api Key THETVDB from /tmp/thetvdbkey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api4), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api4) and os.stat(api4).st_size > 0:
                with open(api4, 'r') as f:
                    fpage = f.readline()
                    with open(thetvdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozeta.txtapi4.setValue(str(fpage))
                    config.ozeta.txtapi4.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("THETVDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api4), MessageBox.TYPE_INFO, timeout=4)
        return

#  reset config
    def zDefault(self, answer=None):
        if str(cur_skin) == 'oZeta-FHD':
            if answer is None:
                self.session.openWithCallback(self.zDefault, MessageBox, _("Reset Settings to Defaults Parameters?"))
            else:
                config.ozeta.FirstMenuFHD.value = 'Menu Default'
                config.ozeta.FirstInfobarFHD.value = 'InfoBar Default'
                config.ozeta.SecondInfobarFHD.value = 'SecondInfoBar Default'
                config.ozeta.ChannSelectorFHD.value = 'Channel Default'
                config.ozeta.VolumeFHD.value = 'Volume Default'
                config.ozeta.RadioFHD.value = 'RadioInfoBar Default'
                config.ozeta.MediaPlayerFHD.value = 'MediaPlayer Default'
                config.ozeta.EventviewFHD.value = 'Eventview Default'
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                    config.ozeta.PluginsFHD.value = 'PluginBrowser Default'
                config.ozeta.LogoaFHD.value = 'TopLogo Default'
                config.ozeta.LogobFHD.value = 'BottomLogo Default'
                config.ozeta.Logoboth.value = 'Bootlogo Default'
                self.createSetup()
                self.UpdatePicture()
            return

# update zskin
    def zUpdate(self):
        if os.path.exists('/usr/share/enigma2/oZeta-FHD'):
            self.session.openWithCallback(self.zUpdate2, MessageBox, _("Skin exist!! Do you really want to Upgrade?"), MessageBox.TYPE_YESNO)
        else:
            self.session.openWithCallback(self.zUpdate2, MessageBox, _('Do you really want to install the oZeta Skin ?\nDo it at your own risk.\nDo you want to continue?'), MessageBox.TYPE_YESNO)
        return

    def zUpdate2(self, answer=None):
        if answer:
            if config.ozeta.update:
                self.zSkin()
                self.upd_zeta()
                self.check_line()
        return

    def zUpConponent(self):
        if os.path.exists('/usr/share/enigma2/oZeta-FHD'):
            self.session.openWithCallback(self.zConponentReq, MessageBox, _("Skin exist!! Do you really want to Update Conponent?"), MessageBox.TYPE_YESNO)

    def zConponentReq(self, answer=None):
        if answer:
            self.zConponent()
        return

    def dowfil(self):
        if PY3:
            import urllib.request as urllib2
            import http.cookiejar as cookielib
        else:
            import urllib2
            import cookielib
        Req = RequestAgent()
        headers = {'User-Agent': Req}
        cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        urllib2.install_opener(opener)
        try:
            req = urllib2.Request(self.com, data=None, headers=headers)
            handler = urllib2.urlopen(req, timeout=15)
            data = handler.read()
            with open(tarfile, 'wb') as f:
                f.write(data)
            print('MYDEBUG - download ok - URL: %s , filename: %s' % (self.com, tarfile))
        except:
            print('MYDEBUG - download failed - URL: %s , filename: %s' % (self.com, tarfile))
        return tarfile

    def start(self):
        pass

#  install conponent zskin
    def zConponent(self):
        if fileExists(tarfile):
            os.remove(tarfile)
        try:
            self.com = 'http://patbuweb.com/ozeta/conponent.tar'
            self.dest = self.dowfil()
            Req = RequestAgent()
            self.command = ["tar -xvf /tmp/download.tar -C /"]
            cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge';%s;rm -rf /tmp/download.tar > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
            if "https" in str(self.com):
                cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge';%s;rm -rf /tmp/download.tar > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
            print('cmd: ', cmd)
            self.session.open(Console, title=_('Installation oZeta Skin Conponent'), cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.upd_zeta)
        except Exception as e:
            print('error download: ', e)
            self.session.open(MessageBox, _('Download Error!!!\nPlease Report Issue on forum:\nzConponent error'), MessageBox.TYPE_INFO, timeout=5)
            return
        self.session.open(MessageBox, _('OZSKIN CONPONENT DONE\nPLEASE RESTART GUI'), MessageBox.TYPE_INFO, timeout=5)


#  install update zskin
    def zSkin(self):
        if fileExists(tarfile):
            os.remove(tarfile)
        try:
            self.com = 'http://patbuweb.com/ozeta/ozeta.tar'
            self.dest = self.dowfil()
            Req = RequestAgent()
            cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge' > /dev/null" % (Req, str(self.com), self.dest)
            if "https" in str(self.com):
                cmd = "wget --no-cache --no-dns-cache --no-check-certificate -U '%s' -c '%s' -O '%s' --post-data='action=purge' > /dev/null" % (Req, str(self.com), self.dest)
            print('cmd: ', cmd)
            self.session.open(Console, title=_('Installation oZeta Skin'), cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.upd_zeta)
        except Exception as e:
            print('error download: ', e)
            self.session.open(MessageBox, _('Download Error!!!\nPlease Report Issue on forum:\nzSkin error'), MessageBox.TYPE_INFO, timeout=5)
            return
        print('update tarfile')

    def upd_zeta(self):
        time.sleep(5)
        print('init update zeta')
        content1 = '/etc/issue'
        with open(content1, 'r') as f:
            content = f.read()
            if 'openpli' in content:
                print("In version =", content)
        type = content.strip().lower()
        print('type is  ', str(type))

        if 'openpli' or 'nonsolosat' in type or os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
            cmd1 = 'cp -rf /usr/share/enigma2/%s/zSkin/skin_team.xml /usr/share/enigma2/%s/zSkin/skin_teamOrig.xml > /dev/null 2>&1' % (cur_skin, cur_skin)
            cmd2 = 'cp -rf /usr/share/enigma2/%s/zSkin/skin_teampli.xml /usr/share/enigma2/%s/zSkin/skin_team.xml > /dev/null 2>&1' % (cur_skin, cur_skin)
            os.system(cmd1)
            os.system(cmd2)
            print(cmd1 + '\n' + cmd2)

        if 'openatv' in type:
            if '6.' in type:
                cmd1 = 'cp -rf /usr/share/enigma2/%s/zSkin/skin_team.xml /usr/share/enigma2/%s/zSkin/skin_teamOrig.xml > /dev/null 2>&1' % (cur_skin, cur_skin)
                cmd2 = 'cp -rf /usr/share/enigma2/%s/zSkin/skin_teamatv6.xml /usr/share/enigma2/%s/zSkin/skin_team.xml > /dev/null 2>&1' % (cur_skin, cur_skin)
                os.system(cmd1)
                os.system(cmd2)
                print(cmd1 + '\n' + cmd2)

        if 'openspa' in type:
            cmd1 = 'cp -rf /usr/share/enigma2/%s/zSkin/skin_team.xml /usr/share/enigma2/%s/zSkin/skin_teamOrig.xml > /dev/null 2>&1' % (cur_skin, cur_skin)
            cmd2 = 'cp -rf /usr/share/enigma2/%s/zSkin/skin_teamspa.xml /usr/share/enigma2/%s/zSkin/skin_team.xml > /dev/null 2>&1' % (cur_skin, cur_skin)
            os.system(cmd1)
            os.system(cmd2)
            print(cmd1 + '\n' + cmd2)
        else:
            self.session.open(MessageBox, _('Image Box Not Tested!!'), MessageBox.TYPE_INFO, timeout=5)
        # self.check_line()

# install default options

    def zOptions(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.zOptions, MessageBox, _('Install Test Options for oZeta skin\nDo you really want to install now?'))
        elif answer:
            if fileExists(tarfile):
                os.remove(tarfile)
            try:
                self.com = 'http://patbuweb.com/ozeta/options.tar'
                self.dest = self.dowfil()
                Req = RequestAgent()
                self.command = ["tar -xvf /tmp/download.tar -C /"]
                cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge';%s;rm -rf /tmp/download.tar > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
                if "https" in str(self.com):
                    cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge';%s;rm -rf /tmp/download.tar > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
                print('cmd: ', cmd)
                self.session.open(Console, title=_('Installation oZeta Skin options'), cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.upd_zeta)

            except Exception as e:
                print('error download: ', e)
                self.session.open(MessageBox, _('Download Error!!!\nPlease Report Issue on forum:\ngoUp error'), MessageBox.TYPE_INFO, timeout=5)
                return
            self.session.open(MessageBox, _('OZSKIN OPTIONS DONE\nPLEASE RESTART GUI'), MessageBox.TYPE_INFO, timeout=5)

    def starts(self):
        pass

    def check_line(self):
        # if str(cur_skin) == 'oZeta-FHD':
        lulu = 'skin_templatepanelslulu.xml'
        fldlulu = '/usr/share/enigma2/oZeta-FHD/zSkin/skin_templatepanelslulu.xml'
        filename = '/usr/share/enigma2/oZeta-FHD/skin.xml'
        filename2 = '/usr/share/enigma2/oZeta-FHD/skin2.xml'
        if fileExists(fldlulu):
            with open(filename, 'r') as f:
                fpage = f.readline()
                if lulu in fpage:
                    print('line lulu exist')
                    f.close()
                else:
                    print('line lulu not exist')
                    fin = open(filename, "rt")
                    fout = open(filename2, "wt")
                    for line in fin:
                        fout.write(line.replace('</skin>', '\t<include filename="zSkin/skin_templatepanelslulu.xml"/>\n</skin>'))
                    fin.close()
                    fout.close()
                    cmd1 = 'mv -f %s %s > /dev/null 2>&1' % (filename2, filename)
                    os.system(cmd1)
            self.session.open(MessageBox, _('OZSKIN UPDATE\nPLEASE RESTART GUI'), MessageBox.TYPE_INFO, timeout=5)

#  error load
    def errorLoad(self):
        print('error: errorLoad')

# import mmpicons plugin OK work
    def zMMpicons(self, answer=None):
        mmpiconz = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('mmPicons'))
        if os.path.isdir(mmpiconz):
            from Plugins.Extensions.mmPicons.plugin import SelectPicons
            self.session.open(SelectPicons)
        else:
            if answer is None:
                self.session.openWithCallback(self.zOptions, MessageBox, _('mmPicons Plugin Not Installed!!\nDo you really want to install now?'))
            elif answer:
                if fileExists(tarfile):
                    os.remove(tarfile)
                try:
                    self.com = 'http://patbuweb.com/mmpicons/mmpicons.tar'
                    self.dest = self.dowfil()
                    Req = RequestAgent()
                    self.command = ["tar -xvf /tmp/download.tar -C /"]
                    cmd = "wget --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge';%s;rm -rf /tmp/download.tar > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
                    if "https" in str(self.com):
                        cmd = "wget --no-check-certificate --no-cache --no-dns-cache -U '%s' -c '%s' -O '%s' --post-data='action=purge';%s;rm -rf /tmp/download.tar > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
                    print('cmd: ', cmd)
                    self.session.open(Console, title=_('Installation mmpicons Plugin'), cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.upd_zeta)

                except Exception as e:
                    print('error download: ', e)
                    self.session.open(MessageBox, _('Download Error!!!\nPlease Report Issue on forum:\nzMMpicons error'), MessageBox.TYPE_INFO, timeout=5)
                    return
                self.session.open(MessageBox, _('MMPICONS PLUGIN INSTALLED\nPLEASE RESTART GUI'), MessageBox.TYPE_INFO, timeout=5)

# weather search
# config.plugins.ozeta.zweather = ConfigOnOff(default=False)
# config.plugins.ozeta.weather = NoSave(ConfigSelection(['-> Ok']))
# config.plugins.ozeta.city = ConfigText(default='', visible_width=50, fixed_size=False)
    def KeyMenu(self):
        if os.path.isdir(weatherz):
            weatherPluginEntryCount = config.plugins.WeatherPlugin.entrycount.value
            if weatherPluginEntryCount >= 1:
                self.session.openWithCallback(self.goWeather, MessageBox, _('Data entered for the Weather, do you want to continue the same?'), MessageBox.TYPE_YESNO)
            else:
                self.goWeather(True)
        elif os.path.isdir(theweather):
            locdirsave = "/etc/enigma2/TheWeather_last.cfg"
            location = 'n\A'
            if os.path.exists(locdirsave):
                for line in open(locdirsave):
                    location = line.rstrip()
                # zLine = str(location)
                if location != 'n\A':
                    zLine = str(location)
                # zLine = str(city) + ' - ' + str(location)
                config.ozeta.city.setValue(zLine)
                config.ozeta.city.save()
                self['city'].setText(zLine)
                self.createSetup()
            else:
                return
        else:
            restartbox = self.session.openWithCallback(self.goWeatherInstall, MessageBox, _('Weather Plugin Plugin Not Installed!!\nDo you really want to install now?'), MessageBox.TYPE_YESNO)
            restartbox.setTitle(_('Install Weather Plugin and Reboot'))
        self.UpdatePicture()

    def goWeather(self, result=False):
        if result:
            try:
                from .addons import WeatherSearch
                entry = config.plugins.WeatherPlugin.Entry[0]
                self.session.openWithCallback(self.UpdateComponents, WeatherSearch.MSNWeatherPluginEntryConfigScreen, entry)
            except:
                pass

    def goWeatherInstall(self, result=False):
        if result:
            try:
                cmd = 'enigma2-plugin-extensions-weatherplugin'
                self.session.open(Console, _('Install WeatherPlugin'), ['opkg install %s' % cmd], closeOnSuccess=False)
                time.sleep(5)
                # self.zSwitchMode()
            except Exception as e:
                print(e)
        else:
            message = _('Plugin WeatherPlugin not installed!!!')
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

    def KeyMenu2(self, answer=None):
        if os.path.isdir(OAWeather):
            if answer is None:
                self.session.openWithCallback(self.KeyMenu2, MessageBox, _('Open OAWeather, do you want to continue?'), MessageBox.TYPE_YESNO)
            elif answer:
                self.goOAWeather(True)
        else:
            restartbox = self.session.openWithCallback(self.goOAWeatherInstall, MessageBox, _('OAWeather Plugin Plugin Not Installed!!\nDo you really want to install now?'), MessageBox.TYPE_YESNO)
            restartbox.setTitle(_('Install OAWeather Plugin and Reboot'))
        self.UpdatePicture()

    def goOAWeather(self, result=False):
        if result:
            try:
                from Plugins.Extensions.OAWeather.plugin import WeatherSettingsView
                print('i am here!!')
                self.session.openWithCallback(self.UpdateComponents2, WeatherSettingsView)
            except:
                print('passed!!')
                pass

    def goOAWeatherInstall(self, result=False):
        if result:
            try:
                cmd = 'enigma2-plugin-extensions-oaweather'
                self.session.open(Console, _('Install OAWeatherPlugin'), ['opkg install %s' % cmd], closeOnSuccess=False)
                time.sleep(5)
                # self.zSwitchMode()
            except Exception as e:
                print(e)
        else:
            message = _('Plugin OAWeatherPlugin not installed!!!')
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

    def KeyMenu3(self):
        if os.path.isdir(theweather):
            try:
                from Plugins.Extensions.TheWeather.plugin import localcityscreen
                self.session.openWithCallback(self.UpdateComponents3, localcityscreen)
            except:
                print('passed!!')
        else:
            message = _('Plugin TheWeather not installed!!!')
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.UpdatePicture()

    def UpdateComponents(self):
        try:
            weatherPluginEntryCount = config.plugins.WeatherPlugin.entrycount.value
            if weatherPluginEntryCount >= 1:
                zLine = ''
                weatherPluginEntry = config.plugins.WeatherPlugin.Entry[0]
                location = weatherPluginEntry.weatherlocationcode.value
                city = weatherPluginEntry.city.value
                zLine = str(city) + ' - ' + str(location)
                config.ozeta.city.setValue(zLine)
                config.ozeta.city.save()
                self['city'].setText(zLine)
                self.createSetup()
            else:
                return
        except:
            pass

    def UpdateComponents2(self):
        try:
            if config.plugins.OAWeather.enabled.value:
                zLine = ''
                city = config.plugins.OAWeather.weathercity.value
                location = config.plugins.OAWeather.owm_geocode.value.split(",")
                zLine = str(city)
                if location:
                    zLine += ' - ' + str(location)
                # zLine = str(city) + ' - ' + str(location)
                config.ozeta.city.setValue(zLine)
                config.ozeta.city.save()
                self['city'].setText(zLine)
                self.createSetup()
            else:
                return
        except:
            pass

    def UpdateComponents3(self, date=None):
        try:
            locdirsave = "/etc/enigma2/TheWeather_last.cfg"
            if os.path.exists(locdirsave):
                location = 'n\A'
                for line in open(locdirsave):
                    location = line.rstrip()
                    locdirsave.close()
                if location != 'n\A' or location != '':
                    zLine = location
                zLine = str(location)
                config.ozeta.city.setValue(zLine)
                config.ozeta.city.save()
                self['city'].setText(zLine)
                self.createSetup()
            else:
                return
        except:
            pass

    def zExit(self):
        self.close()


class ozHelp(Screen):

    skin = """
              <screen name="ozHelp" position="center,center" size="1700,1000" title="oZeta Skin Help" backgroundColor="#10000000" flags="wfNoBorder">
                    <widget name="helpdesc" position="20,20" font="Regular;28" size="1640,960" halign="left" foregroundColor="#ffffff" backgroundColor="#101010" transparent="1" zPosition="1" />
                    <eLabel position="10,900" size="1680,3" backgroundColor="#303030" zPosition="1" />
                    <ePixmap position="30,930"      pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZsetup/basefile/red.png"    size="30,30" alphatest="blend" zPosition="2" />
                    <ePixmap position="330,930" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZsetup/basefile/green.png"      size="30,30" alphatest="blend" zPosition="2" />
                    <ePixmap position="630,930" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZsetup/basefile/yellow.png" size="30,30" alphatest="blend" zPosition="2" />
                    <ePixmap position="930,930" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZsetup/basefile/blue.png"       size="30,30" alphatest="blend" zPosition="2" />
                    <widget name="key_red"    font="Regular;28" position="70,930"  size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="1" transparent="1" />
                    <widget name="key_green"  font="Regular;28" position="370,930" size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="1" transparent="1" />
                    <widget name="key_yellow" font="Regular;28" position="670,930" size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="2" transparent="1" />
                    <widget name="key_blue"   font="Regular;28" position="970,930" size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="2" transparent="1" />
              </screen>
            """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setup_title = ('About oZsetup')
        self["version"] = Label(version)
        self['key_red'] = Label(_('Back'))
        self['key_green'] = Label(_('ApiKey Info'))
        self['key_yellow'] = Label(_('Preview Info'))
        self['key_blue'] = Label(_('Restart Info'))
        self["helpdesc"] = Label()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions'], {"red": self.zExit,
                                                       "green": self.green,
                                                       "yellow": self.yellow,
                                                       "blue": self.blue,
                                                       "ok": self.zExit,
                                                       "cancel": self.zExit}, -1)
        self.onLayoutFinish.append(self.finishLayout)

    def finishLayout(self):
        helpdesc = self.homecontext()
        self["helpdesc"].setText(helpdesc)

    def homecontext(self):
        conthelp = "Original oZeta Skin"
        conthelp += "Version : " + "%s\n" % version
        conthelp += "License: Open\n\n"
        conthelp += "Skin Author: Mmark - Info: e2skin.blogspot.it\n"
        conthelp += "Tested on:\n"
        conthelp += "openATV 7.x - OpenPLi 8.x - OpenSPA\n"
        conthelp += "zSetup Base Release: 2.0.0 - 30/06/2022\n"
        conthelp += "***Coded by @Lululla - @Corvoboys ***\n"
        conthelp += "*************************************\n\n"
        conthelp += "Please reports bug or info to blog:\n"
        conthelp += "http://e2skin.blogspot.com\n\n"
        conthelp += "*************************************\n\n"
        conthelp += "This plugin is NOT free software. It is open source, you are allowed to"
        conthelp += "modify it (if you keep the license), but it may not be commercially"
        conthelp += "distributed other than under the conditions noted above.\n\n"
        conthelp += "***CORVOBOYS.ORG TEAM***\n"
        return conthelp

    def yellow(self):
        helpdesc = self.yellowcontext()
        self["helpdesc"].setText(helpdesc)

    def yellowcontext(self):
        conthelp = "HELP ZSETUP PLUGIN:\n\n"
        conthelp += (" (RED BUTTON):\n")
        conthelp += _("         Exit zSetup\n\n")
        conthelp += (" (GREEN BUTTON):\n")
        conthelp += _("         Save and Copy changes in the Settings xml file\n\n")
        conthelp += (" (YELLOW BUTTON):\n")
        conthelp += _("         View Pic of Panels preview, in the FullHD mode\n\n")
        conthelp += (" (BLUE BUTTON):\n")
        conthelp += _("         Restart E2 but not apply changes\n\n")
        conthelp += (" (0 BUTTON):\n")
        conthelp += _("         Reset Settings\n\n")
        conthelp += (" (MENU BUTTON):\n")
        conthelp += _("         Install or Set Weather Plugin if installed\n\n")
        conthelp += (" (ALTERNATIVE RADIO)\n")
        conthelp += _("         Menu/Setup/Graphic Interface/OSD Setup\n")
        conthelp += _("         Alternative Radio Mode= Yes\n")
        return conthelp

    def green(self):
        helpdesc = self.greencontext()
        self["helpdesc"].setText(helpdesc)

    def greencontext(self):
        conthelp = "SETTINGS APIKEY: COVER AND WEATHER:\n\n"
        conthelp += ("(OMDB ApiKey):\n")
        conthelp += _("    For use The OMDB Covers, copy the omdbkey file in the skin folder:\n")
        conthelp += _("    /usr/share/enigma2/oZeta-FHD/omdbkey\n")
        conthelp += _("    Or manually enter the key, created on the OMDB portal'\n")
        conthelp += _("    use the virtual keyboard.\n")
        conthelp += _("    Or import from /tmp the file omdbkey.txt\n\n")
        conthelp += ("(TMDB ApiKey):\n")
        conthelp += _("    For use The TMDB Covers, copy the apikey file in the skin folder:\n")
        conthelp += _("    /usr/share/enigma2/oZeta-FHD/apikey\n")
        conthelp += _("    Or manually enter the key, created on the TMDB portal\n")
        conthelp += _("    use the virtual keyboard.\n\n")
        conthelp += _("    Or import from /tmp the file apikey.txt\n\n")
        conthelp += ("(THETMDB ApiKey):\n")
        conthelp += _("    For use The THETMDB Covers, copy the apikey file in the skin folder:\n")
        conthelp += _("    /usr/share/enigma2/oZeta-FHD/thetvdbkey\n")
        conthelp += _("    Or manually enter the key, created on the THETMDB portal\n")
        conthelp += _("    use the virtual keyboard.\n\n")
        conthelp += _("    Or import from /tmp the file thetvdbkey.txt\n\n")
        conthelp += ("(WEATHER Config):\n")
        conthelp += _("    For use The WeatherPlugin:\n")
        conthelp += _("    --Automatic Import from Plugin\n")
        conthelp += _("    For use VisualWeather\n")
        conthelp += _("    --use the virtual keyboard or import from default config plugin")
        return conthelp

    def blue(self):
        helpdesc = self.bluecontext()
        self["helpdesc"].setText(helpdesc)

    def bluecontext(self):
        conthelp = _("SAVE & RESTART\n\n")
        conthelp += (" (GREEN BUTTON):\n")
        conthelp += _("         Save and Copy changes in the xml file config\n")
        conthelp += (" (BLUE BUTTON):\n")
        conthelp += _("         Restart E2 but not apply changes\n")
        return conthelp

    def zExit(self):
        self.close()


class ShowPictureFullX(Screen):
    skin = """
            <screen position="center,center" size="1280,720" title="Preview" backgroundColor="transparent" flags="wfNoBorder">
                <widget name="PreviewFull" position="0,0" size="1920,1080" zPosition="0" />
                <widget name="lab2" position="0,0" size="1920,0" zPosition="2" font="Regular;30" halign="center" valign="center" backgroundColor="green" foregroundColor="white" />
            </screen>
           """

    def __init__(self, session, myprev):
        Screen.__init__(self, session)
        self['PreviewFull'] = Pixmap()
        self['actions'] = ActionMap(['OkCancelActions'], {"cancel": self.close})
        self["lab2"] = Label(_("Click Exit for close this window"))
        self.path = myprev
        self.onLayoutFinish.append(self.PreviewPictureFull)

    def PreviewPictureFull(self):
        myicon = self.path
        if myicon:
            png = loadPic(myicon, 1280, 720, 0, 0, 0, 1)
        self["PreviewFull"].instance.setPixmap(png)


class AutoStartTimerZ:

    def __init__(self, session):
        self.session = session
        global _firstStartZ
        print("*** running AutoStartTimerZ ***")
        if _firstStartZ:
            self.runUpdate()

    def runUpdate(self):
        print("*** running update ***")
        try:
            # if config.ozeta.update.value is True:  # oZsetup
                # from .addons import Uri
                # Uri.upd_done()
            _firstStartZ = False
        except Exception as e:
            print('error AutoStartTimerZ', e)


def autostart(reason, session=None, **kwargs):
    print("*** running autostart ***")
    global autoStartTimerZ
    global _firstStartZ
    if reason == 0:
        if session is not None:
            _firstStartZ = True
            autoStartTimerZ = AutoStartTimerZ(session)
    return


def mainmenu(menuid, **kwargs):
    if menuid == "setup":
        return [('oZsetup', main, _('oZsetup'), None)]
    else:
        return []


def main(session, **kwargs):
    try:
        session.open(oZsetup)
    except:
        import traceback
        traceback.print_exc()
        pass


# def __init__(self, name="Plugin", where=None, description="", icon=None, fnc=None, wakeupfnc=None, needsRestart=None, internal=False, weight=0):
def Plugins(**kwargs):
    result = [
              # PluginDescriptor(name='oZsetup', description=descplug, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
              PluginDescriptor(name='oZsetup', description=descplug, where=PluginDescriptor.WHERE_MENU, icon=iconpic, fnc=mainmenu),
              PluginDescriptor(name='oZsetup', description=descplug, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconpic, fnc=main)
             ]
    return result

#  ~ end code lululla 2022.10
