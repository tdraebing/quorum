from os import listdir                                                          
from os.path import isfile, join 
from azure.datalake.store import core, lib, multithread

def get_adl_client(store_name, client_id=None, client_secret=None, tenant_id=None):
    try:
        from quorum.config.config import AZURE_DATA_LAKE
        token = lib.auth(client_id=AZURE_DATA_LAKE["ADL_CLIENT_ID"],
                         client_secret=AZURE_DATA_LAKE["ADL_CLIENT_SECRET"],
                         tenant_id=AZURE_DATA_LAKE["TENANT_ID"])
    except:
        raise Exception('Pass client_id, client_secret, and tenant_id or define in config.py')
    
    return core.AzureDLFileSystem(token, store_name=store_name)


def put_dir(client, local_dir_path, destination_dir):                           
    files = [f for f in listdir(local_dir_path) if isfile(join(local_dir_path, f))]
    files = [f for f in files if 'log_file.txt' not in f and 'checkpoints_file.txt' not in f]

    for f in files:                                                             
        client.put(join(local_dir_path, f), join(destination_dir, f))
