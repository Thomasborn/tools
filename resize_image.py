import os
from PIL import Image
import math

def calculate_compression_ratio(current_size_mb, target_size_mb):
    """Calculate the compression ratio needed to achieve target file size"""
    return math.sqrt(target_size_mb / current_size_mb)

def resize_image(input_path, output_path, target_size_mb, output_format):
    """
    Resize image to match target file size in MB and convert to specified format
    
    Parameters:
    input_path (str): Path to input image
    output_path (str): Path to save output image
    target_size_mb (float): Desired file size in MB
    output_format (str): Desired output format (e.g., 'JPEG', 'PNG', 'WEBP')
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Get current file size in MB
        current_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        
        # Calculate initial dimensions
        width, height = img.size
        
        # If current size is already smaller than target, just convert format
        if current_size_mb <= target_size_mb:
            img.save(output_path, format=output_format, quality=95)
            print(f"Image converted to {output_format} without resizing")
            return
        
        # Calculate compression ratio
        ratio = calculate_compression_ratio(current_size_mb, target_size_mb)
        
        # Calculate new dimensions
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Initial resize
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with different quality settings until we get close to target size
        quality = 95
        min_quality = 5
        
        while quality >= min_quality:
            temp_output = f"temp_output.{output_format.lower()}"
            resized_img.save(temp_output, format=output_format, quality=quality)
            
            new_size_mb = os.path.getsize(temp_output) / (1024 * 1024)
            
            if new_size_mb <= target_size_mb * 1.1:  # Allow 10% margin
                os.rename(temp_output, output_path)
                print(f"Successfully resized image to {new_size_mb:.2f}MB")
                return
            
            os.remove(temp_output)
            quality -= 5
        
        print("Warning: Could not achieve target size while maintaining acceptable quality")
        # Save with minimum quality as fallback
        resized_img.save(output_path, format=output_format, quality=min_quality)
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise

def main():
    # Get user input
    input_path = input("Enter input image path: ")
    target_size = float(input("Enter target size in MB: "))
    output_format = input("Enter output format (JPEG/PNG/WEBP): ").upper()
    
    # Generate output path
    output_path = f"resized_image.{output_format.lower()}"
    
    # Validate input
    if not os.path.exists(input_path):
        print("Error: Input file does not exist")
        return
        
    if output_format not in ['JPEG', 'PNG', 'WEBP']:
        print("Error: Unsupported format. Please choose JPEG, PNG, or WEBP")
        return
        
    if target_size <= 0:
        print("Error: Target size must be greater than 0")
        return
    
    # Process the image
    resize_image(input_path, output_path, target_size, output_format)

if __name__ == "__main__":
    main()