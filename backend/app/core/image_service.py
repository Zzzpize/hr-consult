from PIL import Image, ImageOps
import io

def process_image(image_path: str, grayscale: bool = False):
    """
    Открывает изображение, опционально обесцвечивает его
    и возвращает в виде байтового потока.
    """
    try:
        with Image.open(image_path) as img:
            if grayscale:
                processed_img = img.convert('L')
            else:
                processed_img = img
            img_byte_arr = io.BytesIO()
            processed_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0) 
            return img_byte_arr
    except FileNotFoundError:
        return None