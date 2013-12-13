#!/usr/bin/python
# -*- coding: utf-8 -*- 

#Copyright (C) 2013 Jonathan Delvaux <dumpformat@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

from exception import dumpManagerException
import os, sys
#import collections #isinstance(informationName, collections.Hashable)
import datetime
from xml.etree import cElementTree
import dateutil.parser #TODO XXX announce/install the depedency XXX
from utils import *

#TODO
    #extend the dump class and specialise for every known card
        #ultralight
        #ultralight C
        #mifare classic
        #desfire
        #...

#-comment structure le stockage en memoire pour pouvoir le reconvertir facilement et rapidement en xml?
    #afin d'eviter les appels recursifs pour generer la structure sur fichier
    #et aussi pouvoir faire des recherches rapidement en mémoire
    #avec des dico ?
        #les clés doivent rester unique
        #faire une hierarchie de dico
    #genre stocker les paths ?
        #/aaa/ddd/vvv/ ?

def loadDump(filePath):
    if filePath == None and type(filePath) != str:
        raise dumpManagerException("(dumpManager) load, invalid file path")
    
    if not os.path.exists(fpath):
        raise dumpManagerException("(dumpManager) load, the selected file does not exist or you don't have the correct right to read.  <"+str(fpath)+">")
        
    #TODO load the dump in xml format
        #also possible with import xml
    
    #TODO return a dump object
    
def saveDump(dump, filePath):
    if filePath == None and type(filePath) != str:
        raise dumpManagerException("(dumpManager) save, invalid file path")
    
    if not os.access(os.path.dirname(filePath), os.W_OK):
        raise dumpManagerException("(dumpManager) save, you don't have the right to create a file here. Or the path is invalid : <"+str(filePath)+">")
    
    #save the dump in xml format
    root = cElementTree.Element("dump")
    
    #reader
    buildXMLList(root, dump.xml["reader"], "reader")
    buildXMLList(root, dump.xml["environment"], "environment")
    buildXMLList(root, dump.xml["misc"], "misc", "miscitem", "key")
    buildXMLList(root, dump.xml["taginfo"], "taginfo")
    buildXMLList(root, dump.xml["keystore"], "keystore", "key", "id")
    
    #keygroups
    keygroups = cElementTree.SubElement(root,"keygroups")
    for k,v in dump.xml["keygroups"].iteritems():
        if len(v) == 0: #does not record empty group
            continue
        
        keygroup_sub = cElementTree.SubElement(taginfo, k)
        
        for keyname in v:
            keyid_sub = cElementTree.SubElement(keygroup_sub, "keyid")
            keyid_sub.set("id", keyname)
    
    #write data
    dump.xml["data"]._toXML(root)
    #TODO include DTD
    
    indent(root)
    tree = cElementTree.ElementTree(root)
    tree.write(filePath, "UTF-8", True)

