#!/usr/bin/python
# -*- coding: utf-8 -*- 

#Copyright (C) 2013 Jonathan Delvaux <dumpformat@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from dumpformat import dumpManager 

#TODO test
    #try to save .test.xml does not work, why ?

class mltriesTest(unittest.TestCase):
    def setUp(self):
        self.d = dumpManager()
        
    def test_init(self):
        self.d.save("./test.xml")

    def test_

    def test_load(self):
        pass
        
        #TODO
            #save then load and compare

if __name__ == '__main__':
    unittest.main()    