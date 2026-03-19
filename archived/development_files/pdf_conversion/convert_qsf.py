from markitdown import MarkItDown
import os

# Define the input and output paths relative to the script's location
pdf_input_path = "../paper/相关工作/Yang 等 - QSF multi-objective optimization based efficient solving for floating-point constraints.pdf"
md_output_path = "QSF_paper.md"

print(f"Attempting to convert '{pdf_input_path}'...")

# Check if the source file exists
if not os.path.exists(pdf_input_path):
    print(f"Error: Input file not found at the specified path.")
else:
    try:
        # Open the PDF file in binary read mode
        with open(pdf_input_path, "rb") as f:
            # Initialize the converter
            md = MarkItDown()
            # Convert the stream
            result = md.convert_stream(f)
            
            # Write the result to the output markdown file
            with open(md_output_path, "w", encoding="utf-8") as out_file:
                out_file.write(result.text_content)
        
        print(f"Successfully converted PDF to '{md_output_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")