class dump(object):
    def __init__(self):
        self.xml                = {}
        self.xml["misc"]        = {}
        
        self.xml["reader"]                 = {}
        self.xml["reader"]["manufacturer"] = "unknown"
        self.xml["reader"]["model"]        = "unknown"
        self.xml["reader"]["version"]      = "unknown"
        self.xml["reader"]["firmware"]     = "unknown"
        
        self.xml["environment"]              = {}
        self.xml["environment"]["datetime"]  = datetime.datetime.now()
        self.xml["environment"]["position"]  = (0.0,0.0, None,) 
        self.xml["environment"]["altitude"]  = (0.0, "M", None,)
        self.xml["environment"]["location"] = ("", sys.maxint, "M","", None,)
        self.xml["environment"]["owner"]     = "unknown"
        
        self.xml["taginfo"]             = {}
        self.xml["taginfo"]["standard"] = "unknown"
        self.xml["taginfo"]["pixnn"]    = 0
        self.xml["taginfo"]["pixss"]    = 0
        self.xml["taginfo"]["uid"]      = hexList()
        
        self.xml["keystore"]    = {}
        self.xml["keygroups"]   = {}
        self.xml["data"]        = dataGroup()

    ### misc information
    
    def isExtraInformation(self, informationName):
        #informationName is hashable + stringable ?
            #need to be hashable because it is stored into a directory
            #need to be stringable because it will be stored in xml text file
        
        if not hasattr(informationName,"__str__"):
            raise dumpManagerException("(dumpManager) isExtraInformation, the information name must be able to be convert into string")
        
        return str(informationName) in self.xml["misc"]
    
    def getExtraInformation(self, informationName):
        if not hasattr(informationName,"__str__"):
            raise dumpManagerException("(dumpManager) isExtraInformation, the information name must be able to be convert into string")
            
        if not str(informationName) in self.xml["misc"]:
            raise dumpManagerException("(dumpManager) isExtraInformation, the information name is not in the misc dictionnary")
            
        #return value
        return self.xml["misc"][str(informationName)] 
    
    def setExtraInformation(self, informationName, informationValue):
        if not hasattr(informationName,"__str__"):
            raise dumpManagerException("(dumpManager) setExtraInformation, the information name must be able to be convert into string")
        
        if not hasattr(informationValue,"__str__"):
            raise dumpManagerException("(dumpManager) setExtraInformation, the information value must be able to be convert into string")
        
        self.xml["misc"][str(informationName)] = str(informationValue)

    def unsetExtraInformation(self, informationName):
        if not hasattr(informationName,"__str__"):
            return
            
        if str(informationName) in self.xml["misc"]:
            del self.xml["misc"][str(informationName)]

    ### tag environment informations
    
    def _setString(self, parent, key, value):
        #no need to check parent or the key, this method is only used inside of the class
    
        if value == None or type(value) != str:
            raise dumpManagerException("(dumpManager) setString, the "+key+" must be a valid string")
    
        self.xml[parent][key] = value
    
    def getOwner(self):
        return self.xml["environment"]["owner"]
    
    def setOwner(self, owner):
        self._setString("environment", "owner", owner)
    
    ##
    
    def getLocation(self):
        return self.xml["environment"]["location"][0]
    
    def setLocation(self, placename, distance, unit = "M", distanceType = None, dtime = None):
        if not isValidInt(distance, 0, 25000):
            raise dumpManagerException("(dumpManager) setLocation, invalid distance, must be an integer between 0 and 25000")
    
        if type(unit) != str and unit not in ALTITUDE_UNITS:
            raise dumpManagerException("(dumpManager) setLocationFixTime, distance unity, must be a string representation of a valid unity (M or F)")
    
        if distanceType != None and type(distanceType) != str:
            raise dumpManagerException("(dumpManager) setLocationFixTime, distance type must be a valid string")
    
        if dtime !=None and not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setLocationFixTime, invalid fix time, must be a None value or an instance of datetime")
    
        self.xml["environment"]["location"] = (placename, distance, unit, distanceType, dtime,)
    
    def getLocationDistance(self):
        return self.xml["environment"]["location"][1]
    
    def setLocationDistance(self, distance):
        if not isValidInt(altitude, 0, 25000):
            raise dumpManagerException("(dumpManager) setLocationDistance, invalid distance, must be an integer between 0 and 25000")
            
        self.xml["environment"]["location"] = (self.xml["environment"]["location"][0],distance, self.xml["environment"]["location"][2], self.xml["environment"]["location"][3], self.xml["environment"]["location"][4],)
        
    def getLocationDistanceUnit(self):
        return self.xml["environment"]["location"][2]
    
    def setLocationDistanceUnit(self, unit = "M"):
        if type(unit) != str and unit not in ALTITUDE_UNITS:
            raise dumpManagerException("(dumpManager) setLocationDistanceUnit, altitude unity must be a string representation of a valid unity (M or F)")
        
        self.xml["environment"]["location"] = (self.xml["environment"]["location"][0], self.xml["environment"]["location"][1], unit, self.xml["environment"]["location"][3], self.xml["environment"]["location"][4],)
        
    def getLocationDistanceType(self):
        return self.xml["environment"]["location"][3]
    
    def setLocationDistanceType(self, distanceType):
        if type(distanceType) != str:
            raise dumpManagerException("(dumpManager) setLocationDistanceType, distance type must be a valid string")
    
        self.xml["environment"]["location"] = (self.xml["environment"]["location"][0], self.xml["environment"]["location"][1], self.xml["environment"]["location"][2], distanceType, self.xml["environment"]["location"][4],)
        
    def getLocationFixTime(self):
        return self.xml["environment"]["location"][4]
    
    def setLocationFixTime(self, dtime=None):
        if dtime !=None and not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setLocationFixTime, invalid fix time, must be a None value or an instance of datetime")
        
        self.xml["environment"]["location"] = (self.xml["environment"]["location"][0], self.xml["environment"]["location"][1], self.xml["environment"]["location"][2], self.xml["environment"]["location"][3], dtime,)
    ##
    
    def getAltitude(self):
        return self.xml["environment"]["altitude"]
    
    def getAltitudeFloat(self):
        return self.xml["environment"]["altitude"][0]
        
    def setAltitude(self, altitude, unit = "M", dtime=None):
        if not isValidInt(altitude, -10000, 10000):
            raise dumpManagerException("(dumpManager) setAltitude, invalid altitude, must be an integer between -10000 and 10000")
            
        if type(unit) != str and unit not in ALTITUDE_UNITS:
            raise dumpManagerException("(dumpManager) setAltitude, altitude unity, must be a string representation of a valid unity (M or F)")
            
        #check dtime
        if dtime !=None and not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setAltitude, invalid fix time, must be a None value or an instance of datetime")
        
    
        if altitude == None or (type(altitude) != int and type(altitude) != float) or altitude < -10000 or altitude > 10000:
            raise dumpManagerException("(dumpManager) setAltitude, invalid altitude")
    
        self.xml["environment"]["altitude"] = (altitude, unit, dtime,)
    
    def getAltitudeUnity(self):
        return self.xml["environment"]["altitude"][1]
        
    def setAltitudeUnity(self, unit = "M"):
        if type(unit) != str and unit not in ALTITUDE_UNITS:
            raise dumpManagerException("(dumpManager) setAltitudeUnity, altitude unity, must be a string representation of a valid unity (M or F)")
    
        self.xml["environment"]["altitude"] = (self.xml["environment"]["altitude"][0],unit,self.xml["environment"]["altitude"][2],)
    
    def getAltitudeFixTime(self):
        return self.xml["environment"]["altitude"][2]

    def setAltitudeFixTime(self, dtime = None):
        #check dtime
        if dtime !=None and not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setAltitudeFixTime, invalid fix time, must be an instance of datetime")
        
        self.xml["environment"]["altitude"] = (self.xml["environment"]["altitude"][0],self.xml["environment"]["altitude"][1], dtime,)
    
    ##
    
    def getPosition(self):
        return self.xml["environment"]["position"][0:2]
    
    def getPositionFixTime(self):
        return self.xml["environment"]["position"][2]

    def setPositionFixTime(self, dtime):
        #check dtime
        if not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setPositionFixTime, invalid fix time, must be a None value or an instance of datetime")
        
        self.xml["environment"]["position"] = (self.xml["environment"]["position"][0],self.xml["environment"]["position"][1], dtime,)

    def setPosition(self, lat, lon, dtime=None):
        #check lat/lon
        if not isValidFloat(lat, -90.0, 90.0):
            raise dumpManagerException("(dumpManager) setPosition, invalid latitude, must be a float between -90 and 90")
            
        if not isValidFloat(lon, -180.0, 180.0):
            raise dumpManagerException("(dumpManager) setPosition, invalid longitude, must be a float between -180 and 180")
        
        #check dtime
        if dtime !=None and not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setPosition, invalid fix time, must be a None value or an instance of datetime")
        
        self.xml["environment"]["position"] = (lat, lon, dtime,)
        
    ### date/time information
        #XXX for the parsing : isinstance(dateutil.parser.parse(string), datetime.datetime) == True
        
    def getDateString(self):
        return self.xml["environment"]["datetime"].date().isoformat()
    
    def getDate(self):
        return dateutil.parser.parse(self.xml["environment"]["datetime"]).date() 
    
    def setDate(self, date):
        if type(date) == str:
            self.xml["environment"]["datetime"] = datetime.combine(dateutil.parser.parse(date).date(), self.xml["environment"]["datetime"].timez())
        elif isinstance(date, datetime.date):
            self.xml["environment"]["datetime"] = datetime.combine(date, self.xml["environment"]["datetime"].timez())
        else:
            raise dumpManagerException("(dumpManager) setDate, the date must be an instance of datetime.date") 
    
    def getTimeString(self):
        return self.xml["environment"]["datetime"].time().isoformat()
    
    def getTime(self):
        return self.xml["environment"]["datetime"].time()
    
    def getDateTimeString(self):
        return self.xml["environment"]["datetime"].isoformat()
    
    def getDateTimeObject(self):
        return self.xml["environment"]["datetime"]
    
    def setTime(self, time):
        if type(time) == str:
            self.xml["environment"]["datetime"] = datetime.combine(self.xml["environment"]["datetime"].date(), dateutil.parser.parse(time).time())
        elif isinstance(time, datetime.time) :
            self.xml["environment"]["datetime"] = datetime.combine(self.xml["environment"]["datetime"].date(), time)
        else:
            raise dumpManagerException("(dumpManager) setTime, the time must be an instance of datetime.time") 

    def setDateTime(self, dtime):
        if type(dtime) == str:
            self.xml["environment"]["datetime"] = dateutil.parser.parse(dtime)
        elif isinstance(dtime, datetime.datetime):
            self.xml["environment"]["datetime"] = dtime
        else:
            raise dumpManagerException("(dumpManager) setDateTime, the dtime must be an instance of datetime.datetime")

    def setCurrentDate(self):
        self.xml["environment"]["datetime"] = datetime.combine(datetime.datetime.now().date(), self.xml["environment"]["datetime"].timez())
        
    def setCurrentTime(self):
        self.xml["environment"]["datetime"] = datetime.combine(self.xml["environment"]["datetime"].date(), datetime.datetime.now().timez())
        
    def setCurrentDatetime(self):
        self.xml["environment"]["datetime"] = datetime.datetime.now()
    
    ### tag information
    
    def getCommunicationStandard(self):
        return self.xml["taginfo"]["standard"]
    
    def setCommunicationStandard(self, standard):
        self._setString("taginfo", "standard", standard)
    
    def getUID(self): 
        return self.xml["taginfo"]["uid"]
    
    def getUIDString(self):
        return str(self.xml["taginfo"]["uid"])
    
    def setUID(self, uid):
        self.xml["taginfo"]["uid"] = hexList(uid)
    
    def setPIX(self, nn, ss):
        if not isValidInt(nn,0,0xFFFF):
            raise dumpManagerException("(dumpManager) setPIX, the nn must be a valid byte value, <"+str(nn)+"> is not valid")
        
        if not isValidByte(ss):
            raise dumpManagerException("(dumpManager) setPIX, the ss must be a valid byte value, <"+str(ss)+"> is not valid")
        
        self.xml["taginfo"]["pixnn"] = nn
        self.xml["taginfo"]["pixss"] = ss
    
    def getPixNNString(self):
        return str(self.xml["taginfo"]["pixnn"])
        
    def getPixSSString(self):
        return str(self.xml["taginfo"]["pixss"])
    
    def getPixNN(self):
        return self.xml["taginfo"]["pixnn"]
    
    def getPixSS(self):
        return self.xml["taginfo"]["pixss"]
    
    ### reader information
    
    def getReaderManufacturer(self):
        return self.xml["reader"]["manufacturer"]
    
    def setReaderManufacturer(self, manufacturer):
        self._setString("reader", "manufacturer", manufacturer)
    
    def getReaderModel(self):
        return self.xml["reader"]["model"]
    
    def setReaderModel(self, model):
        self._setString("reader", "model", model)
    
    def getReaderVersion(self):
        return self.xml["reader"]["version"]
    
    def setReaderVersion(self, version):
        self._setString("reader", "version", version)
    
    def getReaderFirmwareVersion(self):
        return self.xml["reader"]["firmware"]
    
    def setReaderFirmwareVersion(self, version):
        self._setString("reader", "firmware", version)
        
    ### keystore
    
    def setKey(self, keyName, value):
        self.xml["keystore"][keyName] = hexList(value)
    
    def isKeyExist(self, keyName):
        return keyName in self.xml["keystore"]
    
    def getKeyString(self, keyName):
        return str(self.xml["keystore"][keyName])
    
    def getKey(self, keyName):
        self.xml["keystore"][keyName]
    
    def createKeyGroup(self, keyGroupName):
        if version == None or type(version) == str:
            raise dumpManagerException("(dumpManager) createKeyGroup, the version must be a valid string")

        self.xml["keygroups"][keyGroupName] = {}
        
    def associateKeyAndGroup(self, keyName, keyGroupName):
        #keyGroupName must exist
        if keyGroupName not in self.xml["keygroups"]:
            self.xml["keygroups"][keyGroupName] = {} #if not, create it
        
        #keyName must exist
        if keyName not in self.xml["keystore"]:
            raise dumpManagerException("(dumpManager) associateKeyAndGroup, the key name does not exist")
    
        self.xml["keygroups"][keyGroupName][keyName] = True
    
    def getKeysNameInGroup(self, keyGroupName):
        if keyGroupName not in self.xml["keygroups"]:
            raise dumpManagerException("(dumpManager) getKeysNameInGroup, the key group name does not exist")
    
        return self.xml["keygroups"][keyGroupName].keys()
    
    def isKeyGroupNameExist(self, keyGroupName):
        return keyGroupName in self.xml["keygroups"]
    
    ### data management
    
    def addDataGroup(self, groupName):
        if groupName == None or type(version) == str:
            raise dumpManagerException("(dumpManager) addDataGroup, the group name must be a valid string")
            
        self.xml["data"].addSubgroup(groupName)
    
    def addDataSector(self, sectorID, data):
        if not isAValidByteList(data):
            raise dumpManagerException("(dumpManager) addDataSector, the data must be a non empty byte list")
    
        self.xml["data"].addDataSector(sectorID, data)

    def getDataGroup(self, path=""):
        #path will be something like / or /toto/titi/ or /toto/titi or toto or ...
        
        if path == None or type(path) != str:
            raise dumpManagerException("(dumpManager) getDataGroup, invalid data path, must be a string")
        
        path_tokens = path.split("/")
        currentDataGroup = self.xml["data"]
        
        for token in path_tokens:
            if len(token) == 0: #don't care about empty token path
                continue
        
            if token in currentDataGroup.subGroup:
                currentDataGroup = currentDataGroup.subGroup[token]
            else:
                return None
        
        return currentDataGroup

