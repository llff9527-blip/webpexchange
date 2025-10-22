# MetadataService 服务契约

**服务名称**: MetadataService (元数据处理服务)
**职责**: 从图片文件中提取EXIF/XMP/ICC元数据,并在WebP转换时嵌入元数据
**位置**: `src/services/metadata_service.py`

---

## 接口定义

### extract_metadata()

**功能**: 从Pillow Image对象中提取所有可用的元数据。

**签名**:
```python
def extract_metadata(pil_image: Image.Image) -> ImageMetadata
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `pil_image` | `Image.Image` | ✅ | Pillow打开的图片对象 |

**返回值**: `ImageMetadata`对象

**行为规范**:
1. 尝试提取EXIF数据: `pil_image.info.get('exif')`
2. 尝试提取XMP数据: `pil_image.info.get('xmp')`
3. 尝试提取ICC配置文件: `pil_image.info.get('icc_profile')`
4. 如果所有元数据均不存在,返回空的`ImageMetadata`对象

**前置条件**:
- `pil_image`是有效的Pillow Image对象

**后置条件**:
- 返回的`ImageMetadata`对象不为`None`
- 如果原图无元数据,`metadata.has_metadata == False`

**异常**:
不抛出异常,缺失的元数据字段设为`None`

**示例用法**:
```python
from PIL import Image

img = Image.open("photo.jpg")
metadata = metadata_service.extract_metadata(img)

if metadata.has_metadata:
    print(f"EXIF存在: {metadata.exif is not None}")
    print(f"XMP存在: {metadata.xmp is not None}")
```

---

### embed_metadata()

**功能**: 将元数据嵌入到WebP保存参数中(返回用于`Image.save()`的kwargs字典)。

**签名**:
```python
def embed_metadata(metadata: ImageMetadata) -> dict[str, Any]
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `metadata` | `ImageMetadata` | ✅ | 要嵌入的元数据对象 |

**返回值**: `dict[str, Any]` (适用于`Image.save(**kwargs)`的参数字典)

**行为规范**:
返回字典仅包含非空的元数据字段:
```python
{
    'exif': metadata.exif if metadata.exif else None,
    'xmp': metadata.xmp if metadata.xmp else None,
    'icc_profile': metadata.icc_profile if metadata.icc_profile else None
}
```
空值会被过滤掉,避免传递`None`给Pillow导致错误。

**前置条件**:
- `metadata`不为`None`

**后置条件**:
- 返回字典的值均不为`None`(空字段已过滤)

**示例用法**:
```python
metadata = ImageMetadata(exif=exif_bytes, xmp=None, icc_profile=icc_bytes)
save_params = metadata_service.embed_metadata(metadata)

# save_params = {'exif': exif_bytes, 'icc_profile': icc_bytes}
# 注意: 'xmp': None 已被过滤

img.save("output.webp", format="WEBP", quality=80, **save_params)
```

---

### validate_metadata_preservation()

**功能**: 验证转换后的WebP文件是否成功保留了元数据(用于测试)。

**签名**:
```python
def validate_metadata_preservation(
    original_metadata: ImageMetadata,
    output_file_path: Path
) -> tuple[bool, str]
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `original_metadata` | `ImageMetadata` | ✅ | 原始图片的元数据 |
| `output_file_path` | `Path` | ✅ | 转换后的WebP文件路径 |

**返回值**: `tuple[bool, str]`
- `bool`: 是否保留成功
- `str`: 验证结果描述(中文)

**行为规范**:
1. 打开输出文件提取元数据
2. 比较EXIF/XMP/ICC是否与原始数据一致(字节级比较)
3. 返回验证结果

**前置条件**:
- `output_file_path`存在且可读

**后置条件**:
- 如果所有元数据一致,返回`(True, "元数据保留成功")`
- 如果有差异,返回`(False, "EXIF元数据丢失")` 或类似描述

**示例用法**:
```python
# 测试场景
original_metadata = metadata_service.extract_metadata(img)
# ... 执行转换 ...
is_valid, message = metadata_service.validate_metadata_preservation(
    original_metadata,
    Path("output.webp")
)
assert is_valid, message
```

---

## 依赖

### 内部依赖
- `models.ImageMetadata`: 元数据数据类

### 外部依赖
- `Pillow >= 10.0.0`: 图片元数据读写(Pillow 9.4+原生支持WebP EXIF/XMP)

---

## 限制和注意事项

### IPTC元数据
**限制**: WebP规范不原生支持IPTC数据结构。

**缓解方案**:
- 当前版本:忽略IPTC元数据(符合`spec.md`的FR-014:仅明确支持EXIF/IPTC/XMP,但WebP限制了IPTC)
- 未来扩展:将IPTC转换为XMP格式嵌入(需要额外库`iptcinfo3`)

**文档说明**:在用户手册中说明:"WebP格式不支持IPTC元数据,仅保留EXIF和XMP信息"

### 元数据大小限制
**限制**: 超大EXIF数据(如包含完整GPS轨迹)可能导致输出文件膨胀。

**缓解方案**:
- 当前版本:原样保留所有元数据
- 未来优化:提供选项移除缩略图(通常占EXIF的80%)

---

## 测试契约

### 单元测试

**测试用例**:
1. `test_extract_metadata_with_exif`: 从JPEG文件提取EXIF,验证`metadata.exif`不为空
2. `test_extract_metadata_without_metadata`: 从PNG(无EXIF)提取,验证`has_metadata=False`
3. `test_embed_metadata_filters_none_values`: 传入`exif=None`,验证返回字典不含`'exif'`键
4. `test_validate_metadata_preservation_success`: 转换前后元数据一致,验证返回`(True, ...)`
5. `test_validate_metadata_preservation_failure`: 手动删除输出文件EXIF,验证返回`(False, ...)`

### 集成测试

**测试用例**:
1. `test_end_to_end_metadata_preservation`: 完整流程测试(JPEG→WebP),使用`exiftool`外部工具验证EXIF标签存在

---

## 版本历史

- v1.0.0 (2025-10-21): 初始契约定义,支持EXIF/XMP/ICC
