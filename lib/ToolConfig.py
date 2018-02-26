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


