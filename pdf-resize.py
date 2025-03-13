import io
import PyPDF2
from reportlab.lib.pagesizes import A4

def resize_pdf_to_a4(input_pdf, output_pdf):
    with open(input_pdf, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            width, height = A4
            
            original_width = float(page.mediabox.width)
            original_height = float(page.mediabox.height)
            
            scale_x = width / original_width
            scale_y = height / original_height
            scale = min(scale_x, scale_y)
            
            # Create a new page with A4 size
            new_page = PyPDF2.PageObject.create_blank_page(width=width, height=height)
            
            # Merge and scale the original page
            new_page.merge_page(page)
            new_page.scale_by(scale)
            
            writer.add_page(new_page)
        
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

# Specific path usage
resize_pdf_to_a4(r'D:\tools\lamaran_olinnns.PDF', r'D:\tools\output_a4.pdf')