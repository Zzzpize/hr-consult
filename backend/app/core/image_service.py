from PIL import Image
import io
import os

BASE_PATH = "/app/frontend/static/icons"

def process_image(icon_name: str, grayscale: bool = False):
    """
    Открывает изображение, опционально обесцвечивает его
    и возвращает в виде байтового потока.
    """
    image_path = os.path.join(BASE_PATH, icon_name)
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            if grayscale:
                processed_img = img.convert('L').convert('RGBA')
            else:
                processed_img = img
            img_byte_arr = io.BytesIO()
            processed_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Icon not found at absolute container path: {image_path}")
        return None