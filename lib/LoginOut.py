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

import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")

class LoginOut(object):
    """
    class to provide API login/logout collect functions 
    NOTE: Because of limited time, only the APIs to be used by 
    TestBankAccountOps will be provided.
    """
    HAS_LOGGEDIN = False
    def __init__(self, driver, logger, configObj):
        self.driver = driver
        self.logger = logger
        self.configObj = configObj
        
    def openLoginWin(self):
        """
        open login dialog window by click Login link
        @@return value: True for successful, Otherwise Fail
        """
        result = True
        try:
            self.logger.info("STEP: click to open login window")
            xpath = "//a[contains(@href, 'login.xero.com')]"
            login_link = self.driver.find_element_by_xpath(xpath)
            login_link.click()
            
            self.logger.debug("Step: check window is loaded as expected")
            xpath = "//button[@type='submit'][contains(text(),Login)]"
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
        except Exception, e:
            self.logger.error("Failed on login with exception: %s", traceback.format_exc())
            result = False
        return result 
    
    def hasLogin(self):
        """
        Check if has logged in or not
        @@ return True for already logged in 
        """
        return LoginOut.HAS_LOGGEDIN

    def login(self, login_type = 1):
        """
        Log into xero official website
        @login_type: 1 for correct;
                     2 for wrong user name or wrong password;
                     3 not activated user name
                     4 account locked
        @@ result: True for sucess; driver: chromedriver object
        """
        result = True
        try:
            if self.hasLogin():
                self.logger.debug("Step: Already logged in and return.")
                return result

            if not self.openLoginWin():
                return False

            self.logger.info("STEP: do login")
            login_info = self.configObj.getLoginInfo()
            user = login_info['user']
            password = login_info['pwd']
            
            self.logger.info("Step: Login with %s:%s", user, password)
            # input login dialog and click login button
            self.driver.find_element_by_xpath("//input[@name='userName']").send_keys(user)
            self.driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
            self.driver.find_element_by_xpath("//button[@type='submit'][contains(text(), 'Login')]").click()
            
            # check expect result to match real-time result
            self.logger.info("STEP: check real-time result to be as expected")
            login_evidence = None
            if login_type == 1:
                self.logger.debug("Expected result: logged in Xero.com successfully!")
                try:
                    try:
                        xpath = "//div[contains(@class,'xui-page-title')][contains(text(),'Welcome to Xero')]"
                        WebDriverWait(self.driver, 40).until(
                            EC.visibility_of_element_located((By.XPATH, xpath)))
                    except Exception, e:
                        xpath = "//a[contains(text(), 'Add an organisation')]"
                        self.driver.find_element_by_xpath(xpath) 
                except Exception, e:
                    self.driver.find_element_by_link_text("Start Trial")
                LoginOut.HAS_LOGGEDIN = True
            else:
                xpath = "//div[@class='x-boxed warning']"
                if login_type == 2:
                    self.logger.debug("Expected result: message to report wrong user name or password shows up")
                    xpath += "/p[contains(text(), 'email or password is incorrect']"
                elif login_type == 3:
                    self.logger.debug("Expected result: messages, that the account should be activated, shows up")
                    xpath += "/p[contains(text(), 'Please activate your account']" 
                elif login_type == 4:
                    self.logger.debug("Expected result: messages, that account has already been locked, shows up") 
                    xpath += "/p[contains(text(), 'Your account has been temporarily locked']"  
                WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, xpath)))                                             
        except Exception, e:
            self.logger.error("Failed on login with exception: %s", traceback.format_exc())
            result = False
        return result 
                    
    def logout(self):
        """
        logout tvcms system
        @@ result: True for sucess; driver: chromedriver object
        """
        result = True
        self.logger.info("TEST_STEP: do logout")
        try:
            self.logger.info("Step: click account link to enable logout clickable")
            xpath = "//a[@class='username']"
            account_elem = self.driver.find_element_by_xpath(xpath)
            account_elem.click()
            xpath = "//a[contains(text(),'Logout')]"
            logout_elem = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            logout_elem.click()
            
            self.logger.info("Step: check if logged out successfully")
            xpath = "//button[@type='submit'][contains(text(),Login)]"
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            LoginOut.HAS_LOGGEDIN = False
        except Exception, e:
            self.logger.error("Failed on logout with exception %s ", traceback.format_exc())
            result = False
        return result  


   
