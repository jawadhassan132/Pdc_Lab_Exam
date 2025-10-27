"""
Sequential Image Processing Script
Task 1: Sequential Preprocessing
- Reads all images from Dataset folder
- Resizes each to 128x128
- Adds watermark to each image
- Saves to output_seq/ keeping class folders intact
- Prints total execution time
"""

import os
import time
from PIL import Image, ImageDraw, ImageFont

def add_watermark(image, watermark_text="LAB EXAM"):
    """
    Add a semi-transparent diagonal watermark to the image
    """
    # Create a copy to avoid modifying the original
    watermarked = image.copy().convert('RGBA')
    
    # Create a transparent layer for the watermark
    txt_layer = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
    
    # Create a drawing context
    draw = ImageDraw.Draw(txt_layer)
    
    # Define watermark properties
    width, height = watermarked.size
    
    # Try to use a font, fallback to default if not available
    try:
        # Try to load a larger font for better visibility
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", 30)
        except:
            # Use default font if arial is not available
            font = ImageFont.load_default()
    
    # Get text bounding box to calculate position
    try:
        # For newer Pillow versions
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        # Fallback for older versions
        text_width, text_height = draw.textsize(watermark_text, font=font)
    
    # Position at center of the image
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the watermark text in semi-transparent white (RGBA with alpha channel)
    # Using white color with 60 opacity (out of 255) for subtle effect
    draw.text((x, y), watermark_text, fill=(255, 255, 255, 80), font=font)
    
    # Rotate the text layer for diagonal watermark effect
    txt_layer_rotated = txt_layer.rotate(30, expand=False)
    
    # Composite the watermark onto the original image
    watermarked = Image.alpha_composite(watermarked, txt_layer_rotated)
    
    # Convert back to RGB
    return watermarked.convert('RGB')

def process_images_sequential(input_dir, output_dir, target_size=(128, 128)):
    """
    Process all images sequentially
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Counter for processed images
    processed_count = 0
    
    # Get all class folders
    class_folders = [f for f in os.listdir(input_dir) 
                     if os.path.isdir(os.path.join(input_dir, f))]
    
    print(f"Found {len(class_folders)} class folders: {', '.join(class_folders)}")
    print("Starting sequential processing...\n")
    
    for class_folder in class_folders:
        input_class_path = os.path.join(input_dir, class_folder)
        output_class_path = os.path.join(output_dir, class_folder)
        
        if not os.path.exists(output_class_path):
            os.makedirs(output_class_path)
        
        image_files = [f for f in os.listdir(input_class_path) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        
        print(f"Processing {len(image_files)} images from '{class_folder}' folder...")
        
        # Process each image
        for image_file in image_files:
            try:
                input_path = os.path.join(input_class_path, image_file)
                output_path = os.path.join(output_class_path, image_file)
                
                # Read the image
                img = Image.open(input_path)
                
                # Convert to RGB if necessary (for PNG with transparency, etc.)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize the image to 128x128
                img_resized = img.resize(target_size, Image.LANCZOS)
                
                # Add watermark
                img_watermarked = add_watermark(img_resized, "LAB EXAM")
                
                # Save the processed image
                img_watermarked.save(output_path, quality=95)
                
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing {image_file}: {str(e)}")
        
        print(f"Completed '{class_folder}' folder.\n")
    
    return processed_count

def main():
    """
    Main function to run sequential image processing
    """
    # Define paths
    input_dir = "Dataset"
    output_dir = "output_seq"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found!")
        return
    
    print("=" * 60)
    print("Sequential Image Processing")
    print("=" * 60)
    
    # Start timing
    start_time = time.time()
    
    # Process images
    processed_count = process_images_sequential(input_dir, output_dir)
    
    # End timing
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Print results
    print("=" * 60)
    print(f"Processing Complete!")
    print(f"Total images processed: {processed_count}")
    print(f"Sequential Processing Time: {execution_time:.2f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    main()
