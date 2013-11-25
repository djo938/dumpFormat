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

from exception import dumpManagerException
import os
import datetime

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
        
        self.xml              = {}
        self.xml["misc"]      = {}
        self.xml["reader"]    = {}
        self.xml["taginfo"]   = {}
        self.xml["keystore"]  = {}
        self.xml["keygroups"] = {}
        self.xml["data"]      = {}
    
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
        
    def save(self, filePath = None):
        if self.filePath == None and filePath == None:
            raise dumpManagerException("(dumpManager) save, no filePath specified")
        
        if filePath != None:
            fpath = filePath
        else:
            fpath = self.filePath
        
        #TODO what append if the path is invalid ?
        if not os.access(os.path.dirname(filePath), os.W_OK):
            raise dumpManagerException("(dumpManager) save, you don't have the right to create a file here.  <"+str(filePath)+">")
            
        #TODO save the dump in xml format
    
    ### misc information
    
    def setOwner(self, owner):
        if owner == None or type(owner) == str:
            raise dumpManagerException("(dumpManager) setOwner, the owner must be a valid string")
    
        self.xml["misc"]["owner"] = owner
    
    def addExtraInformation(self, informationName, informationValue):
        if informationName == None or type(informationName) == str:
            raise dumpManagerException("(dumpManager) setOwner, the information name must be a valid string")
        
        if informationName in MISC_RESERVED_KEYWORD:
            #TODO call the corresponding method
            pass #TODO
        
        self.xml["misc"][informationName] = str(informationValue)

    ### position/location informations
     
    def setLocation(self, locationDescription):
        if locationDescription == None or type(locationDescription) == str:
            raise dumpManagerException("(dumpManager) setLocation, the location must be a valid string")
    
        self.xml["misc"]["location"] = locationDescription
        
    def setAltitude(self, altitude):
        if altitude == None or type(altitude) != int or altitude < -10000 or altitude > 10000:
            raise dumpManagerException("(dumpManager) setAltitude, the owner must be a valid string")
    
        self.xml["misc"]["location"] = str(altitude)
        
    def setPosition(self, coord):
        
        #TODO try to manage several coord format and always convert it in the same way
        #50.750359,3.816833 (maps)
        #XXX ??? (format gpsd)
        
        pass #TODO
    
    ### date/time information
    
    def setDate(self, date):
        if date == None or not isinstance(date, datetime.date):
            raise dumpManagerException("(dumpManager) setDate, the date must be an instance of datetime.date") 
        
        self.xml["misc"]["date"] = date.isoformat()
        
    def setTime(self, time):
        if time == None or not isinstance(time, datetime.time):
            raise dumpManagerException("(dumpManager) setTime, the time must be an instance of datetime.time") 
        
        self.xml["misc"]["time"] = time.isoformat()
        
    def setDateTime(self, dtime):
        if dtime == None or not isinstance(dtime, datetime.datetime):
            raise dumpManagerException("(dumpManager) setDateTime, the dtime must be an instance of datetime.datetime")
        
        self.xml["misc"]["date"] = dtime.date().isoformat()
        self.xml["misc"]["time"] = dtime.time().isoformat()
        
    def setCurrentDate(self):
        d = datetime.now()
        self.xml["misc"]["date"] = d.date().isoformat()
        
    def setCurrentTime(self):
        d = datetime.now()
        self.xml["misc"]["time"] = d.time().isoformat()
        
    def setCurrentDatetime(self):
        d = datetime.now()
        self.xml["misc"]["date"] = d.date().isoformat()
        self.xml["misc"]["time"] = d.time().isoformat()
    
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
        pass #TODO
        
    def associateKeyAndGroup(self, keyName, keyGroupName, keyID):
        #TODO keyName must exist
        #TODO keyGroupName must exist
    
        pass #TODO associate
        
    ### data management
    
    def addDataGroup(self, groupName, groupID = None):
        pass #TODO
    
    def addGroupToGroup(self, parentGroupName, childGroupName):
        pass #TODO 
    
    def addDataSector(self, sectorID, data, parentGroupName = None):
        if not isAValidByteList(data):
            raise dumpManagerException("(dumpManager) isAValidByteList, the data must be a non empty byte list")
    
        pass #TODO
        
        
