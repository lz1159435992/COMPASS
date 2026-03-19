import fitz  # PyMuPDF
import os

def convert_pdf_to_md(pdf_path, md_path):
    """
    Converts a PDF file to a Markdown file by extracting its text content.

    Args:
        pdf_path (str): The path to the input PDF file.
        md_path (str): The path to the output Markdown file.
    """
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        # Open the output markdown file
        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# Conversion of {os.path.basename(pdf_path)}\n\n")
            
            # Iterate through each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                
                md_file.write(f"## Page {page_num + 1}\n\n")
                md_file.write(text)
                md_file.write("\n\n---\n\n")
        
        print(f"Successfully converted '{pdf_path}' to '{md_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Define the relative paths
    # The script is in 'pdf_conversion', the PDF is in 'paper'
    pdf_input_path = "../paper/main.pdf"
    md_output_path = "output.md"
    
    # Ensure the output path is also within the 'pdf_conversion' directory
    # This is already handled by the md_output_path definition

    convert_pdf_to_md(pdf_input_path, md_output_path)
