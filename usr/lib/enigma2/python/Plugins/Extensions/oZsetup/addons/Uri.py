#!/usr/bin/python
# -*- coding: utf-8 -*-

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#  Lululla coder and MMark skinner 2022.07.20
# NOT REMOVE DISCLAIMER!!!

from __future__ import absolute_import
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists
print("oZeta Uri")

global CountConnOk
CountConnOk = 0


def zCheckInternet(opt=1, server=None, port=None):  # opt=5 custom server and port.
    global CountConnOk
    sock = False
    checklist = [("8.8.4.4", 53), ("8.8.8.8", 53), ("www.e2skin.blogspot.com", 80), ("www.e2skin.blogspot.com", 443), ("www.google.com", 443)]
    if opt < 5:
        srv = checklist[opt]
    else:
        srv = (server, port)
    try:
        import socket
        socket.setdefaulttimeout(0.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(srv)
        sock = True
        CountConnOk = 0
        # print(_("Status Internet: %s:%s -> OK" % (srv[0],srv[1])))
    except:
        sock = False
        # print(_("Status Internet: %s:%s -> KO" % (srv[0],srv[1])))
        if CountConnOk == 0 and opt != 2 and opt != 3:
            CountConnOk = 1
            # print(_("Restart Check 1 Internet."))
            return zCheckInternet(0)
        elif CountConnOk == 1 and opt != 2 and opt != 3:
            CountConnOk = 2
            # print(_("Restart Check 2 Internet."))
            return zCheckInternet(4)
    return sock


#  install update oZsetup


def upd_done():
    # from twisted.web.client import downloadPage
    print("In upd_done")
    import sys
    PY3 = sys.version_info.major >= 3
    xfile = 'http://patbuweb.com/ozeta/zsetup.tar'
    if PY3:
        xfile = b"http://patbuweb.com/ozeta/zsetup.tar"
        print("Update.py in PY3")
    import requests
    response = requests.head(xfile)
    if response.status_code == 200:
        fdest = "/tmp/zsetup.tar"
        print("Code 200 upd_done xfile =", xfile)
        r = requests.get(xfile)
        with open(fdest, 'wb') as f:
            f.write(r.content)
        import time
        import os
        time.sleep(5)
        if fileExists('/tmp/zsetup.tar') and os.stat('/tmp/zsetup.tar').st_size > 100:
            cmd = "tar -xvf /tmp/zsetup.tar -C /"
            print("cmd A =", cmd)
            os.remove('/tmp/zsetup.tar')
        # downloadPage(xfile, fdest).addCallback(upd_last)
    elif response.status_code == 404:
        print("Error 404")
    else:
        return


# def upd_last(fplug):
    # import time
    # import os
    # time.sleep(5)
    # if os.path.isfile('/tmp/zsetup.tar') and os.stat('/tmp/zsetup.tar').st_size > 100:
        # cmd = "tar -xvf /tmp/zsetup.tar -C /"
        # print( "cmd A =", cmd)
        # os.remove('/tmp/zsetup.tar')
    # return


def logtmpdebug(data):
    redcolorinit = '\033[31m'
    redcolorend = '\033[m'
    print(redcolorinit + data + redcolorend)
    data = str(data)
    open("/tmp/debug_my_skin.log", "a").write("\n"+":>"+data)


def get_cpyright():
    import datetime
    cpyright = [u"zSetup by lululla & mmark ©"]
    if (datetime.datetime.now().year > 2021):
        cpyright.append(" %d " % datetime.datetime.now().year)
    return " ".join(cpyright)


def imagevers():
    import os
    try:
        version = ''
        creator = ''
        type = ''
        if fileExists('/etc/image-version'):
            import re
            content1 = '/etc/image-version'
            with open(content1, 'r') as f:
                content = f.read()
                regexcat = 'version=(.+?)\n.+?creator=(.+?)\n'
                match = re.compile(regexcat, re.DOTALL).findall(content)
                print("match =", match)
                for version, creator in match:
                    print("In version =", version)
                    print("In creator =", creator)
            type = creator + ' ' + version
            print('type        ', str(type))
            return str(type)
        elif fileExists('/etc/issue'):
            content1 = '/etc/issue'
            with open(content1, 'r') as f:
                content = f.read()
                if 'openpli' in content:
                    print("In version =", content)
            type = content.strip()
            print('type 1    ', str(type))
            type = 'OpenPLi'
            print('type 2    ', str(type))
            return 'OpenPLi'
        #  used confirmed
        elif os.path.isdir('/usr/lib/enigma2/python/Plugins/PLi'):
            type = 'OpenPLi'
            print('type 3    ', str(type))
            return 'OpenPLi'
        elif fileExists('/etc/issue'):
            content1 = '/etc/issue'
            with open(content1, 'r') as f:
                content = f.read()
                if 'openspa' in content:
                    print("In version =", content)
            type = content.strip()
            print('type 4   ', str(type))
            type = 'OpenSPA'
            # print('type 5   ', str(type))
            return 'OpenSPA'
        else:
            type = 'Unknow '
            print('type 6  ', str(type))
            return 'by Lululla'
    except:
        print('no line image- - -  ')
        return 'by Lululla'


#  install mmpicons

def zPicons(answer):
    if answer is True:
        try:
            import sys
            from Tools import Notifications
            # from twisted.web.client import downloadPage
            PY3 = sys.version_info.major >= 3
            xfile = 'http://patbuweb.com/mmpicons/mmpicons.tar'
            if PY3:
                xfile = b"http://patbuweb.com/mmpicons/mmpicons.tar"
                print("Update.py in PY3")
            import requests
            response = requests.head(xfile)
            if response.status_code == 200:

                fdest = "/tmp/mmpicons.tar"
                print("Code 200 upd_done xfile =", xfile)
                r = requests.get(xfile)
                with open(fdest, 'wb') as f:
                    f.write(r.content)

                import time
                import os
                time.sleep(5)
                if fileExists('/tmp/mmpicons.tar') and os.stat('/tmp/mmpicons.tar').st_size > 100:
                    cmd = "tar -xvf /tmp/mmpicons.tar -C /"
                    os.system(cmd)
                    os.remove('/tmp/mmpicons.tar')
                    messageText = "Restart Gui Please"
                    Notifications.AddPopup(messageText, MessageBox.TYPE_INFO, timeout=5)
                # print("upd_done xfile =", xfile)
                # downloadPage(xfile, fdest).addCallback(upd_mm).addErrback(errorLoad)
            elif response.status_code == 404:
                print("Error 404")
                messageText = "ZPICONS NOT INSTALLED"
                Notifications.AddPopup(messageText, MessageBox.TYPE_ERROR, timeout=5)
            else:
                return
        except Exception as e:
            print('error download ', str(e))
    else:
        return


# def upd_mm(fplug):
    # from Tools import Notifications
    # import time
    # import os
    # time.sleep(5)
    # if os.path.isfile('/tmp/mmpicons.tar') and os.stat('/tmp/mmpicons.tar').st_size > 100:
        # cmd = "tar -xvf /tmp/mmpicons.tar -C /"
        # os.system(cmd)
        # os.remove('/tmp/mmpicons.tar')
        # messageText = _("Restart Gui Please")
        # Notifications.AddPopup(messageText, MessageBox.TYPE_INFO, timeout=5)


def zXStreamop(answer=True):
    if answer is True:
        try:
            # import os
            import sys
            # from twisted.web.client import downloadPage
            PY3 = sys.version_info.major >= 3
            zfile = 'http://patbuweb.com/ozeta/Zeta_4_xtreamity_opt.tar'
            if PY3:
                zfile = b"http://patbuweb.com/ozeta/Zeta_4_xtreamity_opt.tar"
                print("Update.py in PY3")
            import requests
            response = requests.head(zfile)
            if response.status_code == 200:
                fdest = "/tmp/Zeta_4_xtreamity_opt.tar"

                r = requests.get(zfile)
                with open(fdest, 'wb') as f:
                    f.write(r.content)

                import time
                time.sleep(5)
                from Tools import Notifications
                if fileExists('/tmp/Zeta_4_xtreamity_opt.tar') and os.stat('/tmp/Zeta_4_xtreamity_opt.tar').st_size > 100:
                    cmd = "tar -xvf /tmp/Zeta_4_xtreamity_opt.tar -C /"
                    os.system(cmd)
                    time.sleep(2)
                    messageText = "Restart Gui Please and select Skin Zeta from Plugin Xtreamity"
                    Notifications.AddPopup(messageText, MessageBox.TYPE_INFO, timeout=5)

                # downloadPage(zfile, fdest).addCallback(upd_zXS).addErrback(errorLoad)
            elif response.status_code == 404:
                print("Error 404")
                messageText = "zOptions NOT INSTALLED"
                Notifications.AddPopup(messageText, MessageBox.TYPE_ERROR, timeout=5)
            else:
                return
        except Exception as e:
            print('error download ', str(e))
    else:
        return


# def upd_zXS(fplug):
    # import time
    # time.sleep(5)
    # from Tools import Notifications
    # if os.path.isfile('/tmp/Zeta_4_xtreamity_opt.tar') and os.stat('/tmp/Zeta_4_xtreamity_opt.tar').st_size > 100:
        # cmd = "tar -xvf /tmp/Zeta_4_xtreamity_opt.tar -C /"
        # os.system(cmd)
        # time.sleep(2)
        # messageText = _("Restart Gui Please and select Skin Zeta from Plugin Xtreamity")
        # Notifications.AddPopup(messageText, MessageBox.TYPE_INFO, timeout=5)


def zxOptions(answer=True):
    if answer is True:
        try:
            import sys
            import os
            # from twisted.web.client import downloadPage
            from Tools import Notifications
            PY3 = sys.version_info.major >= 3
            zfile = 'http://patbuweb.com/ozeta/options.tar'
            if PY3:
                zfile = b"http://patbuweb.com/ozeta/options.tar"
                print("Update.py in PY3")
            import requests
            response = requests.head(zfile)
            if response.status_code == 200:
                fdest = "/tmp/options.tar"
                r = requests.get(zfile)
                with open(fdest, 'wb') as f:
                    f.write(r.content)
                import time
                time.sleep(5)
                if os.path.isfile('/tmp/options.tar') and os.stat('/tmp/options.tar').st_size > 100:
                    cmd = "tar -xvf /tmp/options.tar -C /"
                    os.system(cmd)
                    time.sleep(2)
                    os.remove('/tmp/options.tar')
                    os.chmod("/usr/lib/enigma2/python/Plugins/Extensions/oZsetup/postUpd.sh", 0o0755)
                    cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/oZsetup/postUpd.sh"
                    os.system(cmd1)
                    messageText = "Restart Gui Please"
                    Notifications.AddPopup(messageText, MessageBox.TYPE_INFO, timeout=5)
                    print('upd_zz Done!!!')
                # downloadPage(zfile, fdest).addCallback(upd_zz).addErrback(errorLoad)
            elif response.status_code == 404:
                print("Error 404")
                messageText = "zOptions NOT INSTALLED"
                Notifications.AddPopup(messageText, MessageBox.TYPE_ERROR, timeout=5)
            else:
                return
        except Exception as e:
            print('error download ', str(e))
    else:
        return


def errorLoad(error):
    print(str(error))
