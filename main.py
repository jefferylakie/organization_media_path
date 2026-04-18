import os
import shutil
from pathlib import Path
from datetime import datetime

# Image library
from PIL import Image
import pillow_heif

# Video library
from pymediainfo import MediaInfo

# =========== Configuration =================
SOURCE_DIR = r"D:\MyPhotos"
# ===========================================

# HEIC
pillow_heif.register_heif_opener()

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.heic', '.heif', '.tiff', '.bmp', '.webp', '.tif', '.dng')
VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.m4v', '.3gp')

MIN_VALID_DATE = datetime(2000, 1, 1)


def parse_datetime(dt_str):
    if not dt_str:
        return None

    clean_str = dt_str.replace(' UTC', '').replace(' GMT', '').replace(' UT', '').strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(clean_str, fmt)
        except ValueError:
            continue
    return None


def get_image_date(img_path):
    """
    Get image creation date.
    """
    try:
        with Image.open(img_path) as im:
            exif = im.getexif()
            if exif:
                date_str = exif.get(36867)
                if not date_str:
                    date_str = exif.get(306)

                if date_str:
                    try:
                        dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                        if dt >= MIN_VALID_DATE:
                            return dt
                    except ValueError:
                        pass

            return datetime.fromtimestamp(os.path.getmtime(img_path))

    except Exception as e:
        return datetime.fromtimestamp(os.path.getmtime(img_path))


def get_video_date(video_path):
    """
    Get video creation date.
    """
    try:
        mediainfo = MediaInfo.parse(video_path)

        for track in mediainfo.tracks:
            if track.track_type in ['General', 'Video']:
                dt = parse_datetime(track.encoded_date)
                if dt and dt >= MIN_VALID_DATE:
                    return dt
    except Exception as e:
        pass

    return datetime.fromtimestamp(os.path.getmtime(video_path))


def organize_all_media(source_folder):
    source_path = Path(source_folder)
    if not source_path.exists():
        print(f"Error: '{source_folder}' does not exist.")
        return

    all_files = source_path.rglob('*')
    processed_count = 0
    skipped_count = 0

    print(f"Starting...")

    for file_path in all_files:
        if file_path.is_file():
            suffix = file_path.suffix.lower()
            file_date = None

            if suffix in IMAGE_EXTS:
                file_date = get_image_date(file_path)
            elif suffix in VIDEO_EXTS:
                file_date = get_video_date(file_path)
            else:
                continue

            if not file_date:
                continue

            # Create directory.
            year = file_date.strftime("%Y")
            month = file_date.strftime("%m")
            target_dir = source_path / year / month
            target_dir.mkdir(parents=True, exist_ok=True)

            # Destination path.
            target_path = target_dir / file_path.name

            # Move only when the source path and the destination path are different
            if file_path.resolve() != target_path.resolve():
                if target_path.exists():
                    print(f"Skip: {file_path}")
                    skipped_count += 1
                    continue

                try:
                    shutil.move(str(file_path), str(target_path))
                    print(f"Move: [{suffix}] {file_path.name} -> {year}/{month}/")
                    processed_count += 1
                except Exception as e:
                    print(f"Move failed: {file_path} (Error: {e})")

    print("\n" + "=" * 30)
    print(f"Completed!")
    print(f"Moved: {processed_count} files.")
    print(f"Skiped: {skipped_count} files.")
    print("=" * 30)


if __name__ == "__main__":
    organize_all_media(SOURCE_DIR)
