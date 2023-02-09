'''
    Run this script to get the latest notebook from collab
    
    Example Usecases:
        -> Just onboarded to project
        -> Ran a long GPU intensive job on collab and would like to get latest version of notebook with outputs
'''
import argparse
import logging
import logging.handlers
import os
from google_drive import GoogleDriver, init_logger


def get_file_from_drive(collab_notebook_name: str, save_path: str):
    logger = init_logger("download_job.out")
    gd = GoogleDriver()
    gd.download_file(collab_notebook_name, save_path, logger)

#1) Add arg parse
#2): Add logging
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--collab_notebook_name', required=True,
                        help='Name of the notebook in drive to download')
    
    parser.add_argument('--save_path', required=True,
                        help='Path to save file to')



    args = parser.parse_args()
    get_file_from_drive(args.collab_notebook_name, args.save_path)
    