DATAGROUPFLAG_LOCKED      = "locked"
DATAGROUPFLAG_READONLY    = "readonly"
DATAGROUPFLAG_WRITABLE    = "writable"
DATAGROUPFLAG_KEYTOREAD   = "readkey"
DATAGROUPFLAG_KEYTOWRITE  = "writekey"
DATAGROUPFLAG_KEYTOCHANGE = "changekey"
DATAGROUPFLAG_MASTERKEY   = "masterkey"
DATAGROUPFLAG_KEYTOLIST   = "listkey"
DATAGROUPFLAG_KEYA        = "keyA"
DATAGROUPFLAG_KEYB        = "keyB"
DATAGROUPFLAG_RAW         = "raw"
#DATAGROUPFLAG_... #XXX add flag if necessary


class dataGroup(object):
    def __init__(self, keyGroup = None):
        self.subGroup = {}
        self.data     = {}
        self.misc     = {}
        
        #TODO keyGroup must exist or None
        
        self.keyGroup = keyGroup
            #TODO search after a key into the keygroup then in the global keylist
        
        self.attributes = {}
    
    def addSubgroup(self, name):
        newgroup = dataGroup()
        self.subGroup[name] = newgroup
        return newgroup
    
    def addDataSector(self, sectorID, data):
        self.data[sectorID] = (hexList(data),{},)
    
    def addMisc(self, key, value):
        self.misc[key] = value
    
    def getSector(self, sectorID):
        return self.data[sectorID][0]
    
    def setSectorAttribute(self, sectorID, attribute, value):
        #TODO check params
    
        self.data[sectorID][1][attribute] = value
        
    def removeSectorAttribute(self, sectorID, attribute):
        pass #TODO
    
    def setAttribute(self, attribute, value):
        #TODO check params
        
        self.attributes[attribute] = value
        
    def removeAttribute(self, attribute):
        pass #TODO
    
    def setKeyGroup(self, keyGroup):
        pass #TODO
    
    def _toXML(self, parent, name = None):
        datagroup = cElementTree.SubElement(parent,"datagroup")
        #TODO write attribute
        
        #TODO write keygroup
        
        #build misc
        if len(self.misc) > 0:
            buildXMLList(datagroup, self.misc, "misc", "miscitem", "key") 
        
        #build data
        data = cElementTree.SubElement(datagroup,"data")
        for kdata,vdata in self.data.iteritems():
            ldata = cElementTree.SubElement(data,"data")
            ldata.set("id",str(kdata))
            ldata.text = str(vdata[0])
        
            for katt, vatt in vdata[1].iteritems():
                ldata.set(katt,str(vatt))
        
        #build subgroup
        subgroup = cElementTree.SubElement(datagroup,"subgroups")
        for k,v in self.subGroup.iteritems():
            v._toXML(subgroup, k)

