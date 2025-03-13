import fitz  # PyMuPDF
import os

def resize_pdf(input_pdf, output_pdf, target_size_mb):
    target_size_bytes = target_size_mb * 1024 * 1024  # Convert MB to bytes
    doc = fitz.open(input_pdf)
    
    # Iterate through pages and compress images
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)
        
        for img in images:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Compress image to reduce size
            if len(image_bytes) > 100 * 1024:  # Only compress if image is larger than 100KB
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha > 3:  # Convert to RGB if CMYK
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                # Reduce image quality
                pix.save(f"temp_img_{xref}.jpg", jpg_quality=70)
                with open(f"temp_img_{xref}.jpg", "rb") as f:
                    compressed_image = f.read()
                os.remove(f"temp_img_{xref}.jpg")
                
                # Replace the original image with the compressed one
                doc.delete_object(xref)
                doc.embedded_file_add(xref, "image/jpg", compressed_image)
    
    # Save the document and check the size
    doc.save(output_pdf)
    doc.close()
    
    # Check the final size
    final_size = os.path.getsize(output_pdf)
    if final_size > target_size_bytes:
        print(f"Warning: The final size is {final_size / (1024 * 1024):.2f} MB, which is larger than the target size.")
    else:
        print(f"Success: The final size is {final_size / (1024 * 1024):.2f} MB.")

# Usage
input_pdf = "input.pdf"
output_pdf = "output.pdf"
target_size_mb = 10  # Target size in MB

resize_pdf(input_pdf, output_pdf, target_size_mb)