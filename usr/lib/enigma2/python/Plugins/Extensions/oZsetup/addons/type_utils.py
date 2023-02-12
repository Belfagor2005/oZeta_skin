from os import system

# Components
from Components.config import config
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
# from Components.AVSwitch import AVSwitch
# from Components.Pixmap import Pixmap
# from Components.Sources.StaticText import StaticText

# Screens
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen
# from Screens.InfoBar import MoviePlayer as Movie_Audio_Player

# Tools
from Tools.Directories import fileExists  # , fileReadLines
from errno import ENOENT
# from enigma import eGetEnigmaDebugLvl
# from Tools.TextBoundary import getTextBoundarySize
from sys import _getframe as getframe
DEFAULT_MODULE_NAME = __name__.split(".")[-1]
# forceDebug = eGetEnigmaDebugLvl() > 4

# Various
# from .InputBox import InputBoxWide
# from enigma import eTimer, getDesktop, gFont, eSize, ePicLoad
import skin

##################################

pname = _("File Commander - Addon Mediaplayer")
pdesc = _("play/show Files")
pversion = "1.0-r0"


from enigma import eLabel

# Calls onto the static function in eLabel. This avoids causing an invalidate
# on the parent container which is detrimental to UI performance,
# particularly in a complex screen like the graph EPG


def getTextBoundarySize(instance, font, targetSize, text):
	return eLabel.calculateTextSize(font, text, targetSize)

# ### play with movieplayer ###
def fileReadLines(filename, default=None, source=DEFAULT_MODULE_NAME, debug=False):
	lines = None
	try:
		with open(filename, "r") as fd:
			lines = fd.read().splitlines()
		msg = "Read"
	except OSError as err:
		if err.errno != ENOENT:  # ENOENT - No such file or directory.
			print("[%s] Error %d: Unable to read lines from file '%s'!  (%s)" % (source, err.errno, filename, err.strerror))
		lines = default
		msg = "Default"
	# if debug or forceDebug:
		# length = len(lines) if lines else 0
		# print("[%s] Line %d: %s %d lines from file '%s'." % (source, getframe(1).f_lineno, msg, length, filename))
	return lines

# class MoviePlayer(Movie_Audio_Player):
    # def __init__(self, session, service):
        # self.WithoutStopClose = False
        # Movie_Audio_Player.__init__(self, session, service)

    # def leavePlayer(self):
        # self.is_closing = True
        # self.close()

    # def leavePlayerConfirmed(self, answer):
        # """
        # overwrite InfoBar method.
        # """

    # def doEofInternal(self, playing):
        # if not self.execing:
            # return
        # if not playing:
            # return
        # self.leavePlayer()

    # def showMovies(self):
        # self.WithoutStopClose = True
        # self.close()

    # def movieSelected(self, service):
        # self.leavePlayer()

    # def __onClose(self):
        # if not(self.WithoutStopClose):
            # self.session.nav.playService(self.lastservice)

# ### File viewer/line editor ###


class zEditor(Screen):

    skin = """
        <screen name="zEditor" position="40,80" size="1900,900" title="zEditor">
            <widget name="list_head" position="8,10" size="1850,45" font="Regular;20" foregroundColor="#00fff000" />
            <widget name="filedata" scrollbarMode="showOnDemand" position="10,60" size="1850,750" itemHeight="50" />
            <widget name="key_red" position="100,840" size="260,25" transparent="1" font="Regular;20" />
            <widget name="key_green" position="395,840" size="260,25" transparent="1" font="Regular;20" />
            <widget name="key_yellow" position="690,840" size="260,25" transparent="1" font="Regular;20" />
            <widget name="key_blue" position="985,840" size="260,25" transparent="1" font="Regular;20" />
            <ePixmap position="70,840" size="260,25" zPosition="0" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap position="365,840" size="260,25" zPosition="0" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap position="660,840" size="260,25" zPosition="0" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <ePixmap position="955,840" size="260,25" zPosition="0" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 
        </screen>"""

    def __init__(self, session, file):
        self.skin = zEditor.skin
        Screen.__init__(self, session)
        # HelpableScreen.__init__(self)
        self.file_name = file
        self.list = []
        self["filedata"] = MenuList(self.list)
        self["actions"] = ActionMap(["WizardActions", "ColorActions", "DirectionActions"], {
            "ok": self.exitEditor,
            "green": self.exitEditor,
            "back": self.exitEditor,
            "red": self.exitEditor,
            "yellow": self.exitEditor,
            "blue": self.exitEditor, 
            # "chplus": self.posStart,
            # "chminus": self.posEnd,
        }, -1)
        self["list_head"] = Label(self.file_name)
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Exit"))
        self["key_yellow"] = Label(_("Exit"))
        self["key_blue"] = Label(_("Exit"))
        self.selLine = None
        self.oldLine = None
        self.isChanged = False
        self.skinName = "vEditorScreen"
        self.GetFileData(file)
        self.setTitle(_("Z File Commander - Addon File-Viewer"))

    def exitEditor(self):
        # if self.isChanged:
            # warningtext = "\n" + (_("has been CHANGED! Do you want to save it?"))
            # warningtext = warningtext + "\n\n" + (_("WARNING!"))
            # warningtext = warningtext + "\n" + (_("The authors are NOT RESPONSIBLE"))
            # warningtext = warningtext + "\n" + (_("for DATA LOSS OR DAMAGE !!!"))
            # msg = self.session.openWithCallback(self.SaveFile, MessageBox, _(self.file_name + warningtext), MessageBox.TYPE_YESNO)
            # msg.setTitle(_("oZeta File Commander"))
        # else:
            self.close()

    def GetFileData(self, fx):
        lines = fileReadLines(fx)
        if lines:
            for idx, line in enumerate(lines):
                self.list.append(str(idx + 1).zfill(4) + ": " + line)
        self["list_head"] = Label(fx)

    def posStart(self):
        self.selLine = 0
        self["filedata"].moveToIndex(0)

    def posEnd(self):
        self.selLine = len(self.list)
        self["filedata"].moveToIndex(len(self.list) - 1)

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

    def SaveFile(self, answer):
        if answer is True:
            try:
                if fileExists(self.file_name):
                    system("cp " + self.file_name + " " + self.file_name + ".bak")
                eFile = open(self.file_name, "w")
                for x in self.list:
                    my_x = x.partition(": ")[2]
                    eFile.writelines(my_x)
                eFile.close()
            except OSError:
                pass
            self.close()
        else:
            self.close()


