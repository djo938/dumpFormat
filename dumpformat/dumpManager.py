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

#TODO
    #-comment structure le stockage en memoire pour pouvoir le reconvertir facilement et rapidement en xml?
        #afin d'eviter les appels recursifs pour generer la structure sur fichier
        #et aussi pouvoir faire des recherches rapidement en mémoire
        #avec des dico ?
            #les clés doivent rester unique
            #faire une hierarchie de dico
    #be able to unset value (set to None ?)
    #allow sub data group if data at the root ? (None group name)
        #and the opposite allow data if subgroup ?
    #write empty data group ?
        #yes ?
            #print warning ?
    #what about the empty string everywhere?, some of them must be non empty
        #empty is "unknow"
    #http://docs.python.org/2/library/xml.etree.elementtree.html

from exception import dumpManagerException
import os
import datetime
from xml.etree import cElementTree

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

def byteListToString(blist):
    return ' '.join('0x{:02x}'.format(x) for x in blist)

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
        
        misc_sub.text = v

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
        
    def insert(self, index, value): #TODO
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
        self.xml["environment"]["date"]      = "unknown"
        self.xml["environment"]["time"]      = "unknown"
        self.xml["environment"]["position"]  = "unknown"
        self.xml["environment"]["altitude"]  = "unknown"
        self.xml["environment"]["placename"] = "unknown"
        self.xml["environment"]["owner"]     = "unknown"
        
        self.xml["taginfo"]             = {}
        self.xml["taginfo"]["standard"] = "unknown"
        self.xml["taginfo"]["pixnn"]    = "unknown"
        self.xml["taginfo"]["pixmm"]    = "unknown"
        self.xml["taginfo"]["uid"]      = "unknown"
        
        self.xml["keystore"]    = {}
        self.xml["keygroups"]   = {}
        self.xml["data"]        = dataGroup()

    ### misc information
    
    def isExtraInformation(self, informationName):
        pass #TODO
    
    def getExtraInformation(self, informationName):
        pass #TODO
    
    def addExtraInformation(self, informationName, informationValue):
        if informationName == None or type(informationName) == str:
            raise dumpManagerException("(dumpManager) setOwner, the information name must be a valid string")

        self.xml["misc"][informationName] = str(informationValue)

    ### tag environment informations
    
    def getOwner(self):
        return self.xml["environment"]["owner"]
    
    def setOwner(self, owner):
        if owner == None or type(owner) == str:
            raise dumpManagerException("(dumpManager) setOwner, the owner must be a valid string")
    
        self.xml["environment"]["owner"] = owner
    
    def getLocation(self):
        return self.xml["environment"]["location"]
    
    def setLocation(self, locationDescription):
        if locationDescription == None or type(locationDescription) == str:
            raise dumpManagerException("(dumpManager) setLocation, the location must be a valid string")
    
        self.xml["environment"]["location"] = locationDescription
    
    def getAltitude(self):
        return self.xml["environment"]["location"]
    
    def getAltitudeFloat(self):
        pass #TODO
    
    #TODO altitude mesure unity
    
    def setAltitude(self, altitude):
        if altitude == None or type(altitude) != int or altitude < -10000 or altitude > 10000:
            raise dumpManagerException("(dumpManager) setAltitude, the owner must be a valid string")
    
        self.xml["environment"]["location"] = str(altitude)
    
    def getPosition(self):
        return self.xml["environment"]["position"]
    
    def getPositionFloat(self):
        pass #TODO
    
    def setPosition(self, coord):        
        self.xml["environment"]["position"] = str(coord)
    
        #TODO try to manage several coord format and always convert it in the same way
        #50.750359,3.816833 (maps)
        #XXX ??? (format gpsd)
    
    ### date/time information
    
    def getDate(self):
        return self.xml["environment"]["date"]
    
    def getDateObject(self):
        pass #TODO
    
    def setDate(self, date):
        if date == None or not isinstance(date, datetime.date):
            raise dumpManagerException("(dumpManager) setDate, the date must be an instance of datetime.date") 
        
        self.xml["environment"]["date"] = date.isoformat()
    
    def getTime(self):
        return self.xml["environment"]["time"] #TODO return time object or string ?
    
    def getTimeObject(self):
        pass #TODO
    
    def getDateTimeObject(self):
        pass #TODO
    
    def setTime(self, time):
        if time == None or not isinstance(time, datetime.time):
            raise dumpManagerException("(dumpManager) setTime, the time must be an instance of datetime.time") 
        
        self.xml["environment"]["time"] = time.isoformat()
        
    def setDateTime(self, dtime):
        if dtime == None or not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setDateTime, the dtime must be an instance of datetime.datetime")
        
        self.xml["environment"]["date"] = dtime.date().isoformat()
        self.xml["environment"]["time"] = dtime.time().isoformat()
        
    def setCurrentDate(self):
        d = datetime.now()
        self.xml["environment"]["date"] = d.date().isoformat()
        
    def setCurrentTime(self):
        d = datetime.now()
        self.xml["environment"]["time"] = d.time().isoformat()
        
    def setCurrentDatetime(self):
        d = datetime.now()
        self.xml["environment"]["date"] = d.date().isoformat()
        self.xml["environment"]["time"] = d.time().isoformat()
    
    ### tag information
    
    def getCommunicationStandard(self):
        return self.xml["taginfo"]["standard"]
    
    def setCommunicationStandard(self, standard):
        if locationDescription == None or type(locationDescription) == str:
            raise dumpManagerException("(dumpManager) setLocation, the owner must be a valid string")
    
        self.xml["taginfo"]["standard"] = standard
    
    def getUID(self):
        return self.xml["taginfo"]["uid"]
    
    def getUIDHexArray(self):
        pass #TODO
    
    def setUID(self, uid):
        if not isAValidByteList(uid):
            raise dumpManagerException("(dumpManager) setUID, the uid must be a non empty byte list")
            
        self.xml["taginfo"]["uid"] = byteListToString(uid)
    
    def setPIX(self, nn, mm):
        if not isValidByte(nn):
            raise dumpManagerException("(dumpManager) setPIX, the nn must be a valid byte value, <"+str(nn)+"> is not valid")
        
        if not isValidByte(mm):
            raise dumpManagerException("(dumpManager) setPIX, the mm must be a valid byte value, <"+str(mm)+"> is not valid")
        
        self.xml["taginfo"]["pixnn"] = str(nn)
        self.xml["taginfo"]["pixmm"] = str(mm)
    
    def getPixNN(self):
        return self.xml["taginfo"]["pixnn"]
        
    def getPixMM(self):
        return self.xml["taginfo"]["pixmm"]
    
    def getPixNNInteger(self):
        pass #TODO
        
    def getPixMMInteger(self):
        pass #TODO
    
    ### reader information
    
    def getReaderManufacturer(self):
        return self.xml["reader"]["manufacturer"]
    
    def setReaderManufacturer(self, manufacturer):
        if manufacturer == None or type(manufacturer) == str:
            raise dumpManagerException("(dumpManager) setReaderManufacturer, the manufacturer must be a valid string")
    
        self.xml["reader"]["manufacturer"] = manufacturer
    
    def getReaderModel(self):
        return self.xml["reader"]["model"]
    
    def setReaderModel(self, model):
        if model == None or type(model) == str:
            raise dumpManagerException("(dumpManager) setReaderModel, the model must be a valid string")
    
        self.xml["reader"]["model"] = manufacturer
    
    def getReaderVersion(self):
        return self.xml["reader"]["version"]
    
    def setReaderVersion(self, version):
        if version == None or type(version) == str:
            raise dumpManagerException("(dumpManager) setReaderVersion, the version must be a valid string")
            
        self.xml["reader"]["version"] = manufacturer
    
    def getReaderFirmwareVersion(self)
        return self.xml["reader"]["firmware"]
    
    def setReaderFirmwareVersion(self, version):
        if version == None or type(version) == str:
            raise dumpManagerException("(dumpManager) setReaderFirmwareVersion, the version must be a valid string")
            
        self.xml["reader"]["firmware"] = manufacturer
        
    ### keystore
    
    def createKey(self, keyName, value):
        if version == None or type(version) == str:
            raise dumpManagerException("(dumpManager) setReaderFirmwareVersion, the version must be a valid string")
            
        if not isAValidByteList(value):
            raise dumpManagerException("(dumpManager) createKey, the key value must be a non empty byte list")
        
        self.xml["keystore"][keyName] = byteListToString(value)
    
    def getKey(self, keyName):
        pass #TODO
    
    def getKeyHexArray(self, keyName):
        pass #TODO
    
    def createKeyGroup(self, keyGroupName):
        if version == None or type(version) == str:
            raise dumpManagerException("(dumpManager) createKeyGroup, the version must be a valid string")

        self.xml["keygroups"][keyGroupName] = []
        
    def associateKeyAndGroup(self, keyName, keyGroupName):
        #keyGroupName must exist
        if keyGroupName not in self.xml["keygroups"]:
            raise dumpManagerException("(dumpManager) associateKeyAndGroup, the group name does not exist")
        
        #keyName must exist
        if keyName not in self.xml["keystore"]:
            raise dumpManagerException("(dumpManager) associateKeyAndGroup, the key name does not exist")
    
        self.xml["keygroups"][keyGroupName].append(keyName)
    
    def getKeysNameInGroup(self, keyGroupName):
        pass #TODO
    
    ### data management
    
    def addDataGroup(self, groupName):
        if groupName == None or type(version) == str:
            raise dumpManagerException("(dumpManager) addDataGroup, the group name must be a valid string")
            
        self.xml["data"].addSubgroup(groupName)
    
    def addDataSector(self, sectorID, data):
        if not isAValidByteList(data):
            raise dumpManagerException("(dumpManager) addDataSector, the data must be a non empty byte list")
    
        self.xml["data"].addDataSector(sectorID, data)

    def getDataGroup(self, path):
        #path will be something like / or /toto/titi/ or /toto/titi or toto or ...
    
        pass #TODO
    

