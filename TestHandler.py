#coding=utf-8

# import official libs
from optparse import OptionParser
import logging
import sys
import types
import os
import imp
import inspect
import traceback

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

# import local libs
from tests import *
from utils.HtmlTestRunner import *
from lib.ToolConfig import *

reload(sys) 
sys.setdefaultencoding("utf-8")

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-l", "--log_path", dest="log_path", default="xero_testreport.html",
                      help="The logger file full path")
    parser.add_option("-c", "--conf_path", dest="conf_path", default="config/Xero_Auto_Test.txt",
                      help="The config file full path")
                      
    (options, args) = parser.parse_args()

    # create logger for whole tool
    dir_path = os.path.dirname(os.path.realpath(__file__))
    log_name = options.log_path
    log_name = dir_path + "/" + log_name
        
    fmt = '[%(asctime)s] [%(levelname)s] [ %(filename)s:%(lineno)s - %(name)s ] %(message)s '
    
    buff_logger = BufferLogger(fmt, logging.DEBUG)
    buff_logger.startCapture()
    logger = buff_logger.getLogger()
    
    # parse all configuration info
    conf_path = options.conf_path
    conf_path = dir_path + "/" + conf_path
        
    configObj = ToolConfig(logger, conf_path)
    configObj.initConfVals()
    
    
    # detect all files under a path
    total_num = 0
    fail_num = 0
    pass_num = 0
    
    # initialize test classes results
    result_dicts = {}
    
    # singleton driver object
    driver = None
    
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for filename in os.listdir(dir_path+"/tests/"):
        # Each test class would be in only one test file, whose name should be started with "Test..."
        if "Test" in filename and ".py" in filename and ".pyc" not in filename :
            mod_name = filename.split(".")[0]
            # dynamically load all test files under tests/
            module = imp.load_source(mod_name, dir_path + "/tests/"+filename)
            # inspect all modules one by one to get test class
            try: 
                for name, testclass in inspect.getmembers(module):
                    if inspect.isclass(testclass) and mod_name in str(testclass):
                       # initialize the result for test class
                       test_case_dicts = {}
                           
                       #initialize each test class
                       testobj = testclass(logger, configObj)
                       testobj.setDriver(driver)
                       testlist = testobj.getTestList()
                       if len(testlist) == 0:
                           testlist = dir(testclass)
                                             
                       for api in testlist:
                       
                           # each test should be implemented in a single API, whose name starts with "test..."
                           api_name = None
                           if isinstance(testclass.__dict__.get(api), types.FunctionType):
                               api_name = testclass.__dict__.get(api).__name__
                           if api_name and 'test' in api_name:
                               # initialize test case result
                               test_case_result = 0
                               total_num = total_num + 1
                               logger.info("================================================================")
                               try:
                                   logger.info("Begin to run test: %s - %s", mod_name, api_name)
                                   # parse config file
                                   test_conf_path = os.getcwd() + "/config/" + mod_name + ".txt"
                                   logger.info("STEP: parse configure file: %s", test_conf_path)
                                   if not testobj.parseConf(test_conf_path, api_name):
                                       raise Exception("Failed to parse configure file: "+test_conf_path)
                                           
                                   logger.info("STEP: do setup ")
                                   if not testobj.setup():
                                       raise Exception("Failed to run test: " + mod_name +" - " +api_name+" on setup")
                                       
                                   logger.info("STEP: run test")
                                   if not getattr(testobj, api_name)():
                                       raise Exception("Failed to run test: " + mod_name +" - " +api_name+" on running")
                                       
                                   logger.info("Succeed to run test: %s - %s", mod_name, api_name)
                               except Exception, e:
                                   logger.debug("Failed to run test with exception: %s", traceback.format_exc())
                                   testobj.cleanup()
                                   
                                   test_case_result = 1
                                   fail_num = fail_num + 1
                                   logger.error("Failed to run test: %s - %s", mod_name, api_name)
                                       
                               logger.info("================================================================")
                                   
                               # collect test case result
                               test_info = buff_logger.getBufferVal()
                               test_case_result_list = [test_case_result, test_info]
                               buff_logger.stopCapture()
                               test_case_dicts[api_name] = test_case_result_list

                       
                       # collect test class results
                       result_dicts[mod_name] = test_case_dicts
                       
                       testobj.cleanup()
                       
                       # get driver object and pass it to next test group
                       driver = testobj.getDriver()
                           
            except Exception, e:
                logger.error("Failed with exception %s", traceback.format_exc())
    
    if driver != None:
        driver.quit()
        time.sleep(5)
                       
    pass_num = total_num - fail_num          
    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # generate HTML report
    report_writter = HtmlTestRunner(log_name, title="Xero Test Report")
    report_writter.generateReport(total_num, pass_num, fail_num, result_dicts = result_dicts)
    
    # logger clean up
    report_writter.cleanup()
    buff_logger.cleanup()
    
        
if __name__ == "__main__":
    main()
    
    
    
                
