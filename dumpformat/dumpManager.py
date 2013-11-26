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
    #-faire les getters
    #-comment structure le stockage en memoire pour pouvoir le reconvertir facilement et rapidement en xml?
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
    #http://docs.python.org/2/library/xml.etree.elementtree.html

from exception import dumpManagerException
import os
import datetime
import xml.etree.cElementTree

MISC_RESERVED_KEYWORD = ["date", "time", "position", "altitude", "location", "owner"] #... complete if necessary    

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

class dumpManager(object):
    def __init__(self, filePath = None):
        self.setFilePath(filePath)
        
        self.xml                = {}
        self.xml["misc"]        = {}
        self.xml["reader"]      = {}
        self.xml["environment"] = {}
        self.xml["taginfo"]     = {}
        self.xml["keystore"]    = {}
        self.xml["keygroups"]   = {}
        self.xml["data"]        = dataGroup()
    
    def setFilePath(self, filePath):
        if filePath == None or type(filePath) == str or len(filePath) == 0:
            raise dumpManagerException("(dumpManager) setFilePath, invalid file path, it must be a non empty string.  <"+str(filePath)+">")
            
        if not os.path.exists(filePath) and not os.access(os.path.dirname(filePath), os.W_OK):
            raise dumpManagerException("(dumpManager) setFilePath, the selected file does not exist or you don't have the correct right to read.  And you don't have the right to create a file here.  <"+str(filePath)+">")
            
        self.filePath = filePath
        
    def checkFile(self, filePath = None):
        if self.filePath == None and filePath == None:
            raise dumpManagerException("(dumpManager) load, no filePath specified")
        
        if filePath != None:
            fpath = filePath
        else:
            fpath = self.filePath
        
        if not os.path.exists(fpath):
            raise dumpManagerException("(dumpManager) setFilePath, the selected file does not exist or you don't have the correct right to read.  <"+str(fpath)+">")
            
        #TODO check the file
        
    def load(self, filePath = None):
        if self.filePath == None and filePath == None:
            raise dumpManagerException("(dumpManager) load, no filePath specified")
        
        if filePath != None:
            fpath = filePath
        else:
            fpath = self.filePath
        
        if not os.path.exists(fpath):
            raise dumpManagerException("(dumpManager) setFilePath, the selected file does not exist or you don't have the correct right to read.  <"+str(fpath)+">")
            
        #TODO load the dump in xml format
            #qlso possible with import xml
        
    def save(self, filePath = None):
        if self.filePath == None and filePath == None:
            raise dumpManagerException("(dumpManager) save, no filePath specified")
        
        if filePath != None:
            fpath = filePath
        else:
            fpath = self.filePath
        
        if not os.access(os.path.dirname(filePath), os.W_OK):
            raise dumpManagerException("(dumpManager) save, you don't have the right to create a file here. Or the path is invalid : <"+str(filePath)+">")
            
        #save the dump in xml format
        root = cElementTree.Element("dump")
        
        #reader
        reader = cElementTree.SubElement(root,"reader")
        for k,v in self.xml["reader"].iteritems():
            reader_sub = ET.SubElement(reader, k)
            reader_sub.text = v
        
        #environment
        env = cElementTree.SubElement(root,"environment")
        for k,v in self.xml["environment"].iteritems():
            env_sub = ET.SubElement(env, k)
            env_sub.text = v
        
        #misc
        misc = cElementTree.SubElement(root,"misc")
        for k,v in self.xml["misc"].iteritems():
            misc_sub = ET.SubElement(misc, "miscitem")
            field2.set("key", k)
            misc_sub.text = v
        
        #taginfo
        taginfo = cElementTree.SubElement(root,"taginfo")
        for k,v in self.xml["taginfo"].iteritems():
            taginfo_sub = ET.SubElement(taginfo, k)
            taginfo_sub.text = v
        
        #keystore
        keystore = cElementTree.SubElement(root,"keystore")
        for k,v in self.xml["keystore"].iteritems():
            keystore = ET.SubElement(taginfo, "key")
            field2.set("id", k)
            taginfo_sub.text = v
        
        #keygroups
        keygroups = cElementTree.SubElement(root,"keygroups")
        for k,v in self.xml["keygroups"].iteritems():
            if len(v) == 0: #does not record empty group
                continue
        
            keygroup_sub = ET.SubElement(taginfo, k)
            
            for keyname in v:
                keyid_sub = ET.SubElement(keygroup_sub, "keyid")
                field2.set("id", keyname)
        
        #write data
        self.xml["data"]._toXML(root)
        
        tree = ET.ElementTree(root)
        tree.write(fpath)
        
    
    ### misc information
    
    def setOwner(self, owner):
        if owner == None or type(owner) == str:
            raise dumpManagerException("(dumpManager) setOwner, the owner must be a valid string")
    
        self.xml["environment"]["owner"] = owner
    
    def addExtraInformation(self, informationName, informationValue):
        if informationName == None or type(informationName) == str:
            raise dumpManagerException("(dumpManager) setOwner, the information name must be a valid string")

        self.xml["misc"][informationName] = str(informationValue)

    ### position/location informations
     
    def setLocation(self, locationDescription):
        if locationDescription == None or type(locationDescription) == str:
            raise dumpManagerException("(dumpManager) setLocation, the location must be a valid string")
    
        self.xml["environment"]["location"] = locationDescription
        
    def setAltitude(self, altitude):
        if altitude == None or type(altitude) != int or altitude < -10000 or altitude > 10000:
            raise dumpManagerException("(dumpManager) setAltitude, the owner must be a valid string")
    
        self.xml["environment"]["location"] = str(altitude)
        
    def setPosition(self, coord):
        
        #TODO try to manage several coord format and always convert it in the same way
        #50.750359,3.816833 (maps)
        #XXX ??? (format gpsd)
        
        self.xml["environment"]["position"] = str(coord)
    
    ### date/time information
    
    def setDate(self, date):
        if date == None or not isinstance(date, datetime.date):
            raise dumpManagerException("(dumpManager) setDate, the date must be an instance of datetime.date") 
        
        self.xml["environment"]["date"] = date.isoformat()
        
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
    
    def setCommunicationStandard(self, standard):
        if locationDescription == None or type(locationDescription) == str:
            raise dumpManagerException("(dumpManager) setLocation, the owner must be a valid string")
    
        self.xml["taginfo"]["standard"] = standard
    
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
        
    ### reader information
    
    def setReaderManufacturer(self, manufacturer):
        if manufacturer == None or type(manufacturer) == str:
            raise dumpManagerException("(dumpManager) setReaderManufacturer, the manufacturer must be a valid string")
    
        self.xml["reader"]["manufacturer"] = manufacturer
    
    def setReaderModel(self, model):
        if model == None or type(model) == str:
            raise dumpManagerException("(dumpManager) setReaderModel, the model must be a valid string")
    
        self.xml["reader"]["model"] = manufacturer
        
    def setReaderVersion(self, version):
        if version == None or type(version) == str:
            raise dumpManagerException("(dumpManager) setReaderVersion, the version must be a valid string")
            
        self.xml["reader"]["version"] = manufacturer
        
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
        
    ### data management
    
    def addDataGroup(self, groupName):
        if groupName == None or type(version) == str:
            raise dumpManagerException("(dumpManager) addDataGroup, the group name must be a valid string")
            
        self.xml["data"].addSubgroup(groupName)
    
    def addDataSector(self, sectorID, data):
        if not isAValidByteList(data):
            raise dumpManagerException("(dumpManager) addDataSector, the data must be a non empty byte list")
    
        #None key is already in the self.xml["data"][] ?
        self.xml["data"].addDataSector(sectorID, data)

class dataGroup(object):
    def __init__(self):
        self.subGroup = {}
        self.data     = {}
        self.misc     = {} #TODO
        self.keyGroup = None

    def addSubgroup(self, name):
        newgroup = dataGroup()
        self.subGroup[name] = newgroup
        return newgroup
        
    def addDataSector(self, sectorID, data):
        self.data[sectorID] = data
    
    def _toXML(self, parent):
        datagroup = cElementTree.SubElement(parent,"keygroups")
    
        #TODO misc
        
        #TODO data
        
        #TODO subgroup
        
        
        
        
        
        
        
        
        
        
        
        
        
        
