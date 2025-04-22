import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def extract_name_and_amount(h4_element):
    """Extract name and amount from h4 element."""
    if not h4_element:
        return '', ''
    
    text = h4_element.get_text(strip=True)
    parts = text.split(',')
    if len(parts) > 1:
        return ','.join(parts[:-1]).strip(), parts[-1].strip()
    return text.strip(), ''

def extract_time(date_wrapper):
    """Extract time from date wrapper element."""
    if not date_wrapper:
        return ''
    
    time_span = date_wrapper.find('span')
    return time_span.get_text(strip=True) if time_span else ''

def extract_limited_to(card):
    """Extract limitedTo from x-icon image alt text."""
    x_icon = card.find('img', class_='x-icon')
    return x_icon.get('alt', '') if x_icon else ''

def extract_discount(card):
    """Extract discount from card."""
    discount_div = card.find('div', class_='discount')
    return discount_div.get_text(strip=True) if discount_div else ''

def extract_regular_prices(card):
    """Extract regular (non-AČIŪ) prices from card."""
    price_eur = card.find('div', class_='price-eur')
    price_cents = card.find('span', class_='price-cents')
    og_price = card.find('div', class_='price-old')
    
    price = ''
    if price_eur and price_cents:
        price = f"{price_eur.get_text(strip=True)},{price_cents.get_text(strip=True)}"
    
    return price, og_price.get_text(strip=True) if og_price else ''

def extract_aciu_prices(card):
    """Extract ACIU card prices."""
    price_elements = card.find_all('div', class_='price-eur')
    cents_elements = card.find_all('span', class_='price-cents')
    
    if len(price_elements) >= 2 and len(cents_elements) >= 2:
        og_price = f"{price_elements[0].get_text(strip=True)},{cents_elements[0].get_text(strip=True)}"
        price = f"{price_elements[1].get_text(strip=True)},{cents_elements[1].get_text(strip=True)}"
        return price, og_price
    return '', ''

def extract_card_data(card):
    """
    Extract specific fields from a card element.
    
    Args:
        card (BeautifulSoup element): The card-body element
        
    Returns:
        dict: Dictionary containing the extracted fields
    """
    # Initialize data structure
    data = {
        'name': '',
        'amount': '',
        'time': '',
        'discount': '',
        'price': '',
        'og_price': '',
        'needCard': False,
        'limitedTo': ''
    }
    
    # Extract basic information
    data['name'], data['amount'] = extract_name_and_amount(card.find('h4'))
    data['time'] = extract_time(card.find('p', class_='offer-dateTo-wrapper'))
    data['limitedTo'] = extract_limited_to(card)
    data['discount'] = extract_discount(card)
    
    # Handle AČIŪ cards
    is_aciu_card = card.find('img', title='AČIŪ') is not None
    data['needCard'] = is_aciu_card
    
    # Extract prices based on card type
    if is_aciu_card:
        data['price'], data['og_price'] = extract_aciu_prices(card)
    else:
        data['price'], data['og_price'] = extract_regular_prices(card)
    
    return data

def scrape_website(url):
    """
    Scrape data from the specified URL.
    
    Args:
        url (str): The URL of the website to scrape
        
    Returns:
        list: List of scraped data
    """
    try:
        # Send a GET request to the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all offer sections
        offer_sections = soup.find_all(id=lambda x: x and x.startswith('offer_list'))
        
        scraped_data = []
        for section in offer_sections:
            h2_element = section.find('h2')
            card_bodies = section.find_all(class_='card-body')
            card_data = [extract_card_data(card) for card in card_bodies]
            
            if h2_element or card_data:
                scraped_data.append({
                    'section_id': section.get('id', ''),
                    'title': h2_element.text.strip() if h2_element else '',
                    'items': card_data
                })
        
        return scraped_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while scraping: {e}")
        return []

def save_to_json(data, filename=None):
    """
    Save scraped data to a JSON file.
    
    Args:
        data (list): List of dictionaries containing the data to save
        filename (str, optional): Name of the JSON file. If None, generates a timestamp-based name.
    """
    if not data:
        print("No data to save")
        return
        
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraped_data_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

def main():
    url = "https://www.maxima.lt/pasiulymai"
    
    # Scrape the website
    scraped_data = scrape_website(url)
    
    # Save the data to JSON
    save_to_json(scraped_data)

if __name__ == "__main__":
    main()
