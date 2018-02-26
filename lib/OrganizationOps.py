#coding=utf-8

import traceback
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidElementStateException as InvalidElementStateException
from selenium.common.exceptions import TimeoutException as TimeoutException

from utils.GeneralUtils import *

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")


class OrganizationOps(object):
    """
    class to provide APIs to do operations on organizations
    NOTE: Because of limited time, only the APIs to be used by 
    TestBankAccountOps will be provided.
    """
    def __init__(self, driver, logger, configObj):
        self.driver = driver
        self.logger = logger
        self.configObj = configObj
        self.is_GST = True
        
    def setDriver(self, driver):
        self.driver = driver

    def setGST(self, enabled=True):
        self.is_GST = enabled
        
    def showOrganizationList(self):
        """
        open login dialog window by click Login link
        @@return value: True for successful, False otherwise
        """
        result = True
        try:
            try:
                xpath = "//a[contains(text(), 'Add an organisation')]"
                self.driver.find_element_by_xpath(xpath)
                return True
            except Exception, e:
                try:
                    self.driver.find_element_by_link_text("Start Trial")
                    return True
                except Exception, e:
                    self.logger.info("STEP: show organization list")
            
            my_dashboard = "https://my.xero.com/"
            self.driver.get(my_dashboard)

            try:            
                self.logger.debug("Step: verify that organization list shows up")
                xpath = "//a[contains(text(), 'Add an organisation')]"
                WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                self.driver.find_element_by_link_text("Start Trial")
        except Exception, e:
            self.logger.error("Failed on show organizations with exception: %s", traceback.format_exc())
            result = False
        return result 
    
    
    def checkOrganization(self, name):
        """
        select to check details of organization
        @@return value: True for success. False otherwise.  
        """
        self.logger.info("STEP: check the details of organization %s", name)
        result = True
        try:
            result = self.showOrganizationList()
            if not result:
                return result
            
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.LINK_TEXT, name)))
            self.driver.find_element_by_link_text(name).click()
            
            xpath = "//h2[@class='org-name']/a[text()='"+name+"']"
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        except Exception, e:
            self.logger.error("Failed on show organization %s details with exception: %s", 
                              name, traceback.format_exc())
            result = False
        return result 
    
    
    def addOrganization(self, org_dict_in, sorted_keys=None):
        """
        Add an organization
        @org_dict: organization dictionary of xpath mapped to value
                   for organization
        @sorted_keys: the ordered xpaths of keys in org_dict
        @@return value: True for success, False for otherwise
        """
        self.logger.info("STEP: add an organization")
        result = True
        try:
            org_dict = {}
            for key in org_dict_in.keys():
                org_dict[key] = org_dict_in[key]
                
            try:
                self.driver.find_element_by_link_text("Start Trial")
            except Exception, e:
                result = self.showOrganizationList()
                if not result:
                    return result
                
                self.logger.debug("Step: open window of adding organization")
                xpath = "//a[contains(text(), 'Add an organisation')]"
                org_elem = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                org_elem.click()
                
                self.logger.debug("Step: verify that the proper web page is loaded")
                WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.LINK_TEXT, "Start Trial")))
            
            self.logger.debug("Step: input all organization data and post request")
            if sorted_keys == None:
                sorted_keys = org_dict.keys()
            
            # for those items which needs to expand options for selection
            for key in sorted_keys:                  
                dict_key = getKeywithKeyword(org_dict, key)
                self.logger.debug("dict_key=%s", dict_key)
                self.logger.debug("Step: click button to show all options")
                element = self.driver.find_element_by_xpath(dict_key) 
                try:
                    element.clear()
                    time.sleep(2)
                    self.logger.debug("send value %s", org_dict[dict_key])
                    element.send_keys(org_dict[dict_key])
                    time.sleep(2)
                except InvalidElementStateException: 
                    sorted_keys.remove(key)
                    org_dict = delDictwithKeyword(org_dict, dict_key)
                    continue
                                
                xpath = "//div[contains(@id, boundlist-listEl)][contains(@id, '"+key+"')]"
                xpath +="/ul/li[@class='x-boundlist-item']"
                
                try:
                    element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                except Exception, e:
                    time.sleep(5)
                    element.send_keys(u'\ue007')
                    time.sleep(5)

                self.logger.debug("Step: remove this dict")
                org_dict = delDictwithKeyword(org_dict, dict_key)
                for index in org_dict.keys():
                    self.logger.debug("key=%s, value=%s", index, org_dict[index])
            
            if not self.is_gst:
                try:
                    self.driver.find_element_by_xpath("//input[@id='gstChk-inputEl']").click()
                    time.sleep(2)
                    org_dict = delDictwithKeyword(org_dict, key)
                except Exception, e:
                    self.logger.debug("GST property not available.")

            sorted_keys = org_dict.keys()
            for key in sorted_keys:
                element = self.driver.find_element_by_xpath(key)
                try:
                    element.clear()
                    time.sleep(2)
                    element.send_keys(org_dict[key])
                    time.sleep(2)
                except InvalidElementStateException: 
                    sorted_keys.remove(key)
                    org_dict = delDictwithKeyword(org_dict, key)
                    continue
                org_dict = delDictwithKeyword(org_dict, key)
                
            self.logger.debug("Step: trigger trial")
            element = self.driver.find_element_by_link_text("Start Trial")
            element.click()
            #NOTE: on my end, after clicking, the program hangs
            #      so just sleep here
            time.sleep(60)
            
            my_dashboard = "https://my.xero.com/"
            self.driver.get(my_dashboard)
            xpath = "//a[@class='username']"
            WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        except Exception, e:
            self.logger.error("Failed on adding organization with exception: %s", traceback.format_exc())
            result = False
        return result 

    def __getCancleNums__(self):
        """
        get cancel links
        @@return element list or exception
        """
        cancel_list = []
        try:
            xpath = "//div[@class='x-page page-dashboard']/form[@action='/!xkcD/Dashboard']"
            element = self.driver.find_element_by_xpath(xpath)
            xpath = "./div[@class='x-content']/section[@class='x-column']"
            element = element.find_element_by_xpath(xpath)
            xpath = "./div[contains(@id,'grid')][@class='x-grid-container a-fadein']"
            element = element.find_element_by_xpath(xpath)
            xpath = "./div[contains(@id,'ext-comp')][contains(@class,'x-panel-default')]"
            element = element.find_element_by_xpath(xpath)
            xpath = "./div[contains(@id,'ext-comp')][contains(@class, 'x-panel-body-default')]"
            element = element.find_element_by_xpath(xpath)
            xpath = "./div[contains(@id, 'gridview')]"
            element = element.find_element_by_xpath(xpath)
            xpath = "./table[contains(@id,'gridview')]/tbody[contains(@id,'gridview')]"
            element = element.find_element_by_xpath(xpath)
            xpath = "./tr[contains(@id,'gridview')]"
            elems = element.find_elements_by_xpath(xpath)
            
            cancel_list = []
            for elem in elems:
                xpath = "./td[contains(@class,'x-grid-cell-last')]"
                tmp_elems = elem.find_elements_by_xpath(xpath)
                xpath = "./div[@class='x-grid-cell-inner']"
                tmp_elems = tmp_elems[0].find_elements_by_xpath(xpath)
                xpath = "./div[@class='top']"
                tmp_elems = tmp_elems[0].find_elements_by_xpath(xpath)
                element = tmp_elems[0].find_element_by_link_text("Cancel")
                cancel_list.append(element)
        except Exception, e:
            return []
        return cancel_list


    def cancleAllOrganization(self, reason):
        """
        cancle all organization
        @reason: the reason to be cancelled 
        @@return value: True for success, False for otherwise
        """
        self.logger.info("STEP: remove all organizations")
        result = True
        try:
            result = self.showOrganizationList()
            if not result:
                return result
            time.sleep(5)
            elems = self.__getCancleNums__()            
            self.logger.debug("%d number of cancels detected", len(elems))
            elems_len = len(elems)
            while elems_len > 0:
                elem = elems[-1]
                self.logger.debug("Step: cancel an organization ")
                elem.click()
                
                self.logger.debug("Step: verify cancellation need to be confirmed")
                xpath = "//span[text()='Confirm cancellation']"
                cancel_elem = WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                cancel_elem.click()
                
                self.logger.debug("Step: select reason to cancel organization")
                xpath = "//label[contains(text(), '"+reason+"')]"
                radio_elem = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                radio_elem.click()
                time.sleep(2)
                
                self.logger.debug("Step: input reason")
                xpath = "//span[text()='Send feedback'][@class='x-btn-inner x-btn-inner-center']"
                send_btn = self.driver.find_element_by_xpath(xpath)
                send_btn.click()
                time.sleep(2)
                 
                self.logger.debug("Step: verify that organization is deleted")
                #WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.LINK_TEXT, "Cancel")))
                elems = self.__getCancleNums__()
                elems_after = len(elems)
                if(elems_after >= elems_len):
                    self.logger.error("Failed to remove organization successfully")
                    result = False
                elems_len = elems_after
                
        except Exception, e:
            self.logger.warning("Failed on removing organization with exception: %s", traceback.format_exc())
        return result 
   
