from typing import Optional, Type
import os
import io
import json
import logging
import logging.handlers

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


SCOPES = [
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.metadata'
         ]

#Change this variable if needed
USE_PROD = True

#Declare types based on classes
Google_Credential_Type = Type[google.oauth2.credentials.Credentials]
Google_Resource_Type = Type[Resource]
Logger_Type = Type[logging.Logger]

#Handle logging
def init_logger(log_file_name: str):
    """Helper method to initialize the logger

    Args:
        log_file_name (str): name of file for logger to create
    
    Returns:
        logger object
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger_file_handler = logging.handlers.RotatingFileHandler(
        log_file_name,
        maxBytes=1024 * 1024,
        backupCount=1,
        encoding="utf8",
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)
    return logger

class GoogleDriver:
    def __init__(self, USE_API_KEY=False) -> None:
        self.creds = None
        if not USE_API_KEY:
            self.creds = self._hanlde_auth()

    def build_service(self) -> None:
        """Builds service either with or without creds configured to use api key
        
        NOTE: Currently the developer Key option is not supported

        Returns:
            None
        """
        if self.creds is None:
            service = build('drive', 'v3', developerKey=None)  
        else:
            service = build('drive', 'v3', credentials = self.creds)
        return service

    def _hanlde_auth(self, prod_mode=USE_PROD) -> Google_Credential_Type:
        """ Handle user authentication
        
        Permissions window will appear Code in this function taken directly from the drive api docs
        https://developers.google.com/drive/api/quickstart/python

        Args:
            prod_mode (bool): Named argument. If in prod mode, reads creds from env variable

        Returns:
            Credential Object of type Google_Credential_Type
        """
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            if prod_mode: #Use the secret token
                with open('temp_token.json', 'w') as f:
                    json.dump(json.loads(os.environ["SECRET_TOKEN"]), f)
                creds = Credentials.from_authorized_user_file('temp_token.json', SCOPES)
            else:
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    
    def drive_error_handle(func):
        """Decorator that wraps function calls in a try, except
        
        Args:
            func (function): Function being wrapped by the decorator

        Returns:
            Wrapper Decorator function
        """
        def wrapper(*args):
            try:
                # create drive api client
                func(*args)
            except HttpError as error:
                print(F'An error occurred: {error}')
        return wrapper

    
    def get_file_id(self, service: Google_Resource_Type, file_name: str) -> Optional[str]:
        """ Helper function that pulls the file id from a list of files
        
        Args:
            service (Google_Resource_Type): The Drive Service Object
            file_name (str): Name of file

        Returns:
            Optional string: Either a None or a String
        """
        file_list = service.files().list().execute()
        file_id = None
        for file in file_list.get('files', []):
            if file['name'] == file_name:
                file_id = file['id']

        return file_id
        
    
    @drive_error_handle
    def upload_file(self, file_path: str, upload_file_name: str, logger: Logger_Type) -> None:
        """ Upload new or update existing collab file in drive
        NOTE: file_path must have file_name with .ipynb extension

        Args:
            file_path (str): Path of file to be uploaded
            upload_file_name (str): Title of the file once in Google Drive
            logger (Logger_Type): The logger class object

        Returns:
            None

        Raises:
            ValueError: If the upload_file_name arg doesn't have the right 'ipynb' extension
        """

        #Make sure the extension is correct
        if not file_path.endswith('.ipynb'):
            error_msg = """Filename %s does not have the right extension.
                Needs to be a '.ipynb' file""" % file_path 
            logger.error(error_msg)
            raise ValueError(error_msg)


        service = self.build_service()
        # create drive api client
        file_path = f"{os.getcwd()}/{file_path}"
        
        #Create the file object
        file_metadata = {
            'name': upload_file_name,
            'mimeType': 'application/vnd.google.colaboratory'
        }

        media = MediaFileUpload(file_path, mimetype='application/vnd.google.colaboratory',
                        resumable=True)        

        #Get file id to see if this file already exists
        file_id = self.get_file_id(service, upload_file_name)
        if file_id is None:
            file = service.files().create(body=file_metadata, media_body=media,
                                        fields='id').execute()
            logger.info(F'File with ID: "{file.get("id")}" has been uploaded.')
        else:
            file = service.files().get(fileId=file_id).execute()
            del file['id'] #Needed for update
            updated_file = service.files().update(
            fileId=file_id,
            body=file,
            media_body=media).execute()
            logger.info(f'File with ID: "{updated_file.get("id")}" already exists and has been updated.')


    @drive_error_handle
    def rename_file(self, file_id: str, new_name: str) -> None:
        """Changes the name of a file for version control
        
        Args:
            file_id (str): Drive Id of the filename
            new_name (str): New name of the file

        Returns:
            None

        """
        service = self.build_service()
        service.files().update(fileId=file_id, body= {'title' : new_name}).execute()


    @drive_error_handle
    def delete_file(self, file_id: str) -> None:
        """ Handle file deletion
        
        Args:
            file_id (str): Drive Id of the filename

        Returns:
            None
        """
        service = self.build_service()
        service.files().delete(fileId=file_id).execute()


    @drive_error_handle
    def download_file(self, file_name: str, save_path: str, logger: Logger_Type) -> None:
        """Download latest version of file
        Args:
            file_name (str): Name/title of the file to download from drive
            save_path (str): file path to write the file to. Extension optional
            logger (Logger_Type): Logger object for saving information

        Returns:
            None
        
        Raises:
            ValueError: If file_name is not found in the user's Google Drive
        """
        service = self.build_service()
        file_id = self.get_file_id(service, file_name)
        
        if file_id is None:
            error_msg = "File with name %s not found" % file_name
            logger.error(error_msg)
            raise ValueError(error_msg)

        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False

        while done is False:
            status, done = downloader.next_chunk()
            logger.info(F'Download {int(status.progress() * 100)}.')
        file.seek(0)

        #Make sure the extension is ipynb
        if not save_path.endswith('.ipynb'):
            save_path = f'{save_path}.ipynb'

        with open(os.path.join('./',  save_path), 'wb') as f:
            f.write(file.read())
        
        logger.info("Download complete")
        logger.info(file.getvalue())
