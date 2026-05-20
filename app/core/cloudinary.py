import cloudinary
import cloudinary.uploader
from app.core.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_profile_picture(file_bytes: bytes, user_id: int) -> str:
    """Upload a profile picture to Cloudinary and return the secure URL.

    Uses overwrite=True so each user always has exactly one image stored —
    uploading a new photo automatically replaces the previous one.
    """
    result = cloudinary.uploader.upload(
        file_bytes,
        folder="terraform/profile_pictures",
        public_id=f"user_{user_id}",
        overwrite=True,
        resource_type="image",
        transformation=[
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
            {"quality": "auto", "fetch_format": "auto"},
        ],
    )
    return result["secure_url"]


def delete_profile_picture(user_id: int) -> None:
    """Delete a user's profile picture from Cloudinary."""
    cloudinary.uploader.destroy(
        f"terraform/profile_pictures/user_{user_id}",
        resource_type="image",
    )