class dumpManager(object):    
    def checkFile(self, filePath):
        if filePath == None and type(filePath) != str:
            raise dumpManagerException("(dumpManager) checkFile, invalid file path")
        
        if not os.path.exists(filePath):
            raise dumpManagerException("(dumpManager) checkFile, the selected file does not exist or you don't have the correct right to read.  <"+str(filePath)+">")
        
        #TODO check the file
    
    def load(self, filePath):
        if filePath == None and type(filePath) != str:
            raise dumpManagerException("(dumpManager) load, invalid file path")
        
        if not os.path.exists(fpath):
            raise dumpManagerException("(dumpManager) load, the selected file does not exist or you don't have the correct right to read.  <"+str(fpath)+">")
            
        #TODO load the dump in xml format
            #also possible with import xml
        
        #TODO return a dump object
        
    def save(self, dump, filePath):
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
        indent(root)
        tree = cElementTree.ElementTree(root)
        tree.write(fpath, "UTF-8", True)
    

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
        self.data[sectorID] = data
    
    def addMisc(self, key, value):
        self.misc[key] = value
    
    def getSector(self, sectorID):
        pass #TODO
        
    def getSectorByteArray(self, sectorID):
        pass #TODO
        
    def getSectorByteArrayFromTo(self, sectorID, startingByte=0, size=None):
        pass #TODO    
    
    def getSectorBitStringFromTo(self, sectorID, startingByte=0, size=None):
        pass #TODO 
    
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

