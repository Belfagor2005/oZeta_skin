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
from Tools import Notifications
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
    from os import popen, system
    cmd01 = "wget http://patbuweb.com/ozeta/zsetup.tar -O /tmp/zsetup.tar ; tar -xvf /tmp/zsetup.tar -C /"
    cmd02 = "wget --no-check-certificate -U 'Enigma2 - zsetup Plugin' -c 'http://patbuweb.com/ozeta/zsetup.tar' -O '/tmp/zsetup.tar'; tar -xvf /tmp/zsetup.tar -C /"
    cmd22 = 'find /usr/bin -name "wget"'
    res = popen(cmd22).read()
    if 'wget' not in res.lower():
        cmd23 = 'apt-get update && apt-get install wget'
        popen(cmd23)
    try:
        popen(cmd02)
    except:
        popen(cmd01)
    system('rm -rf /tmp/zsetup.tar')
    return


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
            return type
        #  used confirmed
        elif os.path.isdir('/usr/lib/enigma2/python/Plugins/PLi'):
            type = 'OpenPLi'
            print('type 3    ', str(type))
            return type
        elif fileExists('/etc/issue'):
            content1 = '/etc/issue'
            with open(content1, 'r') as f:
                content = f.read()
                if 'openspa' in content:
                    print("In version =", content)
                    type = content.strip()
                    print('type 4   ', str(type))
                    type = 'OpenSPA'
                    return 'OpenSPA'
                if 'openatv' in content:
                    print("In version =", content)
                    type = content.strip()
                    print('type 5   ', str(type))
                    type = type
                    return 'openatv'
        else:
            type = 'Unknow '
            print('type 6  ', str(type))
            return 'by Lululla'
    except:
        print('no line image- - -  ')
        return 'by Lululla'
    return


#  install mmpicons

def zPicons(answer):
    if answer is True:
        try:
            from os import popen, system
            cmd01 = "wget http://patbuweb.com/mmpicons/mmpicons.tar -O /tmp/mmpicons.tar ; tar -xvf /tmp/mmpicons.tar -C /"
            cmd02 = "wget --no-check-certificate -U 'Enigma2 - mmpicons Plugin' -c 'http://patbuweb.com/mmpicons/mmpicons.tar' -O '/tmp/mmpicons.tar'; tar -xvf /tmp/mmpicons.tar -C /"
            cmd22 = 'find /usr/bin -name "wget"'
            res = popen(cmd22).read()
            if 'wget' not in res.lower():
                cmd23 = 'apt-get update && apt-get install wget'
                popen(cmd23)
            try:
                popen(cmd02)
            except:
                popen(cmd01)
            return
            system('rm -rf /tmp/mmpicons.tar')
        except Exception as e:
            print('error download ', str(e))
    else:
        return


def zXStreamop(answer=True):
    if answer is True:
        try:
            from os import popen, system
            from Tools import Notifications
            cmd01 = "wget http://patbuweb.com/ozeta/Zeta_4_xtreamity_opt.tar -O /tmp/Zeta_4_xtreamity_opt.tar ; tar -xvf /tmp/Zeta_4_xtreamity_opt.tar -C /"
            cmd02 = "wget --no-check-certificate -U 'Enigma2 - xtreamity Plugin' -c 'http://patbuweb.com/ozeta/Zeta_4_xtreamity_opt.tar' -O '/tmp/Zeta_4_xtreamity_opt.tar'; tar -xvf /tmp/Zeta_4_xtreamity_opt.tar -C /"
            cmd22 = 'find /usr/bin -name "wget"'
            res = popen(cmd22).read()
            if 'wget' not in res.lower():
                cmd23 = 'apt-get update && apt-get install wget'
                popen(cmd23)
            try:
                popen(cmd02)
            except:
                popen(cmd01)
            return
            system('rm -rf /tmp/Zeta_4_xtreamity_opt.tar')
        except Exception as e:
            print('error download ', str(e))
    else:
        return


def zxOptions(answer=True):
    if answer is True:
        try:
            import sys
            import os
            from Tools import Notifications
            from os import popen, system
            cmd01 = "wget http://patbuweb.com/ozeta/options.tar -O /tmp/options.tar ; tar -xvf /tmp/options.tar -C /"
            cmd02 = "wget --no-check-certificate -U 'Enigma2 - options Plugin' -c 'http://patbuweb.com/ozeta/options.tar' -O '/tmp/options.tar'; tar -xvf /tmp/options.tar -C /"
            cmd22 = 'find /usr/bin -name "wget"'
            res = popen(cmd22).read()
            if 'wget' not in res.lower():
                cmd23 = 'apt-get update && apt-get install wget'
                popen(cmd23)
            try:
                popen(cmd02)
            except:
                popen(cmd01)
            system('rm -rf /tmp/options.tar')
            time.sleep(2)
            os.chmod("/usr/lib/enigma2/python/Plugins/Extensions/oZsetup/postUpd.sh", 0o0755)
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/oZsetup/postUpd.sh"
            system(cmd1)
            messageText = "Restart Gui Please"
            Notifications.AddPopup(messageText, MessageBox.TYPE_INFO, timeout=5)
            print('upd_zz Done!!!')
            return
        except Exception as e:
            print('error download ', str(e))
    else:
        return


def errorLoad(error):
    print(str(error))
