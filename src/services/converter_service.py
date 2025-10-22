"""
WebP转换服务

提供图片到WebP格式的转换功能,支持质量控制、元数据保留和取消机制。
"""

import time
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, UnidentifiedImageError

from src.models.image_file import ImageFile
from src.models.conversion_task import ConversionTask, TaskStatus
from src.services.metadata_service import MetadataService


@dataclass
class ConversionResult:
    """转换结果"""
    success: bool
    output_path: Optional[Path] = None
    output_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    duration: float = 0.0
    error_message: Optional[str] = None


class ConverterService:
    """WebP转换服务"""

    def __init__(self):
        self.metadata_service = MetadataService()

    def convert_image(
        self,
        input_file: ImageFile,
        output_path: Path,
        quality: int,
        preserve_metadata: bool = True,
        stop_event: Optional[threading.Event] = None
    ) -> ConversionResult:
        """
        将单张图片转换为WebP格式

        Args:
            input_file: 输入图片文件对象
            output_path: 输出WebP文件路径
            quality: 质量参数 (0-100)
            preserve_metadata: 是否保留元数据
            stop_event: 取消标志

        Returns:
            ConversionResult对象
        """
        start_time = time.time()

        # 检查取消标志
        if stop_event and stop_event.is_set():
            return ConversionResult(
                success=False,
                error_message="转换已取消",
                duration=time.time() - start_time
            )

        # 验证质量参数
        if not (0 <= quality <= 100):
            return ConversionResult(
                success=False,
                error_message=f"质量参数必须在0-100范围内,当前值: {quality}",
                duration=time.time() - start_time
            )

        # 验证输入文件
        if not input_file.is_valid:
            is_valid, error_msg = input_file.validate()
            return ConversionResult(
                success=False,
                error_message=error_msg,
                duration=time.time() - start_time
            )

        try:
            import sys
            print(f"[CONVERT] 打开图片: {input_file.file_path}", file=sys.stderr)

            # 打开图片
            with Image.open(input_file.file_path) as img:
                print(f"[CONVERT] 图片已打开: {img.mode}, {img.size}", file=sys.stderr)

                # 检查取消标志
                if stop_event and stop_event.is_set():
                    return ConversionResult(
                        success=False,
                        error_message="转换已取消",
                        duration=time.time() - start_time
                    )

                # 提取元数据
                metadata = None
                if preserve_metadata:
                    print(f"[CONVERT] 提取元数据...", file=sys.stderr)
                    metadata = self.metadata_service.extract_metadata(img)
                    print(f"[CONVERT] 元数据提取完成", file=sys.stderr)

                # 转换为RGB模式(WebP不支持P模式)
                if img.mode in ('P', 'RGBA', 'LA'):
                    print(f"[CONVERT] 转换颜色模式: {img.mode}", file=sys.stderr)
                    if img.mode == 'P':
                        img = img.convert('RGB')
                    elif img.mode in ('RGBA', 'LA'):
                        # 保留透明度
                        pass

                # 准备保存参数
                # method=4是质量和速度的平衡点（0-6，6最慢但质量最好）
                # 对于大文件使用method=4避免过长等待时间
                save_params = {
                    'format': 'WEBP',
                    'quality': quality,
                    'method': 4  # 平衡质量和速度
                }
                print(f"[CONVERT] 保存参数: {save_params}", file=sys.stderr)

                # 嵌入元数据
                if preserve_metadata and metadata and metadata.has_metadata:
                    print(f"[CONVERT] 嵌入元数据...", file=sys.stderr)
                    metadata_params = self.metadata_service.embed_metadata(metadata)
                    save_params.update(metadata_params)

                # 检查取消标志
                if stop_event and stop_event.is_set():
                    return ConversionResult(
                        success=False,
                        error_message="转换已取消",
                        duration=time.time() - start_time
                    )

                # 保存为WebP
                print(f"[CONVERT] 开始保存WebP: {output_path}", file=sys.stderr)
                img.save(output_path, **save_params)
                print(f"[CONVERT] WebP保存完成", file=sys.stderr)

            # 计算输出文件大小和压缩比
            output_size = output_path.stat().st_size
            compression_ratio = (1 - output_size / input_file.file_size) * 100

            duration = time.time() - start_time

            return ConversionResult(
                success=True,
                output_path=output_path,
                output_size=output_size,
                compression_ratio=round(compression_ratio, 2),
                duration=duration
            )

        except FileNotFoundError:
            return ConversionResult(
                success=False,
                error_message="图片文件不存在",
                duration=time.time() - start_time
            )
        except UnidentifiedImageError:
            return ConversionResult(
                success=False,
                error_message="不支持的文件格式",
                duration=time.time() - start_time
            )
        except MemoryError:
            return ConversionResult(
                success=False,
                error_message="内存不足,无法处理此图片",
                duration=time.time() - start_time
            )
        except PermissionError:
            return ConversionResult(
                success=False,
                error_message="无权限写入文件",
                duration=time.time() - start_time
            )
        except OSError as e:
            if "No space left on device" in str(e):
                return ConversionResult(
                    success=False,
                    error_message="磁盘空间不足,无法保存转换后的文件",
                    duration=time.time() - start_time
                )
            return ConversionResult(
                success=False,
                error_message=f"文件系统错误: {str(e)}",
                duration=time.time() - start_time
            )
        except Exception as e:
            return ConversionResult(
                success=False,
                error_message=f"转换失败: {str(e)}",
                duration=time.time() - start_time
            )

    def batch_convert(
        self,
        tasks: list[ConversionTask],
        max_workers: int = 3,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        stop_event: Optional[threading.Event] = None
    ) -> list[ConversionResult]:
        """
        批量转换多张图片

        Args:
            tasks: 转换任务列表
            max_workers: 最大并发数
            progress_callback: 进度回调函数 (completed_count, total_count)
            stop_event: 取消标志

        Returns:
            转换结果列表,与tasks顺序对应
        """
        if not tasks:
            return []

        total_count = len(tasks)
        results = [None] * total_count  # 预分配结果列表
        completed_count = 0
        lock = threading.Lock()

        def convert_single_task(index: int, task: ConversionTask) -> tuple[int, ConversionResult]:
            """转换单个任务并返回索引和结果"""
            nonlocal completed_count

            # 检查取消标志
            if stop_event and stop_event.is_set():
                result = ConversionResult(
                    success=False,
                    error_message="转换已取消",
                    duration=0.0
                )
                with lock:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_count)
                return index, result

            # 执行转换
            result = self.convert_image(
                input_file=task.input_file,
                output_path=task.output_path,
                quality=task.quality,
                preserve_metadata=task.preserve_metadata,
                stop_event=stop_event
            )

            # 更新进度
            with lock:
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, total_count)

            return index, result

        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {
                executor.submit(convert_single_task, i, task): i
                for i, task in enumerate(tasks)
            }

            # 收集结果
            for future in as_completed(futures):
                index, result = future.result()
                results[index] = result

                # 如果设置了取消标志,取消后续任务
                if stop_event and stop_event.is_set():
                    # 取消未完成的任务
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    break

        # 填充被取消的任务结果
        for i, result in enumerate(results):
            if result is None:
                results[i] = ConversionResult(
                    success=False,
                    error_message="转换已取消",
                    duration=0.0
                )

        return results
