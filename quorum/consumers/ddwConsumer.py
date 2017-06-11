import os
from time import sleep
import requests
import traceback
from bs4 import BeautifulSoup                                                   
from selenium.common.exceptions import WebDriverException, TimeoutException
from quorum.consumers.SeleniumConsumers import SeleniumConsumers
from quorum.utils.file_utils import create_dir, safe_filename, process_files


class DataDotWorldOD(SeleniumConsumers):
    """ data.world Scraper

        Crawls through the opendata portal which contains multiple catalogs.
        Each catalog contains multiple datasets.

    """
    def __init__(self, virtuald=True, driver='firefox', max_datasets=-1, 
                 data_dir='data', **kwargs):
        super().__init__(virtuald, driver)
        self.url                = 'https://data.world'
        self.portal             = '/opendata'
        self.max_datasets       = max_datasets
        self.data_dir           = data_dir
        self.virtuald           = virtuald
        self.formats            = kwargs["formats"]
        self._kwargs            = kwargs

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


    def parse_catalog(self, catalog):
        main_page = catalog
        path = create_dir([self.url, catalog], self.data_dir)
        self.counter, page_num = 0, 0

        # lgo and checkpoint files
        log_file = open(path+'/log_file.txt', 'w')
        checkpoint_filename = path+'/checkpoints_file.txt'
        checkpoint_file, checkpoints = self.restart_crawl(checkpoint_filename)
        if checkpoints:
            main_page = checkpoints[-1]

        while self.counter <= self.max_datasets or self.max_datasets<0:
            try:
                page_num += 1
                print('{}.\t{}'.format(page_num, catalog))
        
                self.driver.get(main_page)
                self._parse_catalog(path)
                
                process_files(path, **self._kwargs)

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
   
    
    def _parse_catalog(self, path):
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        datasets = soup.find_all('a', class_="dw-dataset-name",href=True)
        datasets = [self.url+x.attrs["href"] for x in datasets] 
        for dataset in datasets:
            if self.counter <= self.max_datasets or self.max_datasets<0:
                self.driver.get(dataset) 
                sleep(1) 
                dataset_link, dataset_name = self._get_datasets()
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
        return dataset_link, dataset_name

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
