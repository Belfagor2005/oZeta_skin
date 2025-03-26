import os
import re
from Components.Converter.Converter import Converter
from Components.Element import cached


class zVpn(Converter, object):
    VPNLOAD = 0

    def __init__(self, type):
        Converter.__init__(self, type)
        if type == 'vpn':
            self.type = self.VPNLOAD

    @cached
    def getBoolean(self):
        info = False
        if os.path.isfile("/etc/openvpn/openvpn.log"):
            read_log = open("/etc/openvpn/openvpn.log", "r")
            for line in read_log:
                if re.search("Initialization Sequence Completed", line):
                    info = True
                elif re.search("VERIFY ERROR", line):
                    info = False
                elif re.search("TLS Error: TLS handshake failed", line):
                    info = False
                elif re.search("AUTH: Received control message: AUTH_FAILED", line):
                    info = False

        return info

    boolean = property(getBoolean)

    def changed(self, what):
        Converter.changed(self, what)
