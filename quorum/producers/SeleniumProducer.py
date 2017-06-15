import os
from xvfbwrapper import Xvfb
from selenium import webdriver 


class SeleniumProducers(object):

    def __init__(self, virtuald=None, driver=''):
        if isinstance(virtuald, bool):
            self.virtuald = virtuald
        else:
            raise TypeError('Virtual display option invalid')
        if isinstance(driver, str):
            self.driver_opt = driver.lower()
        else:
            raise ValueError('Specify wbdriver as a string')


    def start_driver(self):
        if self.virtuald:                                                       
            self.vdisplay = Xvfb()                                             
            self.vdisplay.start()  

        if self.driver_opt=='firefox':
            self.driver = webdriver.Firefox()
        elif self.driver_opt=='chrome':
            self.driver = webdriver.Chrome()
        else:
            raise NotImplementedError()


    def terminate_driver(self):                                                
        self.driver.quit()
        if self.virtuald:
            self.vdisplay.stop()                                               


    def restart_crawl(self, checkpoint_filename):
        checkpoints = []
        if not os.path.isfile(checkpoint_filename):
            checkpoint_file = open(checkpoint_filename, 'w')
        else:
            checkpoint_file = open(checkpoint_filename, 'r+')
            checkpoints = checkpoint_file.readlines()
            checkpoints = [check.strip('\n') for check in checkpoints
                           if check.strip('\n')!='']
        return checkpoint_file, checkpoints
