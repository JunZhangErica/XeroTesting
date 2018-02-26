#coding=utf-8

#import pickle
#import Cookie
import random 
import time
import os.path
import datetime
import traceback

#from urlparse import urlparse

from selenium import webdriver

import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from lib.ToolConfig import ToolConfig
from lib.LoginOut import LoginOut
from selenium.webdriver.chrome.options import Options

from utils.GeneralUtils import ConfigParserUtil

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")


class TestObject(object):
    def __init__(self, logger, configObj):
        self.logger = logger        
        self.configObj = configObj
        self.test_list = []
        
        self.driver = None
        chrome_info = self.configObj.getChromeInfo()
        self.chrome_path = chrome_info['path']
        
        login_info = self.configObj.getLoginInfo()
        self.login_url = login_info['url']
        self.login_user = login_info['user']
        self.login_pwd = login_info['pwd']

        
    def getTestList(self):
        return self.test_list
        
            
    def parseConf(self, path, testname):
        """
        Parse config file to create dicts
        @path: path to configuration file
        @testname: test name
        @@ return True for successful. Otherwise, False
        """
        self.config_dicts = {}
        result = True
        try:
            self.logger.debug("Step: check if %s exists", path) 
            if not os.path.exists(path): 
                return result
            
            self.logger.debug("Step: parse %s", path)    
            cf = ConfigParserUtil()
            cf.read(path)
            for section_name in cf.sections():
                if testname in section_name: 
                    vals = section_name.split(":")
                    self.logger.debug("variable name = %s", vals[1])
                    tmp_dict = {}               
                    for (name, value) in cf.items(section_name):
                        if 'variables' in section_name:
                            skey = name
                        else: 
                            item_vals = name.split("_", 2)
                            skey = "//"+item_vals[0] 
                            if "*" in item_vals[2]:
                                tmp_vals = item_vals[2].split("*")
                                skey += "[contains(" +"@" + item_vals[1] + ",\'" + tmp_vals[1] +"\')]"
                            else:
                                skey += "[@" + item_vals[1] + "=\'"  + item_vals[2] +"\']"
                        tmp_dict[skey] = value #unicode(value)
                        self.logger.debug("key = %s, value = %s", skey, value)
                    self.config_dicts[vals[1]] = tmp_dict
        except Exception, e:
            self.logger.error("Failed on parseConf with exception %s", traceback.format_exc())
            result = False
        return result       
        
   
    def getVariable(self, name):
        """
        Get dict variable with name
        """
        tmp_dict = {}
        if self.config_dicts.has_key(name) :
            tmp_dict = self.config_dicts[name]
        return tmp_dict
    
    
    def setup(self):
        """
        Do preparation before testing to be run 
        1. create chromedriver object instance
        2. load related url
        """
        result = True
        try: 
            self.logger.info("Step: Check if driver already created")
            if self.driver != None:
                logObj = LoginOut(self.driver, self.logger, self.configObj)
                result = logObj.login()
                return result
            
            self.logger.info("Step: No driver instance available. Initialize a driver object.")
            LOGGER.setLevel(logging.ERROR)
            chromeOptions = Options()
            chromeOptions.add_argument("window-size=1920x1080")
            chromeOptions.add_argument("--ignore-certificate-errors")
            chromeOptions.add_argument("--dns-prefetch-disable")
            if os.name != 'nt':
                self.driver = webdriver.Chrome(chrome_options=chromeOptions)
            else:
                self.driver = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=chromeOptions)
                self.logger.debug(self.driver.get_window_size())
            self.driver.maximize_window()
            time.sleep(1)
            
        
            self.logger.debug("Step: load url: %s", self.login_url)
            self.driver.get(self.login_url)
            
            logObj = LoginOut(self.driver, self.logger, self.configObj)
            result = logObj.login()       
            if not result:
                raise Exception("Failed to login and stop the test") 
           
            self.logger.debug("Step: set up cookie")            
            cookies = self.driver.get_cookies()
            for c in cookies:
                self.driver.add_cookie(c)
        except Exception, e: 
            self.logger.error("Failed on setup with exception %s", traceback.format_exc())
            result = False
        return result
        
            
    def setDriver(self, driver):
        self.driver = driver   
        
    
    def getDriver(self):
        return self.driver
        
        
    # do cleanup for testing
    def cleanup(self, should_quit = False):
        """
        Do clean up after the test done
        """
        try:
            self.logger.info("TEST_STEP: Log out")
            logObj = LoginOut(self.driver, self.logger, self.configObj)
            logObj.logout()
            
            self.logger.info("TEST_STEP: Quit browser")
            self.driver.quit()
            time.sleep(5)
            self.driver = None

        except Exception, e:
            self.logger.warning("Failed on cleanup with exception %s", traceback.format_exc())
            


