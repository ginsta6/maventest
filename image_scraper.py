import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from datetime import datetime
import os

def is_valid_image(src):
    # List of common placeholder or non-content image patterns
    placeholder_patterns = [
        'placeholder',
        'spacer',
        'blank',
        'pixel',
        'tracking',
        '1x1',
        'transparent',
        'loading',
        'default',
        'no-image',
        'empty'
    ]
    
    # Convert to lowercase for case-insensitive matching
    src_lower = src.lower()
    
    # Check if the URL contains any of the placeholder patterns
    if any(pattern in src_lower for pattern in placeholder_patterns):
        return False
        
    # Check if the URL contains '/brochures/'
    return 'admin/contentfiles/' in src_lower

def get_image_url(img):
    # Check for various lazy loading attributes
    for attr in ['data-src', 'data-lazy-src', 'data-original', 'data-srcset', 'src']:
        if img.get(attr):
            # For srcset, take the first URL
            if attr == 'data-srcset':
                return img.get(attr).split(',')[0].split(' ')[0]
            return img.get(attr)
    return None

def scrape_images(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all image tags
        images = soup.find_all('img')
        
        # Extract and process image URLs
        image_urls = []
        for img in images:
            src = get_image_url(img)
            if src and is_valid_image(src):
                absolute_url = urljoin(url, src)
                image_urls.append(absolute_url)
        
        return image_urls
    
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the webpage: {e}")
        return []

def save_to_json(image_urls, base_filename="brochure_images"):
    # Create toDownload directory if it doesn't exist
    if not os.path.exists("toDownload"):
        os.makedirs("toDownload")
    
    # Create a timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.json"
    filepath = os.path.join("toDownload", filename)
    
    # Create the data structure
    data = {
        "timestamp": timestamp,
        "total_images": len(image_urls),
        "image_urls": image_urls
    }
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"\nSaved {len(image_urls)} image URLs to {filepath}")
    return filepath

def main():
    # TODO: automate the scraping process and add dynamic file naming

    # Example URL - replace with the webpage you want to scrape
    url = "https://www.raskakcija.lt/maxima-akciju-leidinys.htm"
    
    print(f"Scraping images from: {url}")
    image_urls = scrape_images(url)
    
    if image_urls:
        # Save to JSON with custom base filename
        filename = save_to_json(image_urls, "maxima_brochures")
        print(f"File saved as: {os.path.abspath(filename)}")
    else:
        print("No valid images found or an error occurred.")

if __name__ == "__main__":
    main()