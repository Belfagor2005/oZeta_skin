#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import system
# Components
from Components.config import config
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from enigma import eLabel

# Screens
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen

# Tools
from Tools.Directories import fileExists  # , fileReadLines
from errno import ENOENT

from sys import _getframe as getframe
DEFAULT_MODULE_NAME = __name__.split(".")[-1]

# Various
import skin
# by lululla


pname = _("File Commander - Addon")
pdesc = _("play/show Files")
pversion = "1.0-r3"


def getTextBoundarySize(instance, font, targetSize, text):
    return eLabel.calculateTextSize(font, text, targetSize)


def fileReadLines(filename, default=None, source=DEFAULT_MODULE_NAME, debug=False):
    lines = None
    try:
        with open(filename, "r") as fd:
            lines = fd.read().splitlines()
    except OSError as err:
        if err.errno != ENOENT:  # ENOENT - No such file or directory.
            print("[%s] Error %d: Unable to read lines from file '%s'!  (%s)" % (source, err.errno, filename, err.strerror))
        lines = default
    return lines


class File_Commander(Screen):

    skin = """
        <screen name="File_Commander" position="40,80" size="1900,900" title="Lululla_Commander">
            <widget name="list_head" position="8,10" size="1850,45" font="Regular;24" foregroundColor="#00fff000" />
            <widget name="filedata" scrollbarMode="showOnDemand" itemHeight="45" position="9,78" size="1850,725" />
            <!--
            <widget name="key_red" position="100,840" size="260,40" transparent="1" font="Regular;24" />
            <widget name="key_green" position="395,840" size="260,40" transparent="1" font="Regular;24" />
            <widget name="key_yellow" position="690,840" size="260,40" transparent="1" font="Regular;24" />
            <widget name="key_blue" position="985,840" size="260,40" transparent="1" font="Regular;24" />
            -->
            <widget name="key_red" position="95,820" zPosition="19" size="260,40" transparent="1" font="Regular;24" halign="center" />
            <widget name="key_green" position="395,820" zPosition="19" size="260,40" transparent="1" font="Regular;24" halign="center" />
            <widget name="key_yellow" position="690,820" zPosition="19" size="260,40" transparent="1" font="Regular;24" halign="center" />
            <widget name="key_blue" position="985,820" zPosition="19" size="260,40" transparent="1" font="Regular;24" halign="center" />
            <ePixmap position="95,865" size="260,25" zPosition="0" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap position="395,865" size="260,25" zPosition="0" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap position="690,865" size="260,25" zPosition="0" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <ePixmap position="985,870" size="260,25" zPosition="0" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
        </screen>"""

    def __init__(self, session, file):
        self.skin = File_Commander.skin
        Screen.__init__(self, session)
        # HelpableScreen.__init__(self)
        self.file_name = file
        title = "Lululla File Commander"
        self.newtitle = title == 'vEditorScreen' and ('Console') or title
        self.list = []
        self["filedata"] = MenuList(self.list)
        self["actions"] = ActionMap(["WizardActions", "ColorActions", "DirectionActions"], {
            "ok": self.edit_Line,
            "green": self.SaveFile,
            "back": self.exitEditor,
            "red": self.exitEditor,
            "yellow": self.del_Line,
            "blue": self.ins_Line,
            # "chplus": self.posStart,
            # "chminus": self.posEnd,
        }, -1)
        self["list_head"] = Label(self.file_name)
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Save"))
        self["key_yellow"] = Label(_("Del Line"))
        self["key_blue"] = Label(_("Ins Line"))
        self.selLine = None
        self.oldLine = None
        self.isChanged = False
        self.GetFileData(file)
        self.setTitle(self.newtitle)

    def exitEditor(self):
        self.close()

    def GetFileData(self, fx):
        lines = fileReadLines(fx)
        if lines:
            for idx, line in enumerate(lines):
                self.list.append(str(idx + 1).zfill(4) + ": " + line)
        self["list_head"].setText(fx)

    def posStart(self):
        self.selLine = 0
        self["filedata"].moveToIndex(0)

    def posEnd(self):
        self.selLine = len(self.list)
        self["filedata"].moveToIndex(len(self.list) - 1)

    def edit_Line(self):
        self.selLine = self["filedata"].getSelectionIndex()
        if self.selLine is not None and 0 <= self.selLine < len(self.list):
            current_line = self.list[self.selLine][0]
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title="Edit Line", text=current_line)

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            new_line = callback
            self.list[self.selLine] = (new_line,)  
            self.isChanged = True
            self.refreshList()  # Rendi visibile la lista aggiornata

    def del_Line(self):
        self.selLine = self["filedata"].getSelectionIndex()
        if len(self.list) > 1:
            self.isChanged = True
            del self.list[self.selLine]
            self.refreshList()

    def ins_Line(self):
        self.selLine = self["filedata"].getSelectionIndex()
        self.list.insert(self.selLine, "0000: " + "" + '\n')
        self.isChanged = True
        self.refreshList()

    def refreshList(self):
        lineno = 1
        for x in self.list:
            my_x = x.partition(": ")[2]
            self.list.remove(x)
            self.list.insert(lineno - 1, str(lineno).zfill(4) + ": " + my_x)  # '\n')
            lineno += 1
        self["filedata"].setList(self.list)

    def SaveFile(self):
        try:
            if fileExists(self.file_name):
                import shutil
                shutil.copy(self.file_name, self.file_name + ".bak")

            with open(self.file_name, "w") as eFile:
                for x in self.list:
                    if isinstance(x, tuple):
                        x = x[0]
                    my_x = x.partition(": ")[2]
                    eFile.write(my_x + "\n")

        except (OSError, IOError) as e:
            print("Error saving file:", str(e))
        self.close()
