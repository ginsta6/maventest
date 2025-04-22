import pytesseract
# Tell pytesseract where the tesseract executable is
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image, ImageEnhance, ImageFilter
import os
import json
from datetime import datetime

def preprocess_image(img):
    # Convert to grayscale
    img = img.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Increase contrast
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)  # Increase sharpness
    
    # Apply slight blur to reduce noise
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Apply threshold to make text more distinct
    img = img.point(lambda x: 0 if x < 128 else 255, '1')
    
    return img

def extract_text_from_image(image_path):
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Preprocess the image
        # img = preprocess_image(img)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(img, lang='lit')
        
        return text.strip()
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def process_images_in_folder(folder_path):
    # Get all image files in the folder
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = [f for f in os.listdir(folder_path) 
                  if os.path.isfile(os.path.join(folder_path, f)) 
                  and os.path.splitext(f)[1].lower() in image_extensions]
    
    if not image_files:
        print(f"No image files found in {folder_path}")
        return
    
    # Create results directory if it doesn't exist
    results_dir = "text_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Create a timestamp for the results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = os.path.basename(folder_path)
    results_file = os.path.join(results_dir, f"{folder_name}_text_{timestamp}.json")
    
    # Process each image
    results = {
        "timestamp": timestamp,
        "source_folder": folder_path,
        "total_images": len(image_files),
        "processed_images": []
    }
    
    for i, image_file in enumerate(image_files, 1):
        print(f"\nProcessing image {i}/{len(image_files)}: {image_file}")
        image_path = os.path.join(folder_path, image_file)
        
        text = extract_text_from_image(image_path)
        if text:
            results["processed_images"].append({
                "image_name": image_file,
                "extracted_text": text
            })
            print(f"Successfully extracted text from {image_file}")
        else:
            print(f"Failed to extract text from {image_file}")
    
    # Save results to JSON file
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"\nResults saved to: {results_file}")
    return results_file

def main():
    # Example usage - replace with your folder path
    folder_path = "./images/testing"
    process_images_in_folder(folder_path)

if __name__ == "__main__":
    main() 