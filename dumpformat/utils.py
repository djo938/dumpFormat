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

from xml.etree import cElementTree
import datetime

ALTITUDE_UNITS = ("M", "F",)

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
    
    def getSectorBitStringFromTo(self, startingBit=0, size=None):
        pass #TODO voir le code dans m_extractor

def checkFile(filePath):
    if filePath == None and type(filePath) != str:
        raise dumpManagerException("(dumpManager) checkFile, invalid file path")
    
    if not os.path.exists(filePath):
        raise dumpManagerException("(dumpManager) checkFile, the selected file does not exist or you don't have the correct right to read.  <"+str(filePath)+">")
    

def isValidFloat(value,min_value=None,max_value=None):
    return  (type(value) == float or type(value) == int) and (min_value == None or value >= min_value) and (max_value == None or value <= max_value)

def isValidInt(value,min_value=None,max_value=None):
    return  type(value) == int and (min_value == None or value >= min_value) and (max_value == None or value <= max_value)

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
        k = str(k)
    
        if itemName == None:
            misc_sub = cElementTree.SubElement(misc, k)
        else:
            misc_sub = cElementTree.SubElement(misc, itemName)
            misc_sub.set(keyName, k)
        
        if isinstance(v, datetime.datetime):
            misc_sub.text = v.isoformat()
        elif k == "position":
            misc_sub.text = str(v[0])+", "+str(v[1])
            if v[2] != None:
                misc_sub.set("fixtime", v[2].isoformat())
        elif k == "location":
            misc_sub.text = v[0]
            misc_sub.set("distance", str(v[1]))
            misc_sub.set("unit", v[2])
            misc_sub.set("type", v[3])
            if v[3] != None:
                misc_sub.set("fixtime", v[4].isoformat())
            
        elif k == "altitude":
            misc_sub.text = str(v[0])
            misc_sub.set("unit", v[1])
            if v[2] != None:
                misc_sub.set("fixtime", v[2].isoformat())
        else:
            misc_sub.text = str(v)
            
        


