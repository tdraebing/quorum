from itertools import repeat
from multiprocessing import freeze_support, Pool, cpu_count 
from quorum.consumers.ddwConsumer import DataDotWorldOD


def ckan_pipeline(source, crawling_args):
    print('Scraping {}'.format(source))
    crawler = CkanCrawler(source, **crawling_args)
    crawler.get_datasets()


def ddw_pipeline(source, crawling_args):
    print('Scraping {}'.format(source))
    crawler = DataDotWorldOD(**crawling_args)
    crawler.start_driver()
    crawler.parse_catalog(source)
    crawler.terminate_driver()


def run_pipeline(num_procs, pipeline, sources, crawling_args):
    freeze_support()
    pool = Pool(1)
    pool.starmap(pipeline, zip(sources, repeat(crawling_args)))
    pool.close()
    pool.join() 


crawling_args = {
    "interval": 50,
    "offset": 0,
    "max_datasets": -1,
    "data_dir": 'data',
    "remote_dir": 'data',
    "formats": ['XLSX','XLS','CSV'],
    "virtuald": False,
    "adl": True,
    "data_lake": 'nktraining',
    "excel2csv": True,                                             
}

ddw = DataDotWorldOD(**crawling_args)                                   
ddw.grab_opendata_catalogs()                                            
ddw.terminate_driver()

for source in ddw.catalogs:
    ddw_pipeline(source, crawling_args)
