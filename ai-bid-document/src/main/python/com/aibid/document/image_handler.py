"""图片处理模块 - Word导出图片支持"""
import io
import os
import re
import logging
import shutil
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import base64

logger = logging.getLogger(__name__)

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".svg", ".bmp", ".gif"}
# Word中图片的默认大小（英寸）
DEFAULT_IMAGE_WIDTH = 6.0
DEFAULT_IMAGE_HEIGHT = None  # None表示按比例


class ImageHandler:
    """图片处理器 - 处理Word文档中的图片"""

    def __init__(self, output_dir: str = "/tmp/word_output"):
        self.output_dir = output_dir
        self.image_dir = os.path.join(output_dir, "media")
        self.image_map: Dict[str, str] = {}  # original_path -> output_path
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)

    def process_markdown_images(
        self,
        markdown_content: str,
        output_subdir: str = ""
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """处理Markdown中的图片引用

        Args:
            markdown_content: 包含图片引用的Markdown文本
            output_subdir: 输出子目录（如项目名）

        Returns:
            处理后的Markdown（图片路径替换为相对路径）, 图片元数据列表
        """
        image_metadata = []
        processed_content = markdown_content

        # 匹配Markdown图片语法 ![alt](url)
        image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

        for match in image_pattern.finditer(markdown_content):
            alt_text = match.group(1)
            image_ref = match.group(2)

            # 跳过chart:和table:标记（由其他模块处理）
            if image_ref.startswith("chart:") or image_ref.startswith("table:"):
                continue

            # 处理图片
            result = self._process_single_image(image_ref, alt_text, output_subdir)
            if result:
                new_ref, metadata = result
                processed_content = processed_content.replace(match.group(0),
                                                             f"![{alt_text}]({new_ref})")
                image_metadata.append(metadata)

        return processed_content, image_metadata

    def _process_single_image(
        self,
        image_ref: str,
        alt_text: str,
        subdir: str
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """处理单个图片引用

        Args:
            image_ref: 图片引用（URL或本地路径）
            alt_text: 图片说明文字
            subdir: 子目录

        Returns:
            (新引用路径, 元数据) 或 None
        """
        try:
            # 确定目标目录
            target_dir = self.image_dir
            if subdir:
                target_dir = os.path.join(self.image_dir, subdir)
                os.makedirs(target_dir, exist_ok=True)

            # 下载或读取图片
            if image_ref.startswith("http://") or image_ref.startswith("https://"):
                image_data = self._download_image(image_ref)
            else:
                image_data = self._read_local_image(image_ref)

            if image_data is None:
                logger.warning(f"Cannot load image: {image_ref}")
                return None

            # 生成唯一文件名
            ext = self._get_extension(image_ref, image_data)
            filename = self._generate_filename(alt_text, ext)
            output_path = os.path.join(target_dir, filename)

            # 保存图片
            with open(output_path, "wb") as f:
                f.write(image_data)

            # 相对路径（相对于output_dir）
            relative_path = os.path.join("media", subdir if subdir else "", filename)
            relative_path = relative_path.replace("\\", "/")

            metadata = {
                "original_ref": image_ref,
                "output_path": output_path,
                "relative_path": relative_path,
                "filename": filename,
                "alt_text": alt_text,
                "size_bytes": len(image_data)
            }

            logger.info(f"Image processed: {image_ref} -> {relative_path}")
            return relative_path, metadata

        except Exception as e:
            logger.error(f"Failed to process image {image_ref}: {e}")
            return None

    def _download_image(self, url: str) -> Optional[bytes]:
        """下载网络图片"""
        import httpx
        try:
            with httpx.Client(timeout=15) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            return None

    def _read_local_image(self, path: str) -> Optional[bytes]:
        """读取本地图片"""
        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read()
            return None
        except Exception as e:
            logger.warning(f"Failed to read local image {path}: {e}")
            return None

    def _get_extension(self, ref: str, data: bytes) -> str:
        """从引用和数据中推断文件扩展名"""
        # 尝试从URL/路径提取扩展名
        if "." in ref:
            ext = "." + ref.rsplit(".", 1)[-1].lower()
            if ext in SUPPORTED_IMAGE_FORMATS:
                return ext

        # 尝试从文件头检测图片类型
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return ".png"
        elif data[:2] == b"\xff\xd8":
            return ".jpg"
        elif data[:5] == b"GIF87" or data[:5] == b"GIF89":
            return ".gif"
        elif data[:2] == b"BM":
            return ".bmp"
        elif b"<svg" in data[:1000]:
            return ".svg"

        return ".png"  # 默认PNG

    def _generate_filename(self, alt_text: str, ext: str) -> str:
        """生成唯一文件名"""
        # 基于alt文本生成友好的文件名
        safe_name = re.sub(r"[^\w\u4e00-\u9fa5]+", "_", alt_text)[:50]
        safe_name = safe_name.strip("_")

        if not safe_name:
            safe_name = "image"

        # 添加短哈希确保唯一性
        hash_suffix = hashlib.md5(alt_text.encode()).hexdigest()[:6]
        return f"{safe_name}_{hash_suffix}{ext}"

    def copy_images_to_output(
        self,
        source_paths: List[str],
        output_dir: str,
        preserve_structure: bool = True
    ) -> Dict[str, str]:
        """复制图片到Word输出目录

        Args:
            source_paths: 源图片路径列表
            output_dir: 目标目录
            preserve_structure: 是否保留目录结构

        Returns:
            source -> dest 映射
        """
        mapping = {}

        # 创建media子目录
        media_dir = os.path.join(output_dir, "media")
        os.makedirs(media_dir, exist_ok=True)

        for source in source_paths:
            try:
                if not os.path.exists(source):
                    continue

                filename = os.path.basename(source)
                dest = os.path.join(media_dir, filename)

                # 如果目标已存在，添加序号
                if os.path.exists(dest):
                    name, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest):
                        dest = os.path.join(media_dir, f"{name}_{counter}{ext}")
                        counter += 1

                shutil.copy2(source, dest)
                mapping[source] = dest
                logger.debug(f"Copied image: {source} -> {dest}")

            except Exception as e:
                logger.warning(f"Failed to copy image {source}: {e}")

        return mapping

    def get_image_dimensions(
        self,
        image_data: bytes
    ) -> Tuple[Optional[float], Optional[float]]:
        """获取图片尺寸（英寸）"""
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_data))
            width_px, height_px = img.size

            # 假设72 DPI
            width_inches = width_px / 72.0
            height_inches = height_px / 72.0

            return width_inches, height_inches
        except Exception as e:
            logger.warning(f"Failed to get image dimensions: {e}")
            return None, None

    def resize_image_to_fit(
        self,
        image_data: bytes,
        max_width: float = 6.0,
        max_height: float = 4.0
    ) -> bytes:
        """调整图片大小以适应指定尺寸

        Args:
            image_data: 原始图片数据
            max_width: 最大宽度（英寸）
            max_height: 最大高度（英寸）

        Returns:
            调整后的图片数据
        """
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_data))
            width_px, height_px = img.size

            # 转换为英寸（72 DPI）
            width_inches = width_px / 72.0
            height_inches = height_px / 72.0

            # 计算缩放比例
            scale_w = max_width / width_inches if width_inches > max_width else 1.0
            scale_h = max_height / height_inches if height_inches > max_height else 1.0
            scale = min(scale_w, scale_h)

            if scale < 1.0:
                new_width = int(width_px * scale)
                new_height = int(height_px * scale)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            # 保存
            output = io.BytesIO()
            img_format = img.format or "PNG"
            img.save(output, format=img_format)
            output.seek(0)
            return output.read()

        except Exception as e:
            logger.warning(f"Failed to resize image: {e}")
            return image_data

    def cleanup_temp_images(self):
        """清理临时图片文件"""
        try:
            if os.path.exists(self.image_dir):
                shutil.rmtree(self.image_dir)
                os.makedirs(self.image_dir, exist_ok=True)
                logger.info("Cleaned up temp images")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp images: {e}")


# ============================================================
# 全局单例
# ============================================================

_image_handler: Optional[ImageHandler] = None


def get_image_handler(output_dir: Optional[str] = None) -> ImageHandler:
    """获取图片处理器实例"""
    global _image_handler
    if _image_handler is None or output_dir:
        _image_handler = ImageHandler(output_dir=output_dir or "/tmp/word_output")
    return _image_handler