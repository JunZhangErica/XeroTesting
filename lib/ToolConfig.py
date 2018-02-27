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

from utils.GeneralUtils import ConfigParserUtil

import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")



class ToolConfig(object):

    def __init__(self, logger, config_path):
        self.logger = logger
        self.config_path = config_path
        self.chrome_info = {}
        self.login_info = {}  


    def initConfVals(self):
        cf = ConfigParserUtil()
        cf.read(self.config_path)

        self.chrome_info['path'] = cf.get('chrome_conf', 'path')
        self.logger.debug("chrome installation path = %s", self.chrome_info['path'])

        self.login_info['user'] = cf.get('xero_web', 'login_user')
        self.login_info['pwd'] = cf.get('xero_web', 'login_pwd')
        self.login_info['url'] = cf.get('xero_web', 'login_url')



    def getChromeInfo(self):
        return self.chrome_info

    def getLoginInfo(self):
        return self.login_info


