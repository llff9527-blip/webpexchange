# ConverterService 服务契约

**服务名称**: ConverterService (WebP转换核心服务)
**职责**: 执行图片到WebP格式的转换,管理转换参数和元数据保留
**位置**: `src/services/converter_service.py`

---

## 接口定义

### convert_image()

**功能**: 将单张图片转换为WebP格式,支持质量参数和元数据保留。

**签名**:
```python
def convert_image(
    input_file: ImageFile,
    output_path: Path,
    quality: int,
    preserve_metadata: bool = True,
    stop_event: threading.Event | None = None
) -> ConversionResult
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|-------|------|------|------|------|
| `input_file` | `ImageFile` | ✅ | 输入图片文件对象 | 必须已验证(`is_valid=True`) |
| `output_path` | `Path` | ✅ | 输出WebP文件路径 | 父目录必须存在且可写 |
| `quality` | `int` | ✅ | 有损压缩质量参数 | 范围[0, 100] |
| `preserve_metadata` | `bool` | - | 是否保留元数据 | 默认`True` |
| `stop_event` | `threading.Event` \| `None` | - | 取消标志 | 周期性检查`is_set()` |

**返回值**: `ConversionResult`

```python
@dataclass
class ConversionResult:
    success: bool                    # 是否成功
    output_path: Path | None         # 输出文件路径(成功时)
    output_size: int | None          # 输出文件大小(字节,成功时)
    compression_ratio: float | None  # 压缩比(百分比,成功时)
    duration: float                  # 转换耗时(秒)
    error_message: str | None        # 错误信息(失败时)
```

**前置条件**:
- `input_file.is_valid == True`
- `0 <= quality <= 100`
- `output_path.parent.exists() == True`

**后置条件**:
- 成功时: `output_path`存在,`output_size > 0`
- 失败时: `success=False`, `error_message`包含中文错误描述
- 取消时: `success=False`, `error_message="转换已取消"`

**异常**:

| 异常类型 | 触发条件 | 处理策略 |
|---------|---------|---------|
| `FileNotFoundError` | 输入文件不存在 | 捕获并返回`success=False`, `error_message="图片文件不存在"` |
| `UnidentifiedImageError` | 文件格式无法识别 | 捕获并返回`error_message="不支持的文件格式"` |
| `MemoryError` | 图片解码内存不足 | 捕获并返回`error_message="内存不足,无法处理此图片"` |
| `PermissionError` | 输出路径无写权限 | 捕获并返回`error_message="无权限写入文件"` |
| `OSError` (磁盘已满) | 磁盘空间不足 | 捕获并返回`error_message="磁盘空间不足,无法保存转换后的文件"` |

**性能要求**:
- 10MB图片: 耗时 < 5秒 (对应`spec.md` SC-003)
- 转换过程中每秒至少检查一次`stop_event`(支持1秒内响应取消)

**示例用法**:
```python
# 基础转换
result = converter_service.convert_image(
    input_file=image_file,
    output_path=Path("output.webp"),
    quality=80
)

if result.success:
    print(f"转换成功,压缩比: {result.compression_ratio:.1f}%")
else:
    print(f"转换失败: {result.error_message}")

# 支持取消的转换
stop_event = threading.Event()
result = converter_service.convert_image(
    input_file=image_file,
    output_path=Path("output.webp"),
    quality=80,
    stop_event=stop_event
)

# 另一线程中触发取消
stop_event.set()
```

---

### batch_convert()

**功能**: 批量转换多张图片,支持并发控制和整体进度跟踪。

**签名**:
```python
def batch_convert(
    tasks: list[ConversionTask],
    max_workers: int = 3,
    progress_callback: Callable[[int, int], None] | None = None,
    stop_event: threading.Event | None = None
) -> list[ConversionResult]
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|-------|------|------|------|------|
| `tasks` | `list[ConversionTask]` | ✅ | 转换任务列表 | 长度 > 0 |
| `max_workers` | `int` | - | 最大并发数 | 默认3,范围[1, 10] |
| `progress_callback` | `Callable[[int, int], None]` \| `None` | - | 进度回调函数 | 参数为(已完成数, 总数) |
| `stop_event` | `threading.Event` \| `None` | - | 取消标志 | 设置后停止后续任务 |

**返回值**: `list[ConversionResult]` (与`tasks`顺序对应)

**前置条件**:
- `len(tasks) > 0`
- `1 <= max_workers <= 10`
- 所有任务的`input_file.is_valid == True`

**后置条件**:
- 返回列表长度 == `len(tasks)`
- 取消后,未开始任务的`result.success=False`, `error_message="转换已取消"`

**行为规范**:
1. 使用`ThreadPoolExecutor(max_workers=max_workers)`并发执行
2. 每完成一个任务,调用`progress_callback(completed_count, total_count)`
3. 检查`stop_event`,如已设置则取消所有未开始的任务
4. 已完成的转换文件保留,不删除

**性能要求**:
- 批量转换10张图片(每张5MB): 总耗时 < 60秒 (对应`spec.md` SC-007)

**示例用法**:
```python
tasks = [
    ConversionTask(input_file=file1, output_path=path1, quality=80),
    ConversionTask(input_file=file2, output_path=path2, quality=80),
    # ...
]

def on_progress(completed, total):
    print(f"进度: {completed}/{total}")

results = converter_service.batch_convert(
    tasks=tasks,
    max_workers=3,
    progress_callback=on_progress
)

for task, result in zip(tasks, results):
    if result.success:
        print(f"{task.input_file.file_name}: 成功")
    else:
        print(f"{task.input_file.file_name}: 失败 - {result.error_message}")
```

---

## 依赖

### 内部依赖
- `models.ImageFile`: 输入文件对象
- `models.ConversionTask`: 任务对象
- `models.ImageMetadata`: 元数据对象
- `services.MetadataService`: 元数据提取/嵌入服务
- `services.FileService`: 文件路径处理

### 外部依赖
- `Pillow >= 10.0.0`: 图片处理和WebP编码
- `threading`: 取消标志
- `concurrent.futures.ThreadPoolExecutor`: 批量转换并发控制

---

## 测试契约

### 单元测试

**测试用例**:
1. `test_convert_image_success`: 验证成功转换,检查`output_path`存在和`compression_ratio`计算正确
2. `test_convert_image_invalid_quality`: 传入`quality=150`,验证返回`success=False`
3. `test_convert_image_file_not_found`: 输入文件不存在,验证错误消息为"图片文件不存在"
4. `test_convert_image_preserve_metadata`: 转换前后EXIF数据一致
5. `test_convert_image_cancelled`: 设置`stop_event`,验证返回`error_message="转换已取消"`
6. `test_batch_convert_success`: 转换3张图片,验证返回3个结果
7. `test_batch_convert_progress_callback`: 验证进度回调被正确调用3次(0/3, 1/3, 2/3, 3/3)
8. `test_batch_convert_cancelled_mid_way`: 转换5张图片,完成2张后取消,验证后3张状态为"转换已取消"

### 集成测试

**测试用例**:
1. `test_end_to_end_conversion_workflow`: 完整流程测试(选择文件→转换→验证输出)
2. `test_large_image_conversion`: 测试200MB图片,验证内存管理和性能

---

## 版本历史

- v1.0.0 (2025-10-21): 初始契约定义
