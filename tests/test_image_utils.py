from io import BytesIO

from PIL import Image

from jewel_db.services.image_utils import normalise_image


def test_image_is_resized_to_max_1600_px():
    # create a 3000 × 2000 red JPEG in-memory
    buf = BytesIO()
    Image.new("RGB", (3000, 2000), (255, 0, 0)).save(buf, format="JPEG")
    buf.seek(0)

    out_bytes, _ext = normalise_image(buf.getvalue(), mime="image/jpeg")
    img = Image.open(BytesIO(out_bytes))

    assert max(img.size) <= 1600
