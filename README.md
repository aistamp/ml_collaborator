# ML Collaborator
Conviniently use Github with Google Collab

## Set up
#### 1) Either fork this repo or create a new one for this project, copying over the following files (preserving the path)
   - .github/workflows/actions.yml
   - download_file.py
   - google_drive.py
   - update_drive.py
   - requirements.txt
   - .gitignore  

#### 2) Get the Google drive credentials
    a)  Follow the steps in the documentation here under the "Enable the API"
        and "Authorize credentials for desktop application section"
        
        https://developers.google.com/drive/api/quickstart/python
        
        INSERT SCREEN SHOT OF DOC HERE

    b)  Make sure to enable the following scopes when creating the Google cloud project
        - https://www.googleapis.com/auth/drive
        - https://www.googleapis.com/auth/drive.file
        - https://www.googleapis.com/auth/drive.metadata

    c) At the end of this process you should have added a `credentials.json` file into 
       your wokring directory
       IMPORTANT: Do not add this file to github (incase you didn't use of modified your gitignore file)
    

#### 3) Set up Environment
    a) Create a new conda python 3.9 enviorment
        Conda installation instructions if not already installed: https://conda.io/projects/conda/en/latest/user-guide/install/index.html

        `conda create -n YOUR_ENV_NAME python=3.9`

        Then activate your environment by running: `conda activate YOUR_ENV_NAME`

    b) Install packages by running
        `pip install -r requirements.txt`

#### 4) Get the token.json file
   a) Run the *download script* or *upload script* (see below)
    
    The first time you run this script, because you don't have a token file,
    your browser will open a new tab and Google will ask you to allow the project
    you created in Google Cloud (in step 2) to access your google drive account.
    Upon confirming, a new `token.json` file will be created in your working directory

   b) Encode your token file to base64 (mac and linux only)
   `openssl base64 -in token.json -out output.txt`

   We need to do this step, because we want to add the token as a github enviornment variable.
   However, github does not allow json text to be used as an env variable. So this is a workaround

   For more information, see this thread: https://github.com/google-github-actions/setup-gcloud/issues/134


  IMPORTANT: Like with the `credentials.json` file, do not add either the `token.json` file
  or the `output.txt` file (where you'd store the tokens base64 encoding) to github. These files should remain private

  IMPORTANT: The token files will at some point expire. When this happens, simply repeat this step for a new token file 
  (and then repeat the following step with the token environment variable)

#### 5) Set your environment variable
    The script expects the following variable:
      - COLLAB_NOTEBOOK_NAME: Name of the collab notebook in your Google Drive
      - UPLOAD_FILE_PATH: Path to your local notebook
      - SECRET_TOKEN: The base64 encoded token

    **Set Env. variable locally** (for Mac and Linux)
    `export SECRET_TOKEN=$(cat output.txt)`
    `export COLLAB_NOTEBOOK_NAME=<YOUR NOTEBOOK NAME>`
    `export UPLOAD_FILE_PATH=<YOUR FILEPATH>`

    **Set Env. variable in Github**
    a) Copy the contents of your `output.txt` file
        `pbcopy < output.txt` (this command simply adds the contents of your file to your clipboard)
    b) In your github repo Go to `Settings`, then under the `Security`
       section on the lefthand side, hit `Secrets and Variables`, then `Actions`

    c) On github Hit the green "New repository secret" button
       In the "Name" field put "SECRET_TOKEN"
       And in the "Secret" field paste the contents of your `output.txt`
       Then hit "Add secret"
    
    TODO: ADD PICTURE

    To add `COLLAB_NOTEBOOK_NAME` and `UPLOAD_FILE_PATH` to github, go to the variables tab and add
    the two variables 

    TODO: ADD PICTURE

## Downloading a file
Run this script if you wish to fetch the latest version of you collab notebook file
from your Google Drive to your working directory

Ex: `python3 download_file.py --collab_notebook_name "Test Book" --save_path "test_notebooks/test"`
Will download a Collaboratory Notebook named "Test Book" and create a new file with the path `test_notebooks/test.ipynb`
in your working directory

## Uploading a file
NOTE: This script will run automatically everytime you push changes to github

But you can run this script if you wish to manually update your collab notebook file
from your Google Drive to your working directory by running: `python3 update_drive.py`

NOTE: if you wish to upload another notebook, simply change the env variables for 

## Contributing
At the current state, this project, small as it is, can of course be improved.
Any contribution in the following will be greatly appreciated:
    a) Simplifying the initial setup process
    b) Adding more automation/utility
    c) Improving code quality/readability, consistancy, etc
To contribute feel free to open a new Github issue or make a pull request addressing an existing issue