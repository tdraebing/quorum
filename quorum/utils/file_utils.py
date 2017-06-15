import os
from time import sleep
from sys import version_info
import xlrd                                                                     
import csv
from quorum.utils.azure_utils import get_adl_client, put_dir 


def safe_filename(name):
    safechar = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._'
    name = ''.join(c for c in name if c in safechar).rstrip()
    return name


def create_dir(urls=[], data_dir='data'):                                   
    if isinstance(urls, list):
        domain = []                                                             
        for url in urls:
            domain.append(url.split('/')[-1])                                   
        instance_dir = data_dir + '/' + '/'.join(domain)
    
        os.makedirs(instance_dir, exist_ok=True)
        return instance_dir


def ls_files(path):
    return (f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)))


def clean_up(path):                                                             
    for f in ls_files(path):
        if 'log_file.txt' not in f and 'checkpoints_file.txt' not in f:
            f = os.path.join(path, f)
            os.remove(f)


def excel_to_csv(exelFile, csvFile):
    with xlrd.open_workbook(exelFile) as wb:
        sh = wb.sheet_by_index(0)
        with open(csvFile,'w') if version_info[0]==3 else open(csvFile,'wb')as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            for row in range(sh.nrows):
                writer.writerow(sh.row_values(row))


def convert_excel2csv(path):
    for f in ls_files(path):
        f = os.path.join(path, f)
        filename, extension = '.'.join(f.split('.')[:-1]), f.split('.')[-1].upper()
        if 'XLSX' in extension or 'XLS' in extension:
            try:
                excel_to_csv(f, filename+'.csv')
            except Exception as e:
                print("Problem while converting excel to csv")                      
                print(e)                                                            
                pass
            os.remove(f)


def process_files(path, **kwargs):                                              
    local_dir   = path                                                          
    remote_dir  = kwargs["remote_dir"]+'/'+path.split('/')[-1]
                                                
    # Convert excel files to csv                                                
    if kwargs["excel2csv"] and os.path.exists(local_dir):                       
        convert_excel2csv(os.path.abspath(local_dir))

    # Store data in Azure data lake                                             
    if kwargs["adl"] and os.path.exists(local_dir):                            
        while True:
            try:
                adl = get_adl_client(kwargs["data_lake"])                               
                put_dir(adl, local_dir, remote_dir)                                     
                # delete all files except log and checkpoint files                      
                clean_up(local_dir)
                break
            except Exception as e:
                print('Error while storing files to Data lake -> process_files()')
                print(e)
                sleep(60*5)
                continue

