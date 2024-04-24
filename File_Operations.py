######################################################
# Project Phase 2 - File_Operations                  #
# Backend for the file operations of the file server #
######################################################

import os
import shutil
import json

FILE_STORAGE_PATH = 'D:\\CryptoCode\\file_storage'  # Directory for storing files (!!!change to your own directory!!!)
JSON_FILE = 'data.json'                             # JSON file to store user and group information

# Function to load data from JSON file
def load_data():
    try:
        with open(JSON_FILE, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"Internal Error": "Data file not found."}
    
# Function to list files associated with a user token 
def list_files(user_token):
    # Initialize list to store user's files
    userfiles=[]
    try:
        # Load data from JSON file
        data = load_data()
        # Find the user in the tokens list
        user_info = next((user for user in data['tokens'] if user['plain_token'] == user_token), None)
        if user_info:
            # Find groups where the user is a member 
            user_groups = [group for group in data['groups'] if user_info['username'] in group['members'] or user_info['username'] == group['owner']]
            # Print file names from the user's groups
            for group in user_groups:
                print(f"Files in group '{group['groupname']}':")
                if 'files' in group:
                    for file_name in group['files']:
                        userfiles.append(file_name)
                        print(file_name)
                else:
                    print("No files found in this group.")
            return userfiles
        else:
            print("User token not found.")
            return False
        
    except Exception as e:
        print(f"Error listing files: {e}")
        return False

# Function to get username from token
def get_username_from_token(token):
    # Load data from JSON file
    data = load_data()
    for user_token in data['tokens']:
        if user_token['plain_token'] == token:
            return user_token['username']
    return None

# Function to check if user is in a group
def is_user_in_group(groupname, token):
    # Load data from JSON file
    data = load_data()
    # Find the user's token in the tokens list
    user = next((user for user in data['tokens'] if user['username'] == get_username_from_token(token)), None)
    if user and user['plain_token'] == token:
        # Find the group in the groups list
        group = next((group for group in data['groups'] if group['groupname'] == groupname), None)
        if group and group['owner'] == get_username_from_token(token):
            # User is the owner of the group
            return True
        elif group and get_username_from_token(token) in group['members']:
            # User is a member of the group
            return True
    # User is not in the group or provided incorrect token
    return False

#Function to update group files
def update_group_files(groupname, distFile):
    # Load the JSON data containing group information
    with open('data.json', 'r') as file:
        data = json.load(file)
    # Find the group in the groups list
    group = next((group for group in data['groups'] if group['groupname'] == groupname), None)
    if group:
        # Add the distFile to the files field of the group
        group['files'].append(distFile)
        # Update the JSON file with the modified data
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)
        return True
    else:
        # Group not found
        return False  

# Function to upload a file to a group
def upload_file(sourceFile, distFile, groupname, token):
    try:
        #print("Uploading file...")
        if is_user_in_group(groupname, token) == False:
            print("User is not in the group or provided incorrect token")
            return False
        
        #Get the source file path and destination file path
        if not os.path.exists(sourceFile):
            print("Source file not found")
            return False
        
        source_path = os.path.join(sourceFile)
        dist_path = os.path.join(FILE_STORAGE_PATH, distFile)
        print(f"Copying file from {source_path} to {dist_path}")
        # Copy the file instead of moving it
        shutil.copyfile(source_path, dist_path)  
        print("File uploaded successfully")
    
        if update_group_files(groupname, distFile):
            #print("VERIFIED")
            return True
        else:
            print("Group not found")
            return False
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

# Function to download a file from the server
def download_file(serverFile, userFile, token):
    try:
        data = load_data()
        
        # Check if the user is part of the group that the file belongs to
        user_groups = get_user_groups(token)
        serverFile_group = next((group for group in data['groups'] if serverFile in group.get('files', [])), None)
        if not serverFile_group or serverFile_group['groupname'] not in user_groups:
            print("User is not part of the group or provided incorrect token.")
            return False
        
        # Check if the file exists in the group's files list
        if serverFile not in serverFile_group['files']:
            print("File not found in the group.")
            return False
        
        # Copy the file to the user's desired location
        source_path = os.path.join(FILE_STORAGE_PATH, serverFile)
        shutil.copy(source_path, userFile)
        print(f"File '{serverFile}' downloaded successfully to '{userFile}'.")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def get_user_groups(user_token):
    try:
        # Load data from JSON file
        data = load_data()

        # Find the user in the tokens list
        user_info = next((user for user in data['tokens'] if user['plain_token'] == user_token), None)
        if user_info:
            # Find groups where the user is a member or owner and extract only the groupnames
            user_groupnames = [group['groupname'] for group in data['groups'] if user_info['username'] in group['members'] or user_info['username'] == group['owner']]
            return user_groupnames
        else:
            print("User token not found.")
            return []
    except Exception as e:
        print(f"Error fetching user groups: {e}")
        return []
