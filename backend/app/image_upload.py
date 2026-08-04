"""
Cloudinary upload helper. Product photos go here instead of a local folder,
since a cloud/multi-device app has no single "local disk" that every
device can see - the URL Cloudinary returns gets stored on the Product
row and works from any device.
"""

import cloudinary
import cloudinary.uploader
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_product_image(file_bytes: bytes, account_id: int) -> str:
    """Uploads an image and returns its public HTTPS URL. Images are put in
    a per-shop folder so they stay organized and one shop's photos are
    never mixed up with another's in the Cloudinary dashboard."""
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=f"boutique-manager/{account_id}",
        resource_type="image",
    )
    return result["secure_url"]
