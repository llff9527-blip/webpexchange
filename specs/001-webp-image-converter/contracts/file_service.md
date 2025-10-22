# FileService 服务契约

**服务名称**: FileService (文件路径处理服务)
**职责**: 跨平台文件路径处理、文件名冲突解决、磁盘空间检查
**位置**: `src/services/file_service.py`

---

## 接口定义

### resolve_output_path()

**功能**: 解决文件名冲突,自动重命名以避免覆盖已有文件(对应FR-013需求)。

**签名**:
```python
def resolve_output_path(base_path: Path) -> Path
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `base_path` | `Path` | ✅ | 期望的输出路径 |

**返回值**: `Path` (唯一的输出路径)

**行为规范**:
1. 如果`base_path`不存在,直接返回
2. 如果存在,按以下规则重命名:
   - `output.webp` → `output_1.webp`
   - `output_1.webp` → `output_2.webp`
   - 依此类推,直到找到不存在的文件名

**示例**:
```python
# 假设目录中已存在: output.webp, output_1.webp
path = file_service.resolve_output_path(Path("/path/to/output.webp"))
# 返回: /path/to/output_2.webp
```

**前置条件**:
- `base_path.parent`必须存在(父目录存在)

**后置条件**:
- 返回的路径不存在(可安全创建)
- 保留原始文件名的前缀和扩展名

**性能要求**:
- 即使有100个冲突文件,查找时间 < 100ms

---

### check_disk_space()

**功能**: 检查目标路径的可用磁盘空间是否足够保存转换后的文件。

**签名**:
```python
def check_disk_space(
    output_path: Path,
    estimated_size: int
) -> tuple[bool, str]
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `output_path` | `Path` | ✅ | 输出文件路径 |
| `estimated_size` | `int` | ✅ | 预估文件大小(字节) |

**返回值**: `tuple[bool, str]`
- `bool`: 是否有足够空间
- `str`: 描述信息(中文)

**行为规范**:
1. 使用`shutil.disk_usage()`获取磁盘可用空间
2. 如果`可用空间 >= estimated_size + 100MB`(预留100MB缓冲),返回`(True, "磁盘空间充足")`
3. 否则返回`(False, "磁盘空间不足,无法保存转换后的文件")`

**前置条件**:
- `output_path.parent`存在

**后置条件**:
- 检查操作不修改文件系统

**示例用法**:
```python
ok, msg = file_service.check_disk_space(
    Path("/path/to/output.webp"),
    estimated_size=5 * 1024 * 1024  # 5MB
)

if not ok:
    show_error_dialog(msg)
```

---

### validate_file_path()

**功能**: 验证文件路径的有效性(存在性、可读性、格式支持)。

**签名**:
```python
def validate_file_path(file_path: Path) -> tuple[bool, str]
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `file_path` | `Path` | ✅ | 要验证的文件路径 |

**返回值**: `tuple[bool, str]`
- `bool`: 是否有效
- `str`: 错误消息(中文,无效时) 或 "文件有效"

**验证规则**:

| 检查项 | 验证方法 | 失败消息 |
|-------|---------|---------|
| 文件存在 | `file_path.exists()` | "图片文件损坏或无法访问,请检查文件" |
| 是文件(非目录) | `file_path.is_file()` | "路径不是有效的文件" |
| 文件可读 | `os.access(file_path, os.R_OK)` | "无权限读取文件" |
| 扩展名支持 | `.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']` | "不支持的文件格式,请选择图片文件(JPEG, PNG, GIF等)" |

**示例用法**:
```python
is_valid, error = file_service.validate_file_path(Path("/path/to/image.jpg"))

if not is_valid:
    show_error_dialog(error)
```

---

### get_safe_filename()

**功能**: 清理文件名中的非法字符,确保跨平台兼容性。

**签名**:
```python
def get_safe_filename(filename: str) -> str
```

**参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `filename` | `str` | ✅ | 原始文件名 |

**返回值**: `str` (清理后的文件名)

**清理规则**:
1. 移除Windows非法字符: `< > : " / \ | ? *`
2. 移除控制字符(ASCII < 32)
3. 替换为下划线`_`
4. 限制长度 ≤ 255字符(文件系统限制)

**示例**:
```python
safe = file_service.get_safe_filename('photo<1>.jpg')
# 返回: 'photo_1_.jpg'
```

---

## 依赖

### 内部依赖
- 无

### 外部依赖
- `pathlib.Path`: 跨平台路径处理(Python标准库)
- `shutil.disk_usage`: 磁盘空间检查(Python标准库)
- `os.access`: 权限检查(Python标准库)

---

## 跨平台兼容性保证

### 路径分隔符
**策略**: 始终使用`pathlib.Path`,自动处理Windows的`\`和Unix的`/`

**示例**:
```python
# 错误做法 (硬编码分隔符)
path = "/path/to/file.jpg"  # Linux可用,Windows失败

# 正确做法
path = Path("/path") / "to" / "file.jpg"  # 跨平台
```

### 文件名限制
**策略**: 使用`get_safe_filename()`清理文件名,避免平台特定非法字符

### 磁盘空间检查
**Windows**: `shutil.disk_usage()`自动识别盘符(如`C:\`)
**Unix**: 自动处理挂载点

---

## 测试契约

### 单元测试

**测试用例**:
1. `test_resolve_output_path_no_conflict`: 文件不存在,返回原路径
2. `test_resolve_output_path_with_conflict`: 文件存在,返回`_1`后缀路径
3. `test_resolve_output_path_multiple_conflicts`: 已有`output.webp`和`output_1.webp`,返回`output_2.webp`
4. `test_check_disk_space_sufficient`: 可用空间充足,返回`(True, ...)`
5. `test_check_disk_space_insufficient`: 可用空间不足,返回`(False, "磁盘空间不足...")`
6. `test_validate_file_path_valid`: 有效文件,返回`(True, "文件有效")`
7. `test_validate_file_path_not_exists`: 文件不存在,返回`(False, "图片文件损坏...")`
8. `test_validate_file_path_unsupported_format`: `.txt`文件,返回`(False, "不支持的文件格式...")`
9. `test_get_safe_filename_remove_illegal_chars`: 输入`"file<1>.jpg"`,返回`"file_1_.jpg"`
10. `test_get_safe_filename_limit_length`: 输入260字符文件名,返回255字符

### 集成测试

**测试用例**:
1. `test_cross_platform_path_handling`: 在Windows和Linux上测试路径创建和文件操作
2. `test_disk_space_edge_case`: 模拟磁盘几乎满的情况,验证错误提示

---

## 版本历史

- v1.0.0 (2025-10-21): 初始契约定义
