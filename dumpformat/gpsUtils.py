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

#TODO see the gps management in the parsing system
    #no need to recreate what already exists

class gpsCoordinates(object):
    def __init__(self):
        #TODO try to manage several coord format and always convert it in the same way
        #50.750359,3.816833 (maps)
        #XXX ??? (format gpsd)
    
        pass #TODO
    
    #TODO parsing + getters/setters + toString + ...
    
class gpsLine(object):
    def __init__(self):
        pass #TODO
    
#TODO utils function on coordinates
    #distance between 2 points
    #distance between a point and a line(two points)
    
    #implement other function from http://www.movable-type.co.uk/scripts/latlong.html
