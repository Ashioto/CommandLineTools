import os
import glob
import argparse
from PIL import Image
import imagehash

def get_image_paths(root_dir):
    """使用glob递归获取所有图片路径"""
    # 支持的图片格式（可根据需要扩展）
    image_extensions = [
        '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp',
        '*.webp', '*.tiff', '*.jfif', '*.heic',
        '*.JPG', '*.PNG', '*.WEBP'  # 大小写兼容
    ]
    
    all_images = []
    for ext in image_extensions:
        # 递归匹配所有子文件夹中的图片
        pattern = os.path.join(root_dir, '**', ext)
        images = glob.glob(pattern, recursive=True)
        all_images.extend(images)
    
    # 去重并返回绝对路径
    return list(set(os.path.abspath(img) for img in all_images))

def calculate_image_hash(image_path, hash_size=8):
    """计算图片的感知哈希值"""
    try:
        with Image.open(image_path) as img:
            # 转换为灰度图并计算哈希
            return imagehash.phash(img, hash_size=hash_size)
    except Exception as e:
        print(f"警告：无法处理图片 {image_path} - {str(e)}")
        return None

def find_similar_images(root_dir, threshold=5, hash_size=8):
    """查找相似图片（哈希差异小于等于阈值）"""
    # 获取所有图片路径
    image_paths = get_image_paths(root_dir)
    if not image_paths:
        print("未找到任何图片文件")
        return
    
    print(f"发现 {len(image_paths)} 张图片，开始计算哈希值...")
    
    # 计算所有图片的哈希值（过滤无效图片）
    image_hashes = {}
    for path in image_paths:
        img_hash = calculate_image_hash(path, hash_size)
        if img_hash:
            image_hashes[path] = img_hash
    
    print(f"有效图片：{len(image_hashes)} 张，开始检测相似图片...")
    
    # 比较所有图片对的哈希差异
    similar_pairs = []
    paths = list(image_hashes.keys())
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            path1 = paths[i]
            path2 = paths[j]
            
            # 计算哈希差异（汉明距离）
            hash_diff = image_hashes[path1] - image_hashes[path2]
            
            if hash_diff <= threshold:
                similar_pairs.append((path1, path2, hash_diff))
    
    return similar_pairs

def main():
    # 命令行参数配置
    parser = argparse.ArgumentParser(
        description="检测文件夹中相似的图片（支持子文件夹）",
        epilog="示例: python similar_images.py /path/to/images --threshold 3"
    )
    parser.add_argument("directory", help="图片所在的根目录")
    parser.add_argument(
        "--threshold", 
        type=int, 
        default=5, 
        help="哈希差异阈值（越小越严格，默认5）"
    )
    parser.add_argument(
        "--hash-size", 
        type=int, 
        default=8, 
        help="哈希计算尺寸（默认8，值越大精度越高但速度越慢）"
    )
    
    args = parser.parse_args()
    
    # 验证目录
    if not os.path.isdir(args.directory):
        print(f"错误：目录 '{args.directory}' 不存在")
        return
    
    # 查找相似图片
    similar_pairs = find_similar_images(
        root_dir=args.directory,
        threshold=args.threshold,
        hash_size=args.hash_size
    )
    
    # 输出结果
    if similar_pairs:
        print(f"\n发现 {len(similar_pairs)} 组相似图片：")
        for i, (path1, path2, diff) in enumerate(similar_pairs, 1):
            print(f"\n组 {i}（差异值：{diff}）:")
            print(f"  {path1}")
            print(f"  {path2}")
    else:
        print("\n未发现相似图片")

if __name__ == "__main__":
    # 需安装依赖：pip install pillow imagehash
    main()
    