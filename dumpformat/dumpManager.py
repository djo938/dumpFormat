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

#XXX
    #http://docs.python.org/2/library/xml.etree.elementtree.html
    #gpsCoordinates

from exception import dumpManagerException
import os
#import collections #isinstance(informationName, collections.Hashable)
import datetime
from xml.etree import cElementTree
import dateutil.parser #TODO XXX announce/install the depedency XXX

def checkFile(filePath):
    if filePath == None and type(filePath) != str:
        raise dumpManagerException("(dumpManager) checkFile, invalid file path")
    
    if not os.path.exists(filePath):
        raise dumpManagerException("(dumpManager) checkFile, the selected file does not exist or you don't have the correct right to read.  <"+str(filePath)+">")
    
    #TODO check the file

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
    tree.write(fpath, "UTF-8", True)

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def byteListToString(blist, space = " "):
    return space.join('0x{:02x}'.format(x) for x in blist)

def isValidByte(b):
    if b == None or type(b) != int or b < 0 or b > 256:
        return False
    
    return True 

def isAValidByteList(byteList):
    if byteList == None or not hasattr(byteList, '__iter__') or len(byteList) == 0:
        return False
    
    for b in byteList:
        if b == None or type(b) != int or b < 0 or b > 256:
            return False
    
    return True 

def buildXMLList(parent, dico, dicoName, itemName = None, keyName = None):
    misc = cElementTree.SubElement(parent,dicoName)
    
    if keyName == None:
        keyName = "id"
    
    for k,v in dico.iteritems():
        if itemName == None:
            misc_sub = cElementTree.SubElement(misc, k)
        else:
            misc_sub = cElementTree.SubElement(misc, itemName)
            misc_sub.set(keyName, k)
        
        if isinstance(v, datetime.datetime):
            misc_sub.text = v.isoformat()
        else:
            misc_sub.text = str(v)

class hexList(list):
    def __init__(self, value = None):
        if value != None:
            if type(value) == str:
                #allowed format
                #FFFFFfff
                #0xFFFFFfff
                #FF, FF,ff, ff
                #0xFF, 0xff, 0XFF, 0Xff,
                #0xFF 0xff 0XFF 0Xff
                value = value.strip()
                if len(value) > 0: #non empty string
                    if value.count(",") > 0: #token separate with comma
                        values = []
                        value_splitted = value.split(",")
                        for vs in value_splitted:
                            values.append(int(vs,16)) #could raise valueError
                            
                    elif value.count(" ") > 0: #token separate with space    
                        values = []
                        value_splitted = value.split(" ")
                        for vs in value_splitted:
                            values.append(int(vs,16)) #could raise valueError
                            
                    else: #token agragated
                        if value.startswith("0x") or value.startswith("0X"):
                            value = value[2:]
                        elif value.startswith("x") or value.startswith("X"):
                            value = value[1:]
                        
                        if (len(value)%2) != 0:
                            value = "0"+value
                        
                        values = []
                        for i in range(0,len(value),2):
                            values.append(int(value[i:i+2],16)) #could raise valueError
                            
                    list.__init__(self,values)
            elif isAValidByteList(value):
                list.__init__(self,value)
            else:
                raise ValueError("(hexList) __init__, need a list of byte or a byte string")
    
    def append(self, value):
        if not isValidByte(value):
            try:
                list.append(self, int(value, 16))
                return 
            except ValueError:
                pass
            
            raise ValueError("(hexList) append, need a byte")
        list.append(self, value)
        
    def extend(self, values): 
        if values == None or not hasattr(values, '__iter__'):
            raise ValueError("(hexList) extend, need an iterable object")
        
        if not isAValidByteList(values):
            index = 0
            try:
                new_values = []
                while index < len(values):
                    new_values.append(int(values[index],16))
                    index += 1
                    
                list.extend(self, new_values)
            except ValueError:
                pass
            
            raise ValueError("(hexList) extend, not a byte item at index "+str(index))
        
        list.extend(self, values)
        
    def insert(self, index, value):
        if not isValidByte(value):
            try:
                list.insert(self, index, int(value, 16))
                return 
            except ValueError:
                pass
            
            raise ValueError("(hexList) append, need a byte")
        list.insert(self, index, value)
        
    def __setitem__(self, index, value):
        if not isValidByte(value):
            try:
                list.__setitem__(self, index, int(value, 16))
                return 
            except ValueError:
                pass
            
            raise ValueError("(hexList) append, need a byte")
        list.__setitem__(self, index, value)
    
    def __setslice__(self, index, jndex, values):
        if values == None or not hasattr(values, '__iter__'):
            raise ValueError("(hexList) extend, need an iterable object")
        
        if not isAValidByteList(values):
            index = 0
            try:
                new_values = []
                while index < len(values):
                    new_values.append(int(values[index],16))
                    index += 1
                    
                list.__setslice__(self, index, jndex, new_values)
            except ValueError:
                pass
            
            raise ValueError("(hexList) extend, not a byte item at index "+str(index))
        
        list.__setslice__(self, index, jndex, values)
        
    def __str__(self):
        return ' '.join('0x{:02x}'.format(x) for x in self)

    #can use __getslice
    #def getSectorByteArrayFromTo(self, sectorID, startingByte=0, size=None):
    #    pass    
    
    def getSectorBitStringFromTo(self, startingByte=0, size=None):
        pass #TODO voir le code dans m_extractor

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
        self.xml["environment"]["position"]  = "unknown" #TODO tuple(lat, lon, dtime) => <position dtime="">lat, lon</position>
        self.xml["environment"]["altitude"]  = "unknown" #TODO tuple(lat, lon, dtime) => <altitude dtime="" unit="">altitude</altitude>
        self.xml["environment"]["placename"] = "unknown" #TODO same as altitude and position
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
        if value == None or type(value) != str:
            raise dumpManagerException("(dumpManager) setString, the "+key+" must be a valid string")
    
        self.xml[parent][key] = value
    
    def getOwner(self):
        return self.xml["environment"]["owner"]
    
    def setOwner(self, owner):
        self._setString("environment", "owner", owner)
    
    def getLocation(self):
        return self.xml["environment"]["location"]
    
    def setLocation(self, placename, distance, unit, distanceType, dtime):
        #TODO
    
        self._setString("environment", "location", locationDescription)
    
    def getAltitude(self):
        return self.xml["environment"]["altitude"]
    
    def getAltitudeFloat(self):
        return self.xml["environment"]["altitude"]
        
    def setAltitude(self, altitude, unit, fixtime):
        #TODO
    
        if altitude == None or (type(altitude) != int and type(altitude) != float) or altitude < -10000 or altitude > 10000:
            raise dumpManagerException("(dumpManager) setAltitude, invalid altitude")
    
        self.xml["environment"]["altitude"] = float(altitude)
    
    def getAltitudeUnity(self):
        return self.xml["environment"]["altitudeUnity"]
        
    def setAltitudeUnity(self, unity = "M"):
        #TODO limit the altitude possibility (M, F, ) #XXX voir aussi ce que raconte le gpsd
    
        self._setString("environment", "altitudeUnity", unity)
    
    def getPosition(self):
        return self.xml["environment"]["position"]
    
    def setPosition(self, lat, lon, dtime):
        #TODO
            
        #init a coord object
        if isinstance(coord, gpsCoordinates)
            self.xml["environment"]["position"] = coord
        elif type(coord) == str:
            self.xml["environment"]["position"] = gpsCoordinates(coord)
        else:
            raise dumpManagerException("(dumpManager) setPosition, invalid position parameter, waiting a gpsCoordinates or a string, got "+str(type(coord)))

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
        if not isValidByte(nn):
            raise dumpManagerException("(dumpManager) setPIX, the nn must be a valid byte value, <"+str(nn)+"> is not valid")
        
        if not isValidByte(ss):
            raise dumpManagerException("(dumpManager) setPIX, the ss must be a valid byte value, <"+str(ss)+"> is not valid")
        
        self.xml["taginfo"]["pixnn"] = nn
        self.xml["taginfo"]["pixss"] = ss
    
    def getPixNN(self):
        return self.xml["taginfo"]["pixnn"]
        
    def getPixSS(self):
        return self.xml["taginfo"]["pixss"]
    
    def getPixNNInteger(self):
        """
        
        raise ValueError: if pixnn is not a valid decimal integer
        """
        return int(self.xml["taginfo"]["pixnn"])
    
    def getPixSSInteger(self):
        """
        
        raise ValueError: if pixss is not a valid decimal integer
        """
        pass int(self.xml["taginfo"]["pixss"])
    
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
    
    def getReaderFirmwareVersion(self)
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
    
    def isKeyGroupNameExist(self, keyGroupName)
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

class dataRight(object):
    
    def __init__(self):
        self.locked = None #data were writable and now are only readable
        self.read   = None #data are readable
        self.write  = None #data are writable
        
    #TODO

class dataGroup(object):
    def __init__(self):
        self.subGroup = {}
        self.data     = {}
        self.misc     = {}
        self.keyGroup = None
    
    def addSubgroup(self, name):
        newgroup = dataGroup()
        self.subGroup[name] = newgroup
        return newgroup
    
    def addDataSector(self, sectorID, data):
        self.data[sectorID] = hexList(data)
    
    def addMisc(self, key, value):
        self.misc[key] = value
    
    def getSector(self, sectorID):
        return self.data[sectorID]
        
    def _toXML(self, parent, name = None):
        datagroup = cElementTree.SubElement(parent,"datagroup")
        
        #build misc
        if len(self.misc) > 0:
            buildXMLList(datagroup, self.misc, "misc", "miscitem", "key") 
        
        #build data
        buildXMLList(datagroup, self.data, "data", "dataitem", "id")            
        
        #build subgroup
        subgroup = cElementTree.SubElement(datagroup,"subgroups")
        for k,v in self.subGroup.iteritems():
            v._toXML(subgroup, k)

