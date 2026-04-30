
import os
import sys
import json
import logging
from pathlib import Path
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("extract_structure")

# Import PaddleOCR with fallback logic
try:
    from paddleocr import PPStructure
    MODEL_CLASS = PPStructure
except ImportError:
    try:
        from paddleocr import PPStructureV2
        MODEL_CLASS = PPStructureV2
    except ImportError:
        try:
             # Manual import for some versions
             from paddleocr.ppstructure.predict_system import PPStructureSystem
             MODEL_CLASS = PPStructureSystem
        except ImportError:
             logger.error("❌ Could not import PPStructure. Please check paddleocr installation.")
             sys.exit(1)

class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def extract_to_json(pdf_path, output_json_path):
    logger.info(f"Initializing {MODEL_CLASS.__name__}...")
    
    # Initialize engine
    # layout=True (default), table=True (default)
    # recovery=True to get docx/markdown structure
    engine = MODEL_CLASS(
        show_log=True, 
        image_orientation=True,
        lang='en',
        layout=True,
        table=True,
        ocr=True,
        recovery=True # Important for order
    )
    
    logger.info(f"Processing {pdf_path}...")
    result = engine(pdf_path)
    
    # result is a list (pages) of list (regions)
    # We want to serialize this
    
    # Depending on version, result might be slightly different
    # But typically it's clean enough to dump
    
    logger.info(f"Saving to {output_json_path}...")
    with open(output_json_path, 'w') as f:
        json.dump(result, f, cls=NumpyEncoder, indent=2, ensure_ascii=False)
        
    logger.info("✅ Done.")
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Auto-detect latest upload
        web_uploads = Path("web/uploads")
        if not web_uploads.exists():
            import tempfile
            web_uploads = Path(tempfile.gettempdir()) / "paper2latex_web" / "uploads"
        
        pdfs = list(web_uploads.glob("*.pdf"))
        if not pdfs:
            print("No PDF provided or found.")
            sys.exit(1)
        pdf_path = str(pdfs[0])

    output_json = "paddle_output.json"
    extract_to_json(pdf_path, output_json)
