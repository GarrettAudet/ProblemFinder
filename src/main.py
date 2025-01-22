from src.google_drive import authenticate_google_drive, get_folder_id_by_path, download_files

if __name__ == "__main__":
    # Authenticate with Google Drive
    service = authenticate_google_drive()
    
    # Define the folder path and get its ID
    folder_path = "Praetor/Organizational Material/Customer Interviews"
    folder_id = get_folder_id_by_path(service, folder_path)
    if not folder_id:
        exit("Folder not found. Exiting.")
    
    # Download files with 'interview' in their names
    download_path = "data/downloads"
    download_files(service, folder_id, download_path)
