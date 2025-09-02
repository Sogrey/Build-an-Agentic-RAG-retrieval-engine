#!/usr/bin/env python3
"""
PyMuPDF-only PDF to Markdown converter (completely offline, no network dependencies)
"""

import os
import fitz  # PyMuPDF

def convert_pdf_to_markdown_offline(pdf_path, output_dir="pdf_images", output_md="output.md"):
    """
    Convert PDF to Markdown using only PyMuPDF (completely offline)
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save extracted images
        output_md (str): Output markdown file name
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📄 Processing PDF: {pdf_path}")
    
    try:
        # Open PDF document
        doc = fitz.open(pdf_path)
        print(f"✅ PDF opened successfully - {len(doc)} pages")
        
        md_lines = []
        total_images = 0
        
        # Process each page
        for page_num, page in enumerate(doc, start=1):
            print(f"📄 Processing page {page_num}/{len(doc)}...")
            
            # Extract text from page
            text = page.get_text()
            if text.strip():
                # Simple text processing - split into paragraphs
                paragraphs = text.split('\\n\\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        # Simple heuristic for headers (short lines, no lowercase)
                        if len(para) < 100 and para.isupper():
                            md_lines.append(f"## {para}\\n")
                        else:
                            md_lines.append(f"{para}\\n\\n")
            
            # Extract images from page
            images = page.get_images(full=True)
            for img_index, img in enumerate(images, start=1):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    img_path = os.path.join(output_dir, f"page{page_num}_img{img_index}.png")
                    
                    if pix.n < 5:  # RGB / Gray
                        pix.save(img_path)
                    else:  # CMYK to RGB conversion
                        rgb_pix = fitz.Pixmap(fitz.csRGB, pix)
                        rgb_pix.save(img_path)
                        rgb_pix = None  # Release memory
                    
                    # Add image reference to markdown
                    md_lines.append(f"![Image]({img_path})\\n\\n")
                    total_images += 1
                    pix = None  # Release memory
                    
                except Exception as e:
                    print(f"⚠️  Warning: Failed to extract image {img_index} from page {page_num}: {e}")
                    continue
        
        total_pages = len(doc)  # Store page count before closing
        doc.close()  # Close document to free memory
        
        # Write Markdown file
        print("💾 Writing Markdown file...")
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("".join(md_lines))
        
        print(f"✅ Conversion completed successfully!")
        print(f"📄 Generated: {output_md}")
        print(f"🖼️  Image folder: {output_dir}/")
        print(f"📊 Statistics:")
        print(f"   - Total pages processed: {total_pages}")
        print(f"   - Total images extracted: {total_images}")
        print(f"   - Markdown lines: {len(md_lines)}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        raise

if __name__ == "__main__":
    # Configuration
    pdf_path = "MCP实战课件【合集】.pdf"
    output_dir = "pdf_images"
    output_md = "output_pymupdf.md"
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        exit(1)
    
    # Run conversion
    convert_pdf_to_markdown_offline(pdf_path, output_dir, output_md)