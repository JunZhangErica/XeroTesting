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
    
    
def setReadOnlyElemVal(driver, id, val):
    js = "document.getElementById('"+id+"').removeAttribute('readonly')"
    driver.execute_script(js)
    driver.find_element_by_id(id).send_keys(val)
    return driver


    