'''
    This script updates the collab notebook with the latest revision
    
    This will run when the latest changes are pushed to github
    In the event that github actions (for automatic deployment)
    aren't working, manually running this script after pushing will help
'''

import os
from google_drive import GoogleDriver, init_logger


def push_file_to_drive(file_path: str, collab_notebook_name: str):
    logger = init_logger("run_job.out")
    gd = GoogleDriver()
    gd.upload_file(file_path, collab_notebook_name, logger)

#TODO: 
# 1) Add os env vars
# 2) Connect to github actions
if __name__ == '__main__':
    file_path = os.environ["UPLOAD_FILE_PATH"]
    collab_notebook_name = os.environ["COLLAB_NOTEBOOK_NAME"]
    push_file_to_drive(file_path, collab_notebook_name)
