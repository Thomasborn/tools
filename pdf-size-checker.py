import PyPDF2
import math
import os

class PaperSizeChecker:
    # Standard paper sizes in millimeters (width, height)
    PAPER_SIZES = {
        'A0': (841, 1189),
        'A1': (594, 841),
        'A2': (420, 594),
        'A3': (297, 420),
        'A4': (210, 297),
        'A5': (148, 210),
        'A6': (105, 148),
        'B0': (1000, 1414),
        'B1': (707, 1000),
        'B2': (500, 707),
        'B3': (353, 500),
        'B4': (250, 353),
        'B5': (176, 250),
        'Letter': (216, 279),
        'Legal': (216, 356),
        'Tabloid': (279, 432)
    }

    @staticmethod
    def get_pdf_dimensions(file_path):
        """
        Retrieve the dimensions of the PDF pages.
        
        Args:
            file_path (str): Path to the PDF file
        
        Returns:
            tuple: (width, height) of the first page in points
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Get the first page
                if len(reader.pages) > 0:
                    page = reader.pages[0]
                    
                    # Get page size in points
                    width = page.mediabox.width
                    height = page.mediabox.height
                    
                    return width, height
                else:
                    return None
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    @staticmethod
    def points_to_mm(points):
        """
        Convert points to millimeters (1 point = 1/72 inch, 1 inch = 25.4 mm)
        
        Args:
            points (float): Dimension in points
        
        Returns:
            float: Dimension in millimeters
        """
        return points * 25.4 / 72

    def categorize_paper_size(self, width_mm, height_mm):
        """
        Categorize PDF dimensions to standard paper sizes.
        
        Args:
            width_mm (float): Width of the page in millimeters
            height_mm (float): Height of the page in millimeters
        
        Returns:
            list: Matching paper sizes
        """
        # Round dimensions to nearest integer
        width_mm = round(width_mm)
        height_mm = round(height_mm)
        
        matching_sizes = []
        for size, (std_width, std_height) in self.PAPER_SIZES.items():
            # Check both portrait and landscape orientations
            if ((abs(width_mm - std_width) < 2 and abs(height_mm - std_height) < 2) or 
                (abs(width_mm - std_height) < 2 and abs(height_mm - std_width) < 2)):
                matching_sizes.append(size)
        
        return matching_sizes

    def analyze_pdf(self, file_path):
        """
        Comprehensive PDF size analysis.
        
        Args:
            file_path (str): Path to the PDF file
        
        Returns:
            dict: Detailed PDF size information
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return {"error": "File does not exist"}
        
        # Get file size
        file_size_bytes = os.path.getsize(file_path)
        
        # Get PDF dimensions
        dimensions = self.get_pdf_dimensions(file_path)
        
        if dimensions is None:
            return {"error": "Could not read PDF dimensions"}
        
        # Convert dimensions to millimeters
        width_points, height_points = dimensions
        width_mm = self.points_to_mm(width_points)
        height_mm = self.points_to_mm(height_points)
        
        # Categorize paper size
        paper_sizes = self.categorize_paper_size(width_mm, height_mm)

        return {
            "file_path": file_path,
            "file_size_bytes": file_size_bytes,
            "file_size_kb": file_size_bytes / 1024,
            "file_size_mb": file_size_bytes / (1024 * 1024),
            "width_points": width_points,
            "height_points": height_points,
            "width_mm": round(width_mm, 2),
            "height_mm": round(height_mm, 2),
            "matched_paper_sizes": paper_sizes if paper_sizes else ["No standard size match"]
        }

# Example usage
def main():
    # Replace with the path to your PDF file
    pdf_path = "D:\\tools\\lamaran_olinnns.PDF"

    
    # Create an instance of the paper size checker
    checker = PaperSizeChecker()
    
    # Analyze the PDF
    analysis = checker.analyze_pdf(pdf_path)
    
    # Print the results
    print("PDF Size Analysis:")
    for key, value in analysis.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
