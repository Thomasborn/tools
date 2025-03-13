#!/usr/bin/env python3
"""
Exact 1MB PDF Resizer - Converts any PDF to exactly (or very close to) 1MB size
"""

import os
import sys
import tempfile
import shutil
import math
import argparse
from PyPDF2 import PdfReader, PdfWriter

# Try to import optional dependencies
try:
    from PIL import Image
    import img2pdf
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def get_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def convert_pdf_to_images(pdf_path, output_dir, dpi=150):
    """Convert PDF to images using Pillow"""
    if not HAS_PIL:
        print("Error: Pillow and img2pdf are required for this operation.")
        return []
    
    try:
        # Try to use pdf2image which is more reliable for PDFs
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=dpi)
            image_files = []
            for i, img in enumerate(images):
                img_path = os.path.join(output_dir, f"page_{i+1:03d}.jpg")
                img.save(img_path, "JPEG")
                image_files.append(img_path)
            return image_files
        except ImportError:
            print("Warning: pdf2image not found. Using less reliable method.")
            pass
        
        # Fallback to direct PIL reading (less reliable)
        from PIL import Image
        images = []
        i = 0
        try:
            pdf = Image.open(pdf_path)
            while True:
                img_path = os.path.join(output_dir, f"page_{i+1:03d}.jpg")
                pdf.seek(i)
                pdf.save(img_path, "JPEG")
                images.append(img_path)
                i += 1
        except EOFError:
            pass
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

def compress_images(image_files, quality):
    """Compress images to specified quality"""
    if not HAS_PIL:
        return False
    
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            img.save(img_path, "JPEG", quality=quality)
        except Exception as e:
            print(f"Error compressing image {img_path}: {e}")
            return False
    return True

def create_pdf_from_images(image_files, output_path):
    """Create PDF from images"""
    if not HAS_PIL:
        return False
    
    try:
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(image_files))
        return True
    except Exception as e:
        print(f"Error creating PDF from images: {e}")
        return False

def resize_to_exact_size(input_path, output_path, target_size_mb=1.0):
    """Resize PDF to exact target size using precise binary search"""
    input_size = get_size_mb(input_path)
    print(f"Input file size: {input_size:.2f} MB")
    
    if input_size <= target_size_mb:
        print(f"File is already smaller than {target_size_mb} MB")
        shutil.copy(input_path, output_path)
        return True
    
    # Create temp directory for working files
    temp_dir = tempfile.mkdtemp()
    temp_output = os.path.join(temp_dir, "output.pdf")
    
    try:
        # First try simple compression with PyPDF2
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        
        with open(temp_output, 'wb') as f:
            writer.write(f)
        
        simple_size = get_size_mb(temp_output)
        print(f"Basic compression result: {simple_size:.2f} MB")
        
        # If already within 5% of target size, we're done
        if 0.95 * target_size_mb <= simple_size <= 1.05 * target_size_mb:
            shutil.copy(temp_output, output_path)
            print(f"Basic compression achieved target size: {simple_size:.2f} MB")
            return True
        
        # If still too large, use image conversion with binary search
        if simple_size > target_size_mb:
            # Extract images
            print("Converting PDF to images...")
            image_dir = os.path.join(temp_dir, "images")
            os.makedirs(image_dir, exist_ok=True)
            
            image_files = convert_pdf_to_images(input_path, image_dir)
            if not image_files:
                print("Failed to convert PDF to images")
                return False
            
            print(f"Converted {len(image_files)} pages to images")
            
            # Binary search for exact size
            min_quality = 1
            max_quality = 100
            best_quality = 50
            best_diff = float('inf')
            iterations = 0
            max_iterations = 10
            
            # Keep track of best result
            best_output = None
            
            while min_quality <= max_quality and iterations < max_iterations:
                iterations += 1
                current_quality = (min_quality + max_quality) // 2
                print(f"Trying quality: {current_quality} (iteration {iterations}/{max_iterations})")
                
                # Create temp output for this quality
                iter_output = os.path.join(temp_dir, f"output_q{current_quality}.pdf")
                
                # Compress images with current quality
                temp_images_dir = os.path.join(temp_dir, f"images_q{current_quality}")
                os.makedirs(temp_images_dir, exist_ok=True)
                
                # Copy and compress images
                temp_images = []
                for i, img_path in enumerate(image_files):
                    new_path = os.path.join(temp_images_dir, f"page_{i+1:03d}.jpg")
                    try:
                        img = Image.open(img_path)
                        img.save(new_path, "JPEG", quality=current_quality)
                        temp_images.append(new_path)
                    except Exception as e:
                        print(f"Error processing image: {e}")
                
                # Create PDF from compressed images
                if not create_pdf_from_images(temp_images, iter_output):
                    print("Failed to create PDF from compressed images")
                    continue
                
                # Check size
                current_size = get_size_mb(iter_output)
                current_diff = abs(current_size - target_size_mb)
                
                print(f"  Quality {current_quality} resulted in {current_size:.3f} MB (diff: {current_diff:.3f} MB)")
                
                # Check if this is our best result so far
                if current_diff < best_diff:
                    best_diff = current_diff
                    best_quality = current_quality
                    best_output = iter_output
                    
                    # If we're close enough (within 1%), we're done
                    if current_diff < 0.01 * target_size_mb:
                        print(f"Found sufficiently close result: {current_size:.3f} MB")
                        break
                
                # Adjust search range
                if current_size > target_size_mb:
                    max_quality = current_quality - 1
                else:
                    min_quality = current_quality + 1
            
            # Copy best result to output
            if best_output and os.path.exists(best_output):
                shutil.copy(best_output, output_path)
                print(f"Best quality found: {best_quality}")
                final_size = get_size_mb(output_path)
                print(f"Final size: {final_size:.3f} MB (target: {target_size_mb:.1f} MB)")
                return True
            else:
                print("Failed to find suitable quality setting")
                return False
        else:
            # Already smaller than target, just copy
            shutil.copy(temp_output, output_path)
            return True
            
    except Exception as e:
        print(f"Error during processing: {e}")
        return False
    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="Resize a PDF to exactly 1MB")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-o", "--output", help="Output PDF file (default: input_1mb.pdf)")
    parser.add_argument("-s", "--size", type=float, default=1.0, help="Target size in MB (default: 1.0)")
    
    args = parser.parse_args()
    
    input_path = args.input
    
    # Default output path if not specified
    if not args.output:
        input_base = os.path.splitext(input_path)[0]
        args.output = f"{input_base}_1mb.pdf"
    
    print(f"Resizing {input_path} to {args.size} MB...")
    
    if resize_to_exact_size(input_path, args.output, args.size):
        print(f"Success! Output saved to: {args.output}")
        print(f"Final size: {get_size_mb(args.output):.3f} MB")
    else:
        print("Failed to resize PDF.")
        sys.exit(1)

if __name__ == "__main__":
    main()