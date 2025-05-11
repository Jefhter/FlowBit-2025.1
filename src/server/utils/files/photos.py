from pathlib import Path
import io
from.io import write
from PIL import Image

def realize_image(
    photo: str|bytes|Path,
    width: int, 
    height: int, 
    mode: str = 'RGB',
    remove_original: bool = True,
    new_path: str|Path|None = None, 
    ignore_errors=False
) -> Path|bytes|None:
    try:
        with Image.open(photo) as image:
            img = image.convert(mode).resize((width, height))
            format_img = Path(new_path).suffix if new_path else image.format or 'PNG'

            img_file = io.BytesIO()
            img.save(img_file, format=format_img) 
            img_file.seek(0)
            img_bytes = img_file.getvalue()

        if new_path:
            result = write(new_path, img_bytes, binary=True)
        elif isinstance(photo, (str,Path)) and remove_original:
            result =  write(photo, img_bytes, binary=True)
        else:
            result = img_bytes

        if remove_original and isinstance(photo, (str, Path)):
            Path(photo).unlink()

        return result

    except Exception as e:
        if not ignore_errors:
            raise e
        return None


