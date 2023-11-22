#!/usr/bin/python
# -*- coding: utf-8 -*-

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#  Lululla coder and MMark skinner 2022.07.20
# NOT REMOVE DISCLAIMER!!!

from __future__ import absolute_import
from Components.config import config
from Tools.Directories import SCOPE_SKIN, SCOPE_PLUGINS
from Tools.Directories import fileExists, resolveFilename
import os
import re
import sys
from os import listdir
from os import remove
# global varShowFile
# varShowFile = ''
colorend = '\033[m'
colorstart = '\033[31m'
PY3 = sys.version_info.major >= 3
pythonFull = float(str(sys.version_info.major) + "." + str(sys.version_info.minor))

mvi = '/usr/share/'
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
folderskinfiles = 'zSkin'


def checklogskin(data):
    print(colorstart + data + colorend)
    data = str(data)
    open("/tmp/debug_my_skin.log", "a").write("\n" + ":>" + data)


def check_module_skin():
    path = "%senigma2/%s" % (mvi, cur_skin)
    dirs = listdir(path)
    listDir = []
    del listDir[:]
    for (root, dirs, files) in os.walk(path):
        print(dirs)
        listDir.append(dirs)
    # varShowFile = ''
    user_skin0 = ""
    user_skin = ""
    user_skin2 = ""
    skin_base_fold2 = ""
    skin_base_fold = "%senigma2/%s/" % (mvi, cur_skin)
    user_skin_file = ('/tmp/skin_user_' + cur_skin + '.xml')
    user_log = '/tmp/debug_my_skin.log'
    if fileExists(user_skin_file):
        remove(user_skin_file)
    if fileExists(user_log):
        remove(user_log)
    checklogskin("==INIT CHECK MY SKIN %s==" % cur_skin)
    checklogskin("skin_base_fold %s" % skin_base_fold)
    checklogskin("python ver. %s" % pythonFull)
    # if os.path.exists(skin_base_fold + folderskinfiles):

    for f in listdir(skin_base_fold):
        if f.endswith('.xml'):
            checklogskin("update write myFile %s" % f)
            user_skin = user_skin + readXMLfile(skin_base_fold + f)

    if os.path.exists(skin_base_fold + folderskinfiles):
            user_skin3 = skin_base_fold + folderskinfiles
            user_skin3 = user_skin3 + '/'
            for f in listdir(user_skin3):
                if f.endswith('.xml'):
                    print('ffff ', f)
                    checklogskin("update write myFile %s" % f)
                    user_skin2 = user_skin0 + readXMLfile(user_skin3 + f)

    if user_skin != '':
        user_skin = "<skin>\n" + user_skin + '\n\n\n\n\n' + user_skin2
        user_skin = user_skin + "</skin>\n"
        with open(user_skin_file, "w") as myFile:
            checklogskin("write myFile %s" % user_skin_file)
            myFile.write(user_skin)
            myFile.flush()
            myFile.close()
    checkComponent(user_skin, 'render', resolveFilename(SCOPE_PLUGINS, '../Components/Renderer/'))
    checkComponent(user_skin, 'Convert', resolveFilename(SCOPE_PLUGINS, '../Components/Converter/'))
    checkComponent(user_skin, 'pixmap', resolveFilename(SCOPE_SKIN, ''))
    checkComponent(user_skin, 'image', resolveFilename(SCOPE_SKIN, ''))
    return


def checkComponent(myContent, look4Component, myPath):
    checklogskin("RESEARCH IN PROGRESS...")

    # def upShowFile(name, sep=', '):
    def upShowFile(name):
        # global varShowFile
        checklogskin("Missing component found:%s" % name)
        # if varShowFile == '':
            # varShowFile = name
        # else:
            # varShowFile += sep + name
    r = re.findall(r' %s="([a-zA-Z0-9_/\.]+)"' % look4Component, myContent)
    r = list(set(r))
    checklogskin("I found %s:" % r)
    if r:
        try:
            checklogskin("Research for %s" % look4Component)
            for ComponentFind in set(r):
                # varShowFile = ''
                if 'Renderer' in myPath:
                    if PY3:
                        if not fileExists(myPath + str(ComponentFind) + ".pyc") and fileExists(myPath + str(ComponentFind) + ".py"):
                            upShowFile(myPath + str(ComponentFind) + ".pyc")
                    else:
                        if not fileExists(myPath + str(ComponentFind) + ".pyo") and fileExists(myPath + str(ComponentFind) + ".py"):
                            upShowFile(myPath + str(ComponentFind) + ".pyo")
                    # if not fileExists(myPath + str(ComponentFind) + ".py"):
                        # upShowFile(myPath + str(ComponentFind) + ".py")
                elif 'Converter' in myPath:
                    if PY3:
                        if not fileExists(myPath + str(ComponentFind) + ".pyc") and fileExists(myPath + str(ComponentFind) + ".py"):
                            upShowFile(myPath + str(ComponentFind) + ".pyc")
                    else:
                        if not PY3:
                            if not fileExists(myPath + str(ComponentFind) + ".pyo") and fileExists(myPath + str(ComponentFind) + ".py"):
                                upShowFile(myPath + str(ComponentFind) + ".pyo")
                        # if not fileExists(myPath + str(ComponentFind) + ".py"):
                            # upShowFile(myPath + str(ComponentFind) + ".py")
                else:
                    for i in listdir(mvi + "enigma2/" + cur_skin + '/'):
                        if ComponentFind.startswith(str(i)):
                            ComponentFind = mvi + "enigma2/" + cur_skin + '/' + str(ComponentFind)
                    if look4Component == 'pixmap':
                        if ComponentFind.startswith('/'):
                            if not os.path.exists(ComponentFind):
                                upShowFile(ComponentFind)
                        else:
                            if not os.path.exists(str(myPath + ComponentFind)):
                                upShowFile(ComponentFind)
                    elif look4Component == 'image':
                        if ComponentFind.startswith('/'):
                            if not os.path.exists(ComponentFind):
                                upShowFile(ComponentFind)
                        else:
                            if not os.path.exists(str(myPath + ComponentFind)):
                                upShowFile(ComponentFind)
                    else:
                        pass
        except Exception as e:
            print('Error ', str(e))
            checklogskin("Error found ", str(e))
    return


def readXMLfile(XMLfilename):
    myPath = os.path.realpath(XMLfilename)
    if not fileExists(myPath):
        remove(XMLfilename)
        return ''
    filecontent = ''
    inittag = '<!-'
    endtag = '-->'
    with open(XMLfilename, "r") as myFile:
        for line in myFile:
            if inittag in line:
                continue
            if endtag in line:
                break
            filecontent = filecontent + line
        myFile.close()
    return filecontent
