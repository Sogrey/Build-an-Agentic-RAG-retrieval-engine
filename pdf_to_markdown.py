#!/usr/bin/env python3
"""
PDF to Markdown converter
"""

import os
import gc
import fitz  # PyMuPDF
from unstructured.partition.pdf import partition_pdf
from html2text import html2text

def convert_pdf_to_markdown(pdf_path, output_dir="pdf_images", output_md="output.md"):
    """
    Convert PDF to Markdown with extracted images
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save extracted images
        output_md (str): Output markdown file name
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📄 Processing PDF: {pdf_path}")
    
    try:
        # Step 1: Extract text/structured content with basic strategy (no network download)
        print("🔍 Step 1: Extracting text and structure (basic mode)...")
        elements = partition_pdf(
            filename=pdf_path,
            strategy="fast",  # Use fast strategy to avoid model downloads
            languages=["chi_sim", "eng"],  # Use languages instead of ocr_languages
            # Remove ocr_engine parameter to avoid PaddleOCR issues
        )
        print(f"✅ Extracted {len(elements)} elements")
        
        # Step 2: Extract images and save
        print("🖼️  Step 2: Extracting images...")
        doc = fitz.open(pdf_path)
        image_map = {}  # Map page_num -> list of image paths
        total_images = 0
        
        # Fix: Use len(doc) to get page count and iterate through page numbers
        total_pages = len(doc)
        for page_num in range(1, total_pages + 1):
            image_map[page_num] = []
            try:
                page = doc.load_page(page_num - 1)  # 0-based index
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
                        
                        image_map[page_num].append(img_path)
                        total_images += 1
                        pix = None  # Release memory
                        
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to extract image {img_index} from page {page_num}: {e}")
                        continue
                
                # Print progress every 50 pages
                if page_num % 50 == 0:
                    print(f"📄 Processed {page_num}/{total_pages} pages...")
                    
            except Exception as e:
                print(f"⚠️  Warning: Failed to process page {page_num}: {e}")
                continue
        
        doc.close()  # Close document to free memory
        print(f"✅ Extracted {total_images} images from {total_pages} pages")
        
        # Step 3: Convert to Markdown
        print("📝 Step 3: Converting to Markdown...")
        md_lines = []
        inserted_images = set()  # Track inserted images to avoid duplicates
        
        # Keep track of which images we've added for each page
        page_image_indices = {page_num: 0 for page_num in image_map.keys()}
        
        for i, el in enumerate(elements):
            try:
                cat = el.category
                text = el.text if el.text else ""
                page_num = getattr(el.metadata, 'page_number', 1)
                
                # Add images that correspond to this page before adding the text
                # This ensures images appear in the right place in the document
                if page_num in image_map:
                    images_for_page = image_map[page_num]
                    while page_image_indices[page_num] < len(images_for_page):
                        img_path = images_for_page[page_image_indices[page_num]]
                        if img_path not in inserted_images:
                            md_lines.append(f"![Image]({img_path})\n")
                            inserted_images.add(img_path)
                        page_image_indices[page_num] += 1
                
                if cat == "Title" and text.strip().startswith("- "):
                    md_lines.append(text + "\n")
                elif cat == "Title":
                    md_lines.append(f"# {text}\n")
                elif cat in ["Header", "Subheader"]:
                    md_lines.append(f"## {text}\n")
                elif cat == "Table":
                    if hasattr(el.metadata, "text_as_html") and el.metadata.text_as_html:
                        md_lines.append(html2text(el.metadata.text_as_html) + "\n")
                    else:
                        md_lines.append(text + "\n")
                elif cat == "Image":
                    # Image elements are handled above
                    pass
                else:
                    md_lines.append(text + "\n")
                
                # Print progress every 1000 elements
                if (i + 1) % 1000 == 0:
                    print(f"📝 Processed {i + 1}/{len(elements)} elements...")
                    
            except Exception as e:
                print(f"⚠️  Warning: Failed to process element {i}: {e}")
                continue
        
        # Add any remaining images that haven't been added yet
        for page_num, images in image_map.items():
            for img_path in images:
                if img_path not in inserted_images:
                    md_lines.append(f"![Image]({img_path})\n")
                    inserted_images.add(img_path)
        
        # Step 4: Write Markdown file
        print("💾 Step 4: Writing Markdown file...")
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        
        # Force garbage collection
        gc.collect()
        
        print(f"✅ Conversion completed successfully!")
        print(f"📄 Generated: {output_md}")
        print(f"🖼️  Image folder: {output_dir}/")
        print(f"📊 Statistics:")
        print(f"   - Total elements processed: {len(elements)}")
        print(f"   - Total images extracted: {total_images}")
        print(f"   - Markdown lines: {len(md_lines)}")
        print(f"   - Images referenced in markdown: {len(inserted_images)}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        raise

if __name__ == "__main__":
    # Configuration
    pdf_path = "MCP实战课件【合集】.pdf"
    output_dir = "pdf_images"
    output_md = "output.md"
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        exit(1)
    
    # Run conversion
    convert_pdf_to_markdown(pdf_path, output_dir, output_md)
