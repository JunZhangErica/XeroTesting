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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException as NoSuchElementException

import time
import traceback

# import local libs
from lib.TestObject import TestObject
from lib.OrganizationOps import OrganizationOps
from utils.GeneralUtils import *

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")

class TestBankAccountOps(TestObject):  
    MAX_NAME_LEN = 30
    MAX_NUM_LEN = 20
    
    def __init__(self, logger, configObj):
        super(TestBankAccountOps, self).__init__(logger, configObj)
        self.test_list = ['testAddBankAccountLocal', 'testAddBankAccountForeign','testAddBankAccountErrCurrency', 
                          'testAddBankAccountErrZone', 'testAddBankAccountUnGST', 'testAddBankAccountMultiOrg',
                          'testAddBankAccountSpecialNum', 'testAddBankAccountSpecialName', 'testAddBankAccountLongNum',
                          'testAddBankAccountLongName', 'testAddMultiBankAccounts', 'testAddMultiAccountsSameName', 
                          'testAddMultiAccountsSameNum',]
                           
        self.org_dict = {}
        self.account_dict = {}
        self.orgObj = OrganizationOps(self.driver, self.logger, self.configObj)
        self.org_dicts = []

        self.is_foreign = False
        self.err_currency = False
        
    def setup(self):
        result = super(TestBankAccountOps, self).setup()
        self.org_dict = super(TestBankAccountOps, self).getVariable('org_dict')
        self.account_dict = super(TestBankAccountOps, self).getVariable('account_dict')
        self.variables = super(TestBankAccountOps, self).getVariable('variables')
        return result
           
    def cleanup(self):
        self.orgObj.setDriver(self.driver)
        self.orgObj.cancleAllOrganization("Added by mistake")
    
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
               len(elem_val) > max_len:
                exceeded = True 
                break
            
        if not exceeded:
            self.logger.error(" Account %s not shows up as expected", elem_val)
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
        dup_name = not checkDictsUnique(data_dicts, 'accountname')
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
            try:
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
            except Exception, e:
                self.logger.warning("Account details are not expected with exception: %s", 
                              traceback.format_exc())
                return self.is_foreign
            
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
            
            xpath = "//input[contains(@id,'accountname')]"
            name_elems = self.driver.find_elements_by_xpath(xpath)
            num_xpath = "//input[contains(@id,'accountnumber')]"
            num_elems = self.driver.find_elements_by_xpath(num_xpath)
            
            self.logger.info("STEP: select type at first")
            index = 0
            
            while index < account_input_len:
                account_type = getValueforDict(data_dicts[index], 'accounttype') 
                self.logger.debug("input account type %s", account_type)
                id = type_elems[index].get_attribute('id')
                self.driver = setReadOnlyElemVal(self.driver, id, account_type)
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
                type_elems[index].send_keys(Keys.TAB + (unicode(number).encode('utf-8')))
                time.sleep(5)
                
                #num_elems[index].send_keys(number)
                time.sleep(2)
                index = index + 1
                            
            self.logger.debug("Step: post request of adding bank account")
            xpath = "//span[contains(@id,'common-button-submit')]"
            self.driver.find_element_by_xpath(xpath).click()
            
            try:
                xpath = "//span[@data-automationid='Add Bank Account-button']"
                WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                for data_dict in data_dicts:
                    self.logger.info("STEP: verify bank account to be added properly")
                    account_name = getValueforDict(data_dict, 'accountname')
                    account_type = getValueforDict(data_dict, 'accounttype')
                    number = getValueforDict(data_dict, 'accountnumber')
                    if "Credit" in account_type:
                        TestBankAccountOps.MAX_NUM_LEN = 4
                    else:
                        TestBankAccountOps.MAX_NUM_LEN = 20
                    result = result and self.checkBankAccount(account_name, number)            
                self.orgObj.setDriver(self.driver)
                if dup_name:
                    result = False
                    self.logger.error("DUPLICATED NAMES SHOULD NOT BE PERMITTED!!!")
            except Exception, e:
                if dup_name:
                    self.logger.debug("Account is not added successfully: %s", 
                              traceback.format_exc())
                else:
                    self.logger.error("Account details are not expected with exception: %s", 
                              traceback.format_exc())
                    result = False
                    
        except Exception, e:
            self.logger.error("Failed to add accounts with exception: %s", 
                              traceback.format_exc())
            result = False
        return result
    
    
    def customizeDict(self, val_dict):
        """
        customize account info into dicts
        @account_dict: each item can be splitted by ","
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
        @@return True for success; False for otherwise
        """
        result = True
        try:
            
            self.logger.info("STEP: create organizations")
            self.org_dicts = self.customizeDict(self.org_dict)
   
            self.logger.debug("will create %d organizations", len(self.org_dicts))
            for org_dict in self.org_dicts:
                self.orgObj.setDriver(self.driver)
                self.orgObj.addOrganization(org_dict, 
                                                      ["countryCmb", 
                                                       "cmbTimeZone", 
                                                       "currencyCmb"])
                        
            self.logger.info("STEP: add bank account")
            data_dicts = self.customizeDict(self.account_dict)
            self.logger.debug("data_dicts len = %d", len(data_dicts))
            
            for org_dict in self.org_dicts:
                for key in org_dict.keys():
                    self.logger.debug("key=%s, value=%s", key, org_dict[key])
                name = getValueforDict(org_dict, 'OrganisationName')
                self.logger.debug("org_dicts len = %d, name=%s", len(self.org_dicts), name)
                result = result and self.addBankAccount(name, data_dicts)

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
    
    def testAddBankAccountLocal(self):
        """
        Add bank account for local organization.
        For this user story, set location to be new zealand.
        @@ return: True for success and False for otherwise.
        """
        self.is_foreign = False
        return self.baseTestAddBankAccount()           

    def testAddBankAccountForeign(self):
        """
        Add bank account for foreign organization.
        For this user story, set location to be a country other 
        than new zealand, e.g. China.
        @@ return: True for failure as expected and False for otherwise,
                   since should not find ANZ(NZ) in that country.
        """
        self.is_foreign = True
        return self.baseTestAddBankAccount()    

    def testAddBankAccountErrCurrency(self):
        """
        Add bank account for organization with currency set to be non-official one.
        For this user story, set location to be China and set currency to be Bitcoin.
        @@ return: True for failure as expected and False for otherwise.
        This SHOULD BE decided in addBankAccount API.
        NOTES: currently, still not sure what should happen for this scenario
        but official web site just report internal server 500 error about it, which 
        should be not valid. So no checking operations done to decide the specific result
        for it.
        """
        self.err_currency = True
        if self.variables != None:
            if self.variables['is_foreign'] == '1':
                self.is_foreign = True
        return self.baseTestAddBankAccount()    

    def testAddBankAccountErrZone(self):
        """
        Add bank account for organization with time zone set to be error one.
        For this user story, set location to be New Zealand and set time zone to be Beijing.
        @@ return: True for success and False for otherwise.
        """
        return self.baseTestAddBankAccount()    
    
    def testAddBankAccountUnGST(self):
        """
        Add bank account for organization with GST disabled.
        @@ return: True for success and False for otherwise.
        """
        self.orgObj.setGST(0)
        return self.baseTestAddBankAccount()  


    def testAddBankAccountMultiOrg(self):
        """
        Add bank account for local organizations.
        @@ return: True for success and False for otherwise.
        """
        return self.baseTestAddBankAccount()          


    def testAddBankAccountSpecialNum(self):
        """
        Add bank account with number in special characters.
        @@ return: True for failure and False for otherwise.
        since the account number should be combination of 0-9,a-z,A-Z,*
        This is decided in addBankAccount API
        """
        return not self.baseTestAddBankAccount()  


    def testAddBankAccountSpecialName(self):
        """
        Add bank account with name in special characters.
        @@ return: True for success and False for otherwise.
        """
        return self.baseTestAddBankAccount() 

   
    def testAddBankAccountLongNum(self):   
        """
        Add bank account with number longer than 20.
        Number longer than 20 should be truncated to 20.
        @@ return: True for success and False for otherwise.
        """
        return self.baseTestAddBankAccount()
    

    def testAddBankAccountLongName(self):
        """
        Add bank account with name longer than 30.
        Name longer than 30 should be truncated wot 30.
        @@ return: True for success and False for otherwise.
        """   
        return self.baseTestAddBankAccount()

                
    def testAddMultiBankAccounts(self):  
        """
        Add multiple valid different bank accounts.
        @@ return: True for success and False for otherwise.
        """   
        return self.baseTestAddBankAccount()
    

    def testAddMultiAccountsSameName(self): 
        """
        Add multiple valid different bank accounts with same names.
        @@ return: True for failure as expected and False for otherwise.
                   This is decided in addBankAccount API
        """   
        return self.baseTestAddBankAccount()


    def testAddMultiAccountsSameNum(self): 
        """
        Add multiple valid different bank accounts with same numbers.
        @@ return: True for success and False for otherwise.
        NOTE: I THINK WE SHOULD NOT DUP NUMBERs FOR SAME USER.
        """   
        return self.baseTestAddBankAccount()
    
        
