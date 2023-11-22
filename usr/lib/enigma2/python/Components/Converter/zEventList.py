# -*- coding: utf-8 -*-
#
# EventList - Converter
#
# Coded by Dr.Best (c) 2013
# Support: www.dreambox-tools.info
# E-Mail: dr.best@dreambox-tools.info
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Property GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Property GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Property GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
# <widget source="ServiceEvent" render="EventListDisplay" position="1080,610" size="1070,180" column0="0,100,yellow,Regular,30,0,0" column1="100,950,white,Regular,28,0,1" primetimeoffset="0"
# rowHeight="35" backgroundColor="#FF101010" transparent="1" zPosition="50">
# <convert type="zEventList">beginOnly=yes,primetime=yes,eventcount=4</convert>
# </widget>


from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eEPGCache, eServiceReference
from time import localtime, strftime, mktime, time
from datetime import datetime, timedelta


class zEventList(Converter, object):
    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgcache = eEPGCache.getInstance()
        self.primetime = 0
        self.eventcount = 0
        self.beginOnly = False
        if (len(type)):
            args = type.split(',')
            i = 0
            while i <= len(args) - 1:
                type_c, value = args[i].split('=')
                if type_c == "eventcount":
                    self.eventcount = int(value)
                elif type_c == "primetime":
                    if value == "yes":
                        self.primetime = 1
                elif type_c == "beginOnly":
                    if value == "yes":
                        self.beginOnly = True
                i += 1

    @cached
    def getContent(self):
        contentList = []
        ref = self.source.service
        info = ref and self.source.info
        if info is None:
            return []
        event = self.source.getCurrentEvent()
        if not event:
            return contentList

        i = 1
        while i <= (self.eventcount) and event:
            event = self.epgcache.lookupEventTime(eServiceReference(ref.toString()), event.getBeginTime() + event.getDuration())
            if event:
                contentList.append(self.getEventTuple(event),)
            i += 1
        if self.primetime == 1:
            now = localtime(time())
            dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, 20, 15)
            if time() > mktime(dt.timetuple()):
                dt += timedelta(days=1)  # skip to next day...
            primeTime = int(mktime(dt.timetuple()))
            event = self.epgcache.lookupEventTime(eServiceReference(ref.toString()), primeTime)
            if event and (event.getBeginTime() <= int(mktime(dt.timetuple()))):
                contentList.append(self.getEventTuple(event),)

        return contentList

    def getEventTuple(self, event):
        try:
            if self.beginOnly:
                time = "%s" % (strftime("%H:%M", localtime(event.getBeginTime())), )
            else:
                time = "%s - %s" % (strftime("%H:%M", localtime(event.getBeginTime())), strftime("%H:%M", localtime(event.getBeginTime() + event.getDuration())))
            title = event.getEventName()
            duration = "%d min" % (event.getDuration() / 60)
            return (time, title, duration)
        except Exception as e:
            print('Error GetEventTuple converter zevent: ', e)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC:
            Converter.changed(self, what)
