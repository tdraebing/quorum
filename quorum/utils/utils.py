from argparse import ArgumentParser


def cl_options():                                                               
    parser = ArgumentParser()                                                   
                                                                                
    parser.add_argument('-a', '--adl',                                          
                        action='store_true',                                    
                        help='Store datasets in data lake')                     
                                                                                
    parser.add_argument('-dl', '--data_lake',                                   
                        type=str,                                               
                        default='nktraining',                                   
                        help='Name of data lake')                               
                                                                                
    parser.add_argument('-m', '--max_datasets',                                 
                        type=int,                                               
                        default=-1, 
                        help='Max number of datasets')                          
                                                                                
    parser.add_argument('-e', '--excel',                                        
                        action='store_true',                                    
                        help='Convert exel files to csv')                       
                                                                                
    parser.add_argument('-d', '--dir',                                          
                        default='data',                                         
                        help='Directory to store data on')

    parser.add_argument('-rd', '--remote_dir',
                        default='data',
                        help='Remote directory to store data on')
                                                                                
    parser.add_argument("-v", "--virtual",                                      
                        action='store_true',                                    
                        help="Use virtual display")                             
                                                                                
    parser.add_argument('--ckan',                                               
                        action='store_true',                                    
                        help='Crawl through ckan instances')                    
                                                                                
    parser.add_argument('--ddw',                                                
                        action='store_true',                                    
                        help='Crawl through data.world instances')              
    
    parser.add_argument('-p', '--processes',
                        type=int,
                        default=2,
                        help='Number of worker processes')

    return parser.parse_args()
