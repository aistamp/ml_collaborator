'''
    This script updates the collab notebook with the latest revision
    
    This will run when the latest changes are pushed to github
    In the event that github actions (for automatic deployment)
    aren't working, manually running this script after pushing will help

    Two modes
    use_single_file
        Ex: python3 download_file.py --single_file --collab_notebook_name "Test Book" --save_path "test_notebooks/heyo"

    multi_file: read from a json config file a list of all notebooks to update
        Ex: python3 download_file.py --notebook_config collab_config.json
'''

import os
import json
import argparse

from google_drive import GoogleDriver, init_logger


def push_file_to_drive(file_path: str, collab_notebook_name: str):
    logger = init_logger("run_job.out")
    gd = GoogleDriver()
    gd.upload_file(file_path, collab_notebook_name, logger)

def push_multi_files_to_drive(collab_json_file: str):
    logger = init_logger("run_job.out")
    gd = GoogleDriver()
    
    with open(collab_json_file) as json_file:
        item_list = json.load(json_file)
        for item in item_list:
            collab_notebook_name = item["collab_notebook_name"]
            file_path = item["file_path"]
            gd.upload_file(file_path, collab_notebook_name, logger)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload/update one or multiple collab files from local files here.')
    parser.add_argument('--use_single_file', action="store_true",
                        help='Name of the notebook in drive to download')

    parser.add_argument('--collab_notebook_name',
                        help='Name of the notebook in drive to download')
    
    parser.add_argument('--save_path',
                        help='Path to save file to')
    
    parser.add_argument('--notebook_config',
                        help='Path to save file to')


    args = parser.parse_args()
    
    if args.use_single_file:
        if not (args.collab_notebook_name and args.save_path):
            print("ERROR, collab_notebook_name and save_path not set")
            exit()
        push_file_to_drive(args.save_path, args.collab_notebook_name)
    else:
        if not args.notebook_config:
            print("ERROR, notebook_config not specified")
            exit()
        push_multi_files_to_drive(args.notebook_config)
