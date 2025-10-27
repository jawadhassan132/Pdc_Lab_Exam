"""
Parallel Image Processing Script
Task 2: Parallel Processing using Multiprocessing
- Performs same operations as sequential but in parallel
- Uses multiprocessing.Pool for true parallelism (multiple CPU cores)
- Tests with 1, 2, 4, and 8 worker processes
- Saves to output_parallel/
- Displays speedup table and efficiency metrics
"""

import os
import time
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool, cpu_count

def add_watermark(image, watermark_text="PROCESSED"):
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
    # Using white color with 80 opacity (out of 255) for subtle effect
    draw.text((x, y), watermark_text, fill=(255, 255, 255, 80), font=font)
    
    # Rotate the text layer for diagonal watermark effect
    txt_layer_rotated = txt_layer.rotate(30, expand=False)
    
    # Composite the watermark onto the original image
    watermarked = Image.alpha_composite(watermarked, txt_layer_rotated)
    
    # Convert back to RGB
    return watermarked.convert('RGB')

def process_single_image(args):
    """
    Process a single image (for parallel execution)
    """
    input_path, output_path, target_size = args
    
    try:
        # Read the image
        img = Image.open(input_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize the image to 128x128
        img_resized = img.resize(target_size, Image.LANCZOS)
        
        # Add watermark
        img_watermarked = add_watermark(img_resized, "PROCESSED")
        
        # Save the processed image
        img_watermarked.save(output_path, quality=95)
        
        return True
    except Exception as e:
        print(f"Error processing {os.path.basename(input_path)}: {str(e)}")
        return False

def get_all_image_paths(input_dir, output_dir, target_size=(128, 128)):
    """
    Get all image paths for processing
    """
    image_tasks = []
    
    # Get all class folders
    class_folders = [f for f in os.listdir(input_dir) 
                     if os.path.isdir(os.path.join(input_dir, f))]
    
    # Collect all image paths
    for class_folder in class_folders:
        input_class_path = os.path.join(input_dir, class_folder)
        output_class_path = os.path.join(output_dir, class_folder)
        
        # Create output class folder
        if not os.path.exists(output_class_path):
            os.makedirs(output_class_path)
        
        # Get all image files in the class folder
        image_files = [f for f in os.listdir(input_class_path) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        
        # Add to task list
        for image_file in image_files:
            input_path = os.path.join(input_class_path, image_file)
            output_path = os.path.join(output_class_path, image_file)
            image_tasks.append((input_path, output_path, target_size))
    
    return image_tasks

def process_images_parallel(input_dir, output_dir, num_workers, target_size=(128, 128)):
    """
    Process all images in parallel using multiprocessing.Pool
    This creates separate processes (not threads) for true parallel execution
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all image tasks
    image_tasks = get_all_image_paths(input_dir, output_dir, target_size)
    
    # Process images in parallel using multiprocessing Pool
    # Pool creates worker processes that can run on different CPU cores
    with Pool(processes=num_workers) as pool:
        results = pool.map(process_single_image, image_tasks)
    
    # Count successful processes
    processed_count = sum(results)
    
    return processed_count

def main():
    """
    Main function to run parallel image processing with different worker configurations
    Demonstrates concepts: Speedup, Efficiency, and Scalability
    """
    # Define paths
    input_dir = "Dataset"
    output_dir = "output_parallel"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found!")
        return
    
    print("=" * 60)
    print("Parallel Image Processing with Multiprocessing")
    print("=" * 60)
    print(f"Available CPU cores: {cpu_count()}")
    print("=" * 60)
    
    # Worker configurations to test
    worker_configs = [1, 2, 4, 8]
    
    # Store results
    results = []
    
    # Test each configuration
    for num_workers in worker_configs:
        print(f"\nTesting with {num_workers} worker process(es)...")
        
        # Start timing
        start_time = time.time()
        
        # Process images
        processed_count = process_images_parallel(input_dir, output_dir, num_workers)
        
        # End timing
        end_time = time.time()
        execution_time = end_time - start_time
        
        results.append({
            'workers': num_workers,
            'time': execution_time,
            'count': processed_count
        })
        
        print(f"Completed: {processed_count} images in {execution_time:.2f} seconds")
    
    # Calculate speedup and efficiency relative to 1 worker (sequential)
    base_time = results[0]['time']
    
    # Print detailed performance table
    print("\n" + "=" * 60)
    print("Performance Analysis:")
    print("=" * 60)
    print(f"{'Workers':<10} | {'Time (s)':<10} | {'Speedup':<10} | {'Efficiency':<10}")
    print("-" * 60)
    
    for result in results:
        speedup = base_time / result['time']
        efficiency = (speedup / result['workers']) * 100  # as percentage
        print(f"{result['workers']:<10} | {result['time']:<10.2f} | {speedup:<10.2f}x | {efficiency:<9.2f}%")
    
    print("=" * 60)
    print("\nKey Parallel Computing Metrics:")
    print(f"- Base Time (1 worker): {base_time:.2f} seconds")
    print(f"- Best Time ({worker_configs[-1]} workers): {results[-1]['time']:.2f} seconds")
    print(f"- Maximum Speedup Achieved: {base_time / results[-1]['time']:.2f}x")
    print("=" * 60)

if __name__ == "__main__":
    main()
