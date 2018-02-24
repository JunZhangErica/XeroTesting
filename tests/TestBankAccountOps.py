#coding=utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException as NoSuchElementException

import time
import traceback

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")

# import local libs
from lib.TestObject import TestObject
from lib.OrganizationOps import OrganizationOps
from utils.GeneralUtils import *

class TestBankAccountOps(TestObject):    
    ORG_CUSTOMIZED = False
    MAX_NAME_LEN = 30
    MAX_NUM_LEN = 20
    ORG_ORDER = 0
    
    def __init__(self, logger, configObj):
        super(TestBankAccountOps, self).__init__(logger, configObj)
        self.test_list = [ 'testAddBankAccountBasic' ]
                          #'testAddBankAccountUnicodeNum', 'testAddBankAccountUnicodeName', 
                          #'testAddBankAccountLongNum', 'testAddBankAccountLongName', 'testAddMultiBankAccounts',
                          #'testAddMultiSameBankAccount']
        self.org_dict = {}
        self.account_dict = {}
        self.orgObj = OrganizationOps(self.driver, self.logger, self.configObj)
        self.org_dicts = []
        
    def setup(self):
        result = super(TestBankAccountOps, self).setup()
        self.org_dict = super(TestBankAccountOps, self).getVariable('org_dict')
        self.account_dict = super(TestBankAccountOps, self).getVariable('account_dict')
        return result
           
    def cleanup(self):
        self.orgObj.setDriver(self.driver)
        self.orgObj.cancleAllOrganization("Other")
    
    def showBankAccounts(self):
        """
        show all bank accounts for current organization
        @@return value: True for success. False for otherwise
        """
        self.logger.info("STEP: show bank accounts")
        result = True
        try:
            self.logger.debug("Step: expand Accounts menu")
            xpath = "//a[@id = 'Accounts']"
            self.driver.find_element_by_xpath(xpath).click()
            
            self.logger.debug("Step: select Bank Accounts menu")
            locator = (By.LINK_TEXT, "Bank Accounts")
            account_link = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(locator))
            account_link.click()
            
            self.logger.debug("Step: verify Bank Accounts window shows up")
            xpath = "//span[text() = 'Add Bank Account']"
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        except Exception, e:
            self.logger.error("Failed on show bank accounts with exception %s ", 
                              traceback.format_exc())
            result = False
        return result
    
    def __checkStrExceedLength__(self, xpath, elem_val, max_len ):
        """
        check string exceed defined length
        @xpath: xpath for checked element
        @elem_val: element text value
        @max_len: account name or card number max length
        @@return value: True for success. False for otherwise
        """
        result = True
        exceeded = False
        elems = self.driver.find_elements_by_xpath(xpath)
        for elem in elems :
            if elem.text in elem_val and \
               strlen(elem.text) > max_len:
                exceeded = True 
                break
            
        if not exceeded:
            self.logger.error(" Account %s not shows up as expected", name)
            result = False
        return result                    
        
    def checkBankAccount(self, name, num, 
                         logo_path="edge.xero.com/banking/logos/anz_small.png"):
        """
        By default is to check the account name, card number
        and logo to be as expected
        @name : account name
        @num : card number
        @logo_path: path for bank logo
        @@return value: True for success. False for otherwise
        """
        result = True
        
        try:
            self.logger.info("STEP: check bank account details")
            self.logger.debug("Step: verify account name")
            xpath = "//a[contains(@href, '/Bank/BankTransactions.aspx')]"
            name_elem = None
            try:
                name_xpath = xpath + "[contains(text(), '"+name+"')]"
                name_elem = self.driver.find_element_by_xpath(name_xpath)
            except NoSuchElementException:
                self.logger.debug("Step: check account name length truncated") 
                result = self.__checkStrExceedLength__(xpath, 
                                                       name, TestBankAccountOps.MAX_NAME_LEN )
            
            self.logger.debug("Step: verify card number")
            exceeded = False 
            xpath += "/span"
            try:
                self.driver.find_element_by_xpath(xpath + "[text()='"+num+"']")
            except NoSuchElementException:
                self.logger.debug("Step: check card number is unicode and report error")     
                if result and not isinstance(num, str):
                    error_msg = "The account " + name +" should not be added successfully but successfully.\n"
                    error_msg = "Maybe because the card number value is unicode."
                    self.logger.error(error_msg)
                    result = False
                
                self.logger.debug("Step: check card number length truncated")
                result = self.__checkStrExceedLength__(xpath, 
                                                       num, TestBankAccountOps.MAX_NUM_LEN )    
                        
            if logo_path != None and logo_path != "":
                self.logger.debug("Step: verify logo path")
                xpath = "//span[@id='acct_'][img[contains(@src, logo_path)]]"
                self.driver.find_element_by_xpath(xpath)
        except Exception, e:
            self.logger.error("Account details are not expected with exception: %s", 
                              traceback.format_exc())
            result = False
        return result

    def addBankAccount(self, org_name, data_dicts):
        """
        add bank account for the specified organization
        @org_name: organization name
        @data_dicts: account data info dictionaries
        @@return value: True for success. False for otherwise 
        """
        self.logger.info("STEP: add bank account for organization %s", org_name)
        result = True
        try:
            #show dashboard for organization
            self.orgObj.setDriver(self.driver)
            self.orgObj.checkOrganization(org_name)
            
            #show bank account for organization
            self.showBankAccounts()
            
            self.logger.info("STEP: search for bank name")
            xpath = "//span[text() = 'Add Bank Account']"
            self.driver.find_element_by_xpath(xpath).click()
            time.sleep(10)
            
            xpath = "//div[@data-automationid='bankSearch']"
            element = self.driver.find_element_by_xpath(xpath)
            for i in [1,2,3]:
                xpath = "./div[contains(@id,'xui-searchfield')]"
                elems = element.find_elements_by_xpath(xpath)
                element = elems[0]
            
            xpath = "./input"
            elems = element.find_elements_by_xpath(xpath)
            search_elem = elems[0]
                        
            bank_name = getValueforDict(data_dicts[0],"xui-searchfield")                           
            search_elem.send_keys(bank_name)
            time.sleep(5)
            search_elem.send_keys(u'\ue007')
            time.sleep(5)
            
            self.logger.info("STEP: input correct bank name")
            xpath = "//div[@class='x-container xui-panel xui-container-small x-container-default']"
            element = self.driver.find_element_by_xpath(xpath)
            element = element.find_element_by_tag_name('section')
            xpath = "./div[@data-automationid='searchBanksList'][contains(@id,'ba-banklist')]"
            element = element.find_element_by_xpath(xpath)            
            
            xpath = "./ul[contains(@id,'dataview')]"
            element = element.find_element_by_xpath(xpath)
            xpath = "./li"
            elems = element.find_elements_by_xpath(xpath)
            element = elems[0]
            element.click()
            time.sleep(2)
            
            xpath = "//input[contains(@id,'accountname')]"
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            
            index = 1
            account_input_len = len(data_dicts)
            while index < account_input_len:
                self.logger.info("STEP: add another bank account")
                xpath = "//span[contains(text(), '+ Add another')]" 
                self.driver.find_element_by_xpath(xpath).click()
                time.sleep(2)
                index += 1
                
            self.logger.info("STEP: create %d number of accounts has been show up for input", 
                             account_input_len)
            
            xpath = "//input[contains(@id,'accounttype')]"
            type_elems = self.driver.find_elements_by_xpath(xpath)
            self.logger.debug("%d types input are detected", len(type_elems))
            if len(type_elems) != account_input_len:
                raise Exception("Failed to add another bank account")
            
            self.logger.info("STEP: select type at first")
            index = 0
            while index < account_input_len:
                account_type = getValueforDict(data_dicts[index], 'accounttype') 
                self.logger.debug("input account type %s", account_type)
                id = type_elems[index].get_attribute('id')
                self.driver = setReadOnlyElemVal(self.driver, id, account_type)
                type_elems = self.driver.find_elements_by_xpath(xpath)
                #type_elems[index].send_keys(account_type)
                time.sleep(5)
                index += 1
            
            xpath = "//input[contains(@id,'accountname')]"
            name_elems = self.driver.find_elements_by_xpath(xpath)
            num_xpath = "//input[contains(@id,'accountnumber')]"
            num_elems = self.driver.find_elements_by_xpath(num_xpath)
            self.logger.debug("Step: input account name and num")
            index = 0
            while index < account_input_len:
                account_name = getValueforDict(data_dicts[index], 'accountname')
                self.logger.debug("input account name %s", account_name)
                name_elems[index].send_keys(account_name)
                time.sleep(2)
                
                number = getValueforDict(data_dicts[index], 'accountnumber')
                id = num_elems[index].get_attribute('id')
                
                class_attr = "xui-input x-form-required-field x-form-text x-form-text-default"
                self.driver = enElemVisible(self.driver, id, number, 'class', class_attr)
                num_elems = self.driver.find_elements_by_xpath(num_xpath)
                #num_elems[index].send_keys(number) 
                time.sleep(2)
                index = index + 1
                            
            self.logger.debug("Step: post request of adding bank account")
            xpath = "//span[contains(@id,'common-button-submit')]"
            self.driver.click()
            
            xpath = "//span[@data-automationid='Add Bank Account-button']"
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.PATH, xpath)))
            for data_dict in data_dicts:
                self.logger.info("STEP: verify bank account to be added properly")
                account_name = getValueforDict(data_dicts[index], 'accountname')
                account_type = getValueforDict(data_dicts[index], 'accounttype')
                number = getValueforDict(data_dicts[index], 'accountnumber')
                if "Credit" in account_type:
                    TestBankAccountOps.MAX_NUM_LEN = 4
                else:
                    TestBankAccountOps.MAX_NUM_LEN = 20
                result = result & self.checkBankAccount(account_name, number)
                
        except Exception, e:
            self.logger.error("Failed to add accounts with exception: %s", 
                              traceback.format_exc())
            result = False
        return result
    
    
    def customizeDict(self, val_dict):
        """
        customize account info into dicts
        @account_dict：each item can be splitted by ","
        @@return data_dicts
        """
        to_be_customized = 0
        data_dicts = []
        keys = val_dict.keys()
        for key in keys:
            key_num = len(val_dict[key].split(","))
            if key_num > to_be_customized:
                to_be_customized = key_num
                        
        index = 0
        while index < to_be_customized-1:
            data_dict = {}
            for key in val_dict.keys():
                if "," in val_dict[key]:
                    vals = val_dict[key].split(",", 1)
                    data_dict[key] = vals[0]
                    val_dict[key] = vals[1]
                else:
                    data_dict[key] = val_dict[key]
            data_dicts.append(data_dict)
            index = index + 1
            
        data_dicts.append(val_dict)
        return data_dicts
        
    def baseTestAddBankAccount(self):
        """
        basic test process of adding bank account
        @data_dicts：add bank accounts for all organizations
        @@return True for success; False for otherwise
        """
        result = True
        try:
            self.logger.info("STEP: create organizations")
            self.org_dicts = self.customizeDict(self.org_dict)
                
            if not TestBankAccountOps.ORG_CUSTOMIZED: 
                self.logger.debug("will create %d organizations", len(self.org_dicts))
                for org_dict in self.org_dicts:
                    self.orgObj.setDriver(self.driver)
                    result = result & self.orgObj.addOrganization(org_dict, 
                                                                  ["countryCmb", 
                                                                   "cmbTimeZone", 
                                                                   "currencyCmb"])
                TestBankAccountOps.ORG_CUSTOMIZED = True
                        
            self.logger.info("STEP: add bank account")
            data_dicts = self.customizeDict(self.account_dict)
            self.logger.debug("data_dicts len = %d", len(data_dicts))
            for org_dict in self.org_dicts:
                name = getValueforDict(org_dict, 'OrganisationName')
                result = result & self.addBankAccount(name, data_dicts)
            
        except Exception, e:
            self.logger.error("Failed on adding bank account with exception %s", traceback.format_exc())
            result = False
        return result    
    
    """
    What following test cover the product of following items: 
    1. Multiple different organizations: 
        NZ vs. Non-NZ, 
        currency not official one, 
        timezone not correct one, 
        different industries
    2. Different Accounts scenario:
        Basic proper one
        Different account type
        Unicode Card Number
        Unicode Name
        Long Card Number
        Long Name
        Multi Bank Account
        Same Bank Accounts
    What they not cover:
        cancel operations
        ...
    Reason for limited coverage:
        time limitation
    """            
    
    def testAddBankAccountBasic(self):
        return self.baseTestAddBankAccount()            
    
    def testAddBankAccountUnicodeNum(self): 
        return (not self.baseTestAddBankAccount())
        
    def testAddBankAccountUnicodeName(self):  
        return self.baseTestAddBankAccount()
    
    def testAddBankAccountLongNum(self):   
        return self.baseTestAddBankAccount(data_dicts)
    
    def testAddBankAccountLongName(self):   
        return self.baseTestAddBankAccount()
                
    def testAddMultiBankAccounts(self):  
        return self.baseTestAddBankAccount()
    
    def testAddMultiSameBankAccount(self):  
        return self.baseTestAddBankAccount()
    
        
