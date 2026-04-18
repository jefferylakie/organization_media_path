import os
import shutil
from pathlib import Path
from datetime import datetime

# 图片处理
from PIL import Image
import pillow_heif

# 视频处理
from pymediainfo import MediaInfo

# ================= 配置区域 =================
SOURCE_DIR = r"D:\MyPhotos"
# ===========================================

# 注册 HEIC 支持
pillow_heif.register_heif_opener()

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.heic', '.heif', '.tiff', '.bmp', '.webp', '.tif', '.dng')
VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.m4v', '.3gp')

MIN_VALID_DATE = datetime(2000, 1, 1)


def parse_datetime(dt_str):
    """清洗并解析时间字符串 (处理 MediaInfo 的 UTC/T 格式)"""
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
    获取图片时间
    优先级：DateTimeOriginal (36867) > DateTime (306) > 文件修改时间
    """
    try:
        with Image.open(img_path) as im:
            exif = im.getexif()
            if exif:
                # 尝试获取 DateTimeOriginal (36867)
                date_str = exif.get(36867)
                if not date_str:
                    # 如果没有 Original，尝试获取 DateTime (306)
                    date_str = exif.get(306)

                if date_str:
                    try:
                        dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                        if dt >= MIN_VALID_DATE:
                            return dt
                    except ValueError:
                        pass

            # 最后的保底：文件系统的修改时间
            return datetime.fromtimestamp(os.path.getmtime(img_path))

    except Exception as e:
        return datetime.fromtimestamp(os.path.getmtime(img_path))


def get_video_date(video_path):
    """
    获取视频时间
    策略：锁定 encoded_date (编码日期)
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

    # 最后的保底：文件系统修改时间
    return datetime.fromtimestamp(os.path.getmtime(video_path))


def organize_all_media(source_folder):
    source_path = Path(source_folder)
    if not source_path.exists():
        print(f"❌ 错误：目录 '{source_folder}' 不存在！")
        return

    # 使用 rglob 递归查找所有文件
    all_files = source_path.rglob('*')
    processed_count = 0
    skipped_count = 0

    print(f"开始整理 (保留原始文件名)...")

    for file_path in all_files:
        if file_path.is_file():
            suffix = file_path.suffix.lower()
            file_date = None

            # 1. 判断文件类型并获取日期
            if suffix in IMAGE_EXTS:
                file_date = get_image_date(file_path)
            elif suffix in VIDEO_EXTS:
                file_date = get_video_date(file_path)
            else:
                continue  # 跳过不支持的格式

            if not file_date:
                continue

            # 2. 构建目标目录：年/月
            year = file_date.strftime("%Y")
            month = file_date.strftime("%m")
            target_dir = source_path / year / month

            # 如果目录不存在则创建
            target_dir.mkdir(parents=True, exist_ok=True)

            # 3. 构建目标路径：目录 + 原始文件名
            target_path = target_dir / file_path.name

            # 4. 只有当源路径和目标路径不一致时才移动
            # resolve() 用于处理相对路径和绝对路径的比较
            if file_path.resolve() != target_path.resolve():

                # 简单的同名检查（如果不希望覆盖，可以在这里加逻辑，比如跳过或重命名）
                if target_path.exists():
                    print(f"跳过 (目标文件已存在): {file_path}")
                    skipped_count += 1
                    continue

                try:
                    shutil.move(str(file_path), str(target_path))
                    print(f"移动: [{suffix}] {file_path.name} -> {year}/{month}/")
                    processed_count += 1
                except Exception as e:
                    print(f"移动失败: {file_path} (错误: {e})")

    print("\n" + "=" * 30)
    print(f"整理完成！")
    print(f"成功移动: {processed_count} 个文件")
    print(f"跳过/重复: {skipped_count} 个文件")
    print("=" * 30)


if __name__ == "__main__":
    organize_all_media(SOURCE_DIR)