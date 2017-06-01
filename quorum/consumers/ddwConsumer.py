import os
from time import sleep
import requests
from bs4 import BeautifulSoup                                                   
from xvfbwrapper import Xvfb
from selenium import webdriver                                                  
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.options import Options
from ..utils.file_utils import create_dir, safe_filename, process_files
import traceback


class DataDotWorldOD(object):
    """ data.world Scraper

        Crawls through the opendata portal which contains multiple catalogs.
        Each catalog contains multiple datasets.

    """
    def __init__(self, url='https://data.world', max_datasets=-1, 
                 data_dir='data', portal='/opendata', virtuald=True, 
                 **kwargs):
        self.url                = url
        self.max_datasets       = max_datasets
        self.portal             = portal
        self.data_dir           = data_dir
        self.virtuald           = virtuald
        self.formats            = kwargs["formats"]
        self._kwargs            = kwargs


    def start_driver(self):
        if self.virtuald:
            self._vdisplay = Xvfb()                                                       
            self._vdisplay.start()
        self.driver = webdriver.Chrome()

    def terminate_driver(self):
        print('Crawling done {}'.format(self.url))
        if self.virtuald:
            self._vdisplay.stop()
        self.driver.quit()

    def get_opendata(self):
        self.start_driver()
        create_dir([self.url], self.data_dir)
        self.driver.get(self.url + self.portal)

    def grab_opendata_catalogs(self):
        self.get_opendata()
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        catalogs = soup.find_all('a',
                                 class_="DSICatalogsListView__catalogCard___30giA",
                                 href=True)
        self.catalogs = [self.url+x.attrs["href"] for x in catalogs]


    def _restart_crawl(self, checkpoint_filename):
        checkpoints = []
        if not os.path.isfile(checkpoint_filename):
            checkpoint_file = open(checkpoint_filename, 'w')
        else:
            checkpoint_file = open(checkpoint_filename, 'r+')
            checkpoints = checkpoint_file.readlines()
            checkpoints = [check.strip('\n') for check in checkpoints
                           if check.strip('\n')!='']

        return checkpoint_file, checkpoints


    def parse_catalog(self, catalog):
        self.driver.get(catalog)
        main_page = self.driver.current_url
        path = create_dir([self.url, catalog], self.data_dir)
        self.counter, page_num = 0, 0

        # lgo and checkpoint files
        log_file = open(path+'/log_file.txt', 'w')
        checkpoint_filename = path+'/checkpoints_file.txt'
        checkpoint_file, start = self._restart_crawl(checkpoint_filename)
        start = checkpoints[-1]

        while self.counter <= self.max_datasets or self.max_datasets<0:
            try:
                page_num += 1
                print('{}.\t{}'.format(page_num, catalog))
                
                self.driver.get(start)
                self._parse_catalog()

                # go to next page                                                   
                checkpoint_file.write('{}\n'.format(previous_page))
                self.driver.get(previous_page) 
                self.driver.find_element_by_xpath('//*[@aria-label="Next"]').click()   
                main_page = self.driver.current_url
            except WebDriverException as e:
                print(e)
                log_file.write('{}\n'.format(e))
                traceback.print_tb(e.__traceback__)
                break
            except TimeoutException:
                sleep(60)
                continue
            except Exception as e:
                print(e)
                log_file.write('{}\n'.format(e))
                traceback.print_tb(e.__traceback__)

        checkpoint_file.close()
        log_file.close()
        return path
   
    
    def _parse_catalog(self):
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        datasets = soup.find_all('a', class_="dw-dataset-name",href=True)
        datasets = [self.url+x.attrs["href"] for x in datasets] 
        for dataset in datasets:
            if self.counter <= self.max_datasets or self.max_datasets<0:
                self.driver.get(dataset) 
                sleep(1) 
                self._get_datasets()
                self._save_datasets(path, dataset_link, dataset_name.contents[0])
            else:
                break



    def _get_datasets(self):
        soup = BeautifulSoup(self.driver.page_source, "lxml")

        info = self._find_all_keyword(soup, 'a', "dw-dataset", href=True)
        author, dataset_name = info[0], info[1]
        #description = soup.find_all('span',class_="Markdown__content___3thyu")
        dataset_link = soup.find_all('a', target="_blank", href=True)
        dataset_link = [d for d in dataset_link 
                        if "data-reactid" not in d.attrs.keys()]

   
   def _save_datasets(self, path, links, dataset_name):
        for link in links:
            file_ext = (link.contents[0]).split('.')[-1]
            if file_ext.upper() in self.formats:
                r = requests.get(link.attrs["href"], stream=True)
                filename = dataset_name + '.' + file_ext
                filename = safe_filename(filename)
                with open(path+'/'+filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                self.counter += 1


    @staticmethod
    def _find_all_keyword(soup, tag, keyword, href=True):                                  
        elements = [                                                                
            x for x in soup.find_all(tag, href=href)                                
            if ("class" in x.attrs) and (keyword in str(x.attrs["class"]))          
        ]                                                                           
        return elements                                                             

if __name__=="__main__":
    crawler = DataDotWorldOD()
    crawler.grab_opendata_catalogs()
    for catalog in crawler.catalogs:
        instance_dir = crawler.parse_catalog(catalog)
    crawler.terminate_driver()
