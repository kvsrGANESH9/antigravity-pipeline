import os
import glob
import fitz  # PyMuPDF
import cv2
import config
from scale_fit import scale_and_fit

def get_pdf_page_count(pdf_path):
    """
    Returns the number of pages in a PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
    with fitz.open(pdf_path) as doc:
        return len(doc)

def convert_pdf_to_slides(pdf_path, output_dir):
    """
    Converts a PDF file to a sequence of JPEGs in output_dir.
    Names slide JPEGs as slide_001.jpg, slide_002.jpg, etc.
    
    If config.REUSE_EXISTING_SLIDES is True and output_dir already contains the expected slide JPEGs,
    the conversion is skipped.
    
    :return: (page_count, skipped)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    page_count = get_pdf_page_count(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if all slide JPEGs already exist
    all_exist = True
    for i in range(1, page_count + 1):
        slide_name = f"slide_{i:03d}.jpg"
        slide_path = os.path.join(output_dir, slide_name)
        if not os.path.exists(slide_path) or os.path.getsize(slide_path) == 0:
            all_exist = False
            break
            
    if config.REUSE_EXISTING_SLIDES and all_exist:
        return page_count, True
        
    # Clear directory of old slides if we are regenerating
    for f in glob.glob(os.path.join(output_dir, "slide_*.jpg")):
        try:
            os.remove(f)
        except Exception:
            pass
            
    print(f"Converting PDF '{pdf_path}' ({page_count} pages) to slides in '{output_dir}'...")
    
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            # Render page to an image
            pix = page.get_pixmap(dpi=150)
            slide_name = f"slide_{i+1:03d}.jpg"
            slide_path = os.path.join(output_dir, slide_name)
            pix.save(slide_path)
            
            # Post-process in-place to fit target video canvas from config.py
            try:
                fitted_img = scale_and_fit(
                    slide_path, 
                    target_width=config.TARGET_VIDEO_WIDTH, 
                    target_height=config.TARGET_VIDEO_HEIGHT
                )
                cv2.imwrite(slide_path, fitted_img)
            except Exception as e:
                print(f"Warning: Failed to scale slide {slide_name}: {e}")
            
    return page_count, False
