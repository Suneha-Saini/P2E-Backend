import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Flush helper
def log(msg):
    print(msg, flush=True)

try:
    log("Importing easyocr...")
    import easyocr
    log("Importing cv2...")
    import cv2
    log("Importing numpy...")
    import numpy as np
    log("Importing fitz...")
    import fitz
    log("Importing PIL.Image...")
    from PIL import Image
    import io
except Exception as e:
    log(f"Import error: {e}")
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)

def test():
    try:
        log("Initializing EasyOCR Reader...")
        reader = easyocr.Reader(['en'], gpu=False)
        log("EasyOCR Reader initialized successfully.")
        
        pdf_path = r"d:\pdf-excel\backend\uploads\4dc65510-adeb-45db-bc69-65609b326126.pdf"
        log(f"Opening PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        log(f"PDF opened. Page count: {len(doc)}")
        
        page = doc.load_page(0)
        log("Loaded page 0. Rendering pixmap...")
        pix = page.get_pixmap(dpi=150)
        log(f"Pixmap rendered. Size: {pix.width}x{pix.height}")
        
        img_data = pix.tobytes("png")
        log(f"Pixmap converted to PNG bytes. Length: {len(img_data)}")
        
        # Load image with PIL
        log("Loading image with PIL...")
        image = Image.open(io.BytesIO(img_data))
        img_np = np.array(image)
        log(f"PIL image converted to numpy array. Shape: {img_np.shape}, Dtype: {img_np.dtype}")
        
        # Convert RGB to BGR if needed
        if len(img_np.shape) == 3 and img_np.shape[2] == 3:
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            log("Converted RGB to BGR.")
        else:
            img_cv = img_np
            log("No color conversion needed.")
            
        log("Running easyocr reader.readtext...")
        res = reader.readtext(img_cv)
        log(f"readtext finished! Results found: {len(res)}")
        if res:
            log(f"First result: {res[0]}")
            
    except Exception as e:
        log(f"Error during test: {e}")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    test()
