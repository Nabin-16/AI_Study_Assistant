import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import io
import numpy as np
from PIL import Image
import easyocr

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _reader


def extract_text_from_image(image_path):
    reader = _get_reader()
    results = reader.readtext(str(image_path))
    extracted_lines = [text for (_, text, _) in results]
    return "\n".join(extracted_lines)


def extract_text_from_image_bytes(image_bytes):
    reader = _get_reader()
    # Convert raw bytes to RGB image numpy array for robust decoding
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(img)
    results = reader.readtext(img_np)
    extracted_lines = [text for (_, text, _) in results]
    return "\n".join(extracted_lines)
