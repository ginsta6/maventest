import requests
import os
import json
import shutil
from urllib.parse import urlparse
from pathlib import Path

def create_download_folder(json_filename):
    # Create base images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")
    
    # Get the full name without extension
    base_name = Path(json_filename).stem
    # Create folder path
    folder_path = os.path.join("images", base_name)
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    return folder_path

def download_image(url, folder_path):
    try:
        # Get the filename from the URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # Create the full path for the image
        save_path = os.path.join(folder_path, filename)
        
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Save the image to a file
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Downloaded: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

def process_json_file(json_path):
    try:
        # Read the JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create download folder
        folder_path = create_download_folder(os.path.basename(json_path))
        print(f"\nProcessing: {os.path.basename(json_path)}")
        print(f"Downloading images to folder: {folder_path}")
        
        # Download each image
        total_images = len(data['image_urls'])
        successful_downloads = 0
        
        for i, url in enumerate(data['image_urls'], 1):
            print(f"\nDownloading image {i}/{total_images}")
            if download_image(url, folder_path):
                successful_downloads += 1
        
        # Move the JSON file to the images folder
        json_filename = os.path.basename(json_path)
        shutil.move(json_path, os.path.join(folder_path, json_filename))
        
        print(f"\nDownload complete!")
        print(f"Successfully downloaded {successful_downloads} out of {total_images} images")
        print(f"Files saved in: {os.path.abspath(folder_path)}")
        return True
        
    except FileNotFoundError:
        print(f"Error: JSON file '{json_path}' not found")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file '{json_path}'")
    except Exception as e:
        print(f"Error: {e}")
    return False

def main():
    # Create toDownload directory if it doesn't exist
    if not os.path.exists("toDownload"):
        os.makedirs("toDownload")
        print("Created 'toDownload' directory. Please place your JSON files there.")
        return
    
    # Get all JSON files from toDownload directory
    json_files = [f for f in os.listdir("toDownload") if f.endswith('.json')]
    
    if not json_files:
        print("No JSON files found in 'toDownload' directory.")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process each JSON file
    for json_file in json_files:
        json_path = os.path.join("toDownload", json_file)
        process_json_file(json_path)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()