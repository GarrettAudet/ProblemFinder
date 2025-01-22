from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Define the scopes for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive():
    """Authenticate and return a Google Drive API service instance."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def get_folder_id_by_path(service, folder_path):
    """Navigate through the folder hierarchy to find the target folder."""
    folders = folder_path.split('/')
    parent_id = 'root'  # Start at the root directory

    for folder_name in folders:
        results = service.files().list(
            q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents",
            fields="files(id, name)"
        ).execute()
        folder_list = results.get('files', [])
        
        if not folder_list:
            print(f"Folder '{folder_name}' not found in the path.")
            return None

        # Use the first match (assuming unique folder names)
        parent_id = folder_list[0]['id']

    return parent_id

def download_files(service, folder_id, download_path):
    """Download all files containing 'interview' in the name from the specified folder."""
    os.makedirs(download_path, exist_ok=True)

    query = f"'{folder_id}' in parents and name contains 'interview' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("No files containing 'interview' found in the folder.")
        return

    for file in files:
        file_id = file['id']
        file_name = file['name']

        request = service.files().get_media(fileId=file_id)
        file_path = os.path.join(download_path, file_name)
        with open(file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloading {file_name}: {int(status.progress() * 100)}% complete.")

    print("All matching files have been downloaded.")

if __name__ == "__main__":
    # Authenticate and build the service
    service = authenticate_google_drive()

    # Get the folder ID
    folder_id = get_folder_id(service)
    if not folder_id:
        exit("Folder not found. Exiting.")

    # Define the download path
    download_path = "downloads"

    # Download files containing 'interview' in the name
    download_files(service, folder_id, download_path)