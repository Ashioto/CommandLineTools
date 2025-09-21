import os
import glob
import re
import argparse
from PIL import Image
from PIL.ExifTags import TAGS

def is_already_renamed(filename):
    """判断文件名是否已经是处理后的时间格式（如 20231005_143022.jpg）"""
    # 正则匹配：YYYYMMDD_HHMMSS.扩展名（年月日8位 + 下划线 + 时分秒6位）
    pattern = r'^\d{8}_\d{6}(_\d+)?\.\w+$'
    return re.match(pattern, filename) is not None

def get_shoot_time(image_path):
    """从图片EXIF数据提取拍摄时间"""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None
            
            exif_tags = {TAGS[key]: value for key, value in exif_data.items()}
            return exif_tags.get('DateTimeOriginal') or exif_tags.get('DateTime')
    except Exception as e:
        print(f"警告: 读取EXIF失败 {image_path}: {str(e)}")
        return None

def format_time(original_time):
    """格式化时间为文件名格式（例如 '2023:10:05 14:30:22' → '20231005_143022'）"""
    if not original_time:
        return None
    return original_time.replace(':', '').replace(' ', '_')

def rename_image(file_path, verbose=False):
    """重命名单个图片文件（跳过已处理的文件）"""
    # 提取文件名（不含路径）
    filename = os.path.basename(file_path)
    
    # 如果已经是处理后的格式，直接跳过
    if is_already_renamed(filename):
        if verbose:
            print(f"已处理，跳过: {file_path}")
        return False
    
    # 提取文件所在目录和扩展名
    dir_name = os.path.dirname(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    # 获取并格式化拍摄时间
    shoot_time = get_shoot_time(file_path)
    formatted_time = format_time(shoot_time)
    
    if not formatted_time:
        if verbose:
            print(f"无有效拍摄时间，跳过: {file_path}")
        return False
    
    # 构建新文件名
    new_filename = f"{formatted_time}{ext}"
    new_path = os.path.join(dir_name, new_filename)
    
    # 处理重名文件（仅对未处理的文件添加计数器）
    counter = 1
    while os.path.exists(new_path):
        new_filename = f"{formatted_time}_{counter}{ext}"
        new_path = os.path.join(dir_name, new_filename)
        counter += 1
    
    # 执行重命名
    os.rename(file_path, new_path)
    print(f"重命名: {filename} → {new_filename}")
    return True

def process_all_images(root_dir, verbose=False):
    """递归处理所有子目录中的图片（跳过已处理文件）"""
    # 定义需要处理的图片扩展名
    image_extensions = [
        '*.jpg', '*.jpeg', '*.png', '*.gif', 
        '*.bmp', '*.cr2', '*.nef', '*.raw',
        '*.JPG', '*.JPEG', '*.PNG', '*.GIF',
        '*.BMP', '*.CR2', '*.NEF', '*.RAW'
    ]
    
    # 递归查找所有符合条件的图片文件
    all_images = []
    for ext in image_extensions:
        pattern = os.path.join(root_dir, '**', ext)
        images = glob.glob(pattern, recursive=True)
        all_images.extend(images)
    
    # 去重
    all_images = list(set(all_images))
    total = len(all_images)
    renamed = 0
    
    # 逐个处理图片
    print(f"发现 {total} 个图片文件，开始处理...\n")
    for img_path in all_images:
        if rename_image(img_path, verbose):
            renamed += 1
    
    print(f"\n处理完成！共处理 {total} 个文件，其中 {renamed} 个被重命名。")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(
        description='根据拍摄时间重命名图片文件的工具，支持处理多层嵌套文件夹。',
        epilog='示例: python image_renamer.py /path/to/your/photos -v'
    )
    
    # 必选参数：文件夹路径
    parser.add_argument(
        'directory', 
        help='要处理的图片文件夹路径'
    )
    
    # 可选参数： verbose模式
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='显示详细处理信息，包括被跳过的文件'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 验证目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在，请检查路径是否正确。")
        return
    
    # 开始处理
    process_all_images(args.directory, args.verbose)

if __name__ == "__main__":
    main()
    