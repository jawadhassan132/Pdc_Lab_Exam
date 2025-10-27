"""
Distributed Image Processing Script
Task 3: Simulated Distributed Task
- Simulates distributed environment using multiprocessing
- Divides images equally among 2 "nodes" (processes)
- Each node processes its subset independently
- Master process aggregates results
- Demonstrates distributed computing concepts (similar to MPI)
"""

import os
import time
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Process, Queue, Manager
import multiprocessing

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
    
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", 30)
        except:
            font = ImageFont.load_default()
    
    try:
        # For newer Pillow versions
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        # Fallback for older versions
        text_width, text_height = draw.textsize(watermark_text, font=font)
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), watermark_text, fill=(255, 255, 255, 80), font=font)
    
    txt_layer_rotated = txt_layer.rotate(30, expand=False)
    watermarked = Image.alpha_composite(watermarked, txt_layer_rotated)
    
    # Convert back to RGB
    return watermarked.convert('RGB')

def process_single_image(input_path, output_path, target_size=(128, 128)):
    """
    Process a single image
    """
    try:
        img = Image.open(input_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_resized = img.resize(target_size, Image.LANCZOS)
        img_watermarked = add_watermark(img_resized, "LAB EXAM")    
        img_watermarked.save(output_path, quality=95)
        
        return True
    except Exception as e:
        return False

def node_worker(node_id, image_tasks, output_dir, result_queue):
    """
    Worker function representing a distributed node
    Each node processes its assigned subset of images
    """
    # Start timing for this node
    start_time = time.time()
    
    # Process assigned images
    processed_count = 0
    for input_path, image_file, class_folder in image_tasks:
        output_class_path = os.path.join(output_dir, class_folder)
        output_path = os.path.join(output_class_path, image_file)
        
        if process_single_image(input_path, output_path):
            processed_count += 1
    
    # End timing
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Send results back to master
    result_queue.put({
        'node_id': node_id,
        'processed_count': processed_count,
        'time': execution_time
    })

def get_all_image_paths(input_dir):
    """
    Get all image paths from input directory
    """
    image_list = []
    
    # Get all class folders
    class_folders = [f for f in os.listdir(input_dir) 
                     if os.path.isdir(os.path.join(input_dir, f))]
    
    # Collect all image paths
    for class_folder in class_folders:
        input_class_path = os.path.join(input_dir, class_folder)
        
        # Get all image files in the class folder
        image_files = [f for f in os.listdir(input_class_path) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        
        # Add to list
        for image_file in image_files:
            input_path = os.path.join(input_class_path, image_file)
            image_list.append((input_path, image_file, class_folder))
    
    return image_list

def divide_tasks(image_list, num_nodes):
    """
    Divide images equally among nodes
    """
    tasks_per_node = []
    chunk_size = len(image_list) // num_nodes
    
    for i in range(num_nodes):
        start_idx = i * chunk_size
        if i == num_nodes - 1:
            # Last node gets remaining images
            end_idx = len(image_list)
        else:
            end_idx = start_idx + chunk_size
        
        tasks_per_node.append(image_list[start_idx:end_idx])
    
    return tasks_per_node

def main():
    """
    Master process - coordinates distributed processing
    Simulates distributed environment with 2 nodes
    """
    # Define paths
    input_dir = "Dataset"
    output_dir = "output_distributed"
    num_nodes = 2
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found!")
        return
    
    # Create output directory structure
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create class folders in output directory
    class_folders = [f for f in os.listdir(input_dir) 
                     if os.path.isdir(os.path.join(input_dir, f))]
    for class_folder in class_folders:
        output_class_path = os.path.join(output_dir, class_folder)
        if not os.path.exists(output_class_path):
            os.makedirs(output_class_path)
    
    # Get all images
    all_images = get_all_image_paths(input_dir)
    total_images = len(all_images)
    
    # Divide tasks among nodes
    node_tasks = divide_tasks(all_images, num_nodes)
    
    # Create queue for collecting results
    result_queue = Queue()
    
    # Start timing for total distributed execution
    total_start_time = time.time()
    
    # Create and start node processes
    processes = []
    for i in range(num_nodes):
        node_id = i + 1
        p = Process(target=node_worker, args=(node_id, node_tasks[i], output_dir, result_queue))
        processes.append(p)
        p.start()
    
    # Wait for all nodes to complete
    for p in processes:
        p.join()
    
    # End timing
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    # Collect results from all nodes
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    # Sort results by node_id for consistent output
    results.sort(key=lambda x: x['node_id'])
    
    # Print results for each node
    for result in results:
        print(f"Node {result['node_id']} processed {result['processed_count']} images in {result['time']:.1f}s")
    
    # Calculate efficiency (compared to sequential time)
    # Sequential time would be the sum of all node times if done one after another
    # But in distributed system, they run in parallel, so we take the max time (bottleneck)
    sequential_time = sum(r['time'] for r in results)
    efficiency = sequential_time / total_time
    
    print(f"Total distributed time: {total_time:.1f}s")
    print(f"Efficiency: {efficiency:.2f}x over sequential")

if __name__ == "__main__":
    main()
