#!/usr/bin/python
# -*- coding: utf-8 -*- 

#example, style iso15693

from datetime import datetime
from dumpformat import saveDump, dumpManager

position = (50.850207,4.391133,datetime.now(),)
altitude = (350, "M", datetime.now(), )
place    = ("toto land", 53, "M", datetime.now(),)

currentDump = dump()
currentDump.setPosition(*position) 
currentDump.setAltitude(*altitude)
currentDump.setLocation(*place)
currentDump.setCurrentDatetime()
currentDump.setExtraInformation("GpsLogId",42)
currentDump.setExtraInformation("DumpLogId",23)
currentDump.setOwner("Jojojojojojo")
currentDump.setUID([0x45, 0x23, 0x42, 0xff, 0x98, 0xab])
currentDump.setPIX(23, 42)
currentDataGroup = currentDump.getDataGroup()
currentDump.setExtraInformation("readType", "SINGLE READ")
for i in range(0,23):
    currentDataGroup.addDataSector(i, [i+1, i+2, i+3, i+4])
    currentDataGroup.addMisc(i, "Locked")
    
saveDump(dump, "./dump_example.xml")
