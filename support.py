import os
import requests
import boto3
import streamlit as st

# def check_and_download_file(file_path, url):
#     if os.path.exists(file_path):
#         print(f"The file '{file_path}' already exists.")
#     else:
#         print(f"The file '{file_path}' does not exist. Downloading...")
#         try:
#             response = requests.get(url)
#             response.raise_for_status()  # Check if the request was successful
#             with open(file_path, 'wb') as file:
#                 file.write(response.content)
#             print(f"File downloaded successfully and saved as '{file_path}'.")
#         except requests.exceptions.RequestException as e:
#             print(f"An error occurred while downloading the file: {e}")

def check_and_download_file(file_path):
    if os.path.exists(file_path):
        print(f"The file '{file_path}' already exists.")
    else:
        print(f"The file '{file_path}' does not exist. Downloading...")
        try:
            ct = client()
            ct.download_file('rja-sanbernardino', 'orange county dashboard/'+file_path, file_path)
            print(f"File downloaded successfully and saved as '{file_path}'.")
        except:
            print(f"An error occurred while downloading the file: {'error'}")


def client():
    client = boto3.client(
    's3',
    aws_access_key_id=st.secrets['api_key'],
    aws_secret_access_key=st.secrets['secret_key'])

    return client