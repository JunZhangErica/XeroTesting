
"""
Copyright (c) 2018-2021, Jun Zhang
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name Wai Yip Tung nor the names of its contributors may be
  used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
"""

#coding=utf-8

import ConfigParser

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")


class ConfigParserUtil(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)
          
    def optionxform(self, optionstr):  
        return optionstr  


def getValueforDict(dict, keyword):
    """
    @dict: the dict to be operated with
    @keyword: word in the key
    """
    for key in dict.keys():
        if keyword in key:
            return dict[key] 
    return None

def getKeywithKeyword(dict, keyword):
    """
    @dict: the dict to be operated with
    @keyword: word in the key
    """
    for key in dict.keys():
        if keyword in key:
            return key 
    return None
    
    
def setValueforDict(dict, keyword, value):
    """
    @dict: the dict to be operated with
    @keyword: word in the key
    @value: value to be set 
    """
    for key in dict.keys():
        if keyword in key:
            dict[key] = value
    return dict
    

def delDictwithKeyword(dict, keyword):
    """
    @dict: the dict to be operated with
    @keyword: word in the key
    """
    for key in dict.keys():
        if keyword in key:
            del dict[key]
    return dict

def checkDictsUnique(dicts, keyword):
    """
    Check if there is any value in dicts not unique
    @dicts: the dicts to be operated with
    @keyword: word in the key
    @@return True for unique and False for otherwise
    """
    vals = []
    for dict in dicts:
        val = getValueforDict(dict, keyword)
        if val != None:
            if val in vals:
                return False
            vals.append(val)
    return True        
    
def setReadOnlyElemVal(driver, id, val):
    js = "document.getElementById('"+id+"').removeAttribute('readonly')"
    driver.execute_script(js)
    driver.find_element_by_id(id).send_keys(val)
    return driver


    