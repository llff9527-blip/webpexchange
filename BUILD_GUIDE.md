# WebP图片转换器 - 打包指南

## 📦 快速开始

### 方法一：一键打包（推荐）

#### macOS / Linux
```bash
# 双击运行或在终端执行
./build.sh
```

#### Windows
```cmd
# 双击运行
build.bat
```

### 方法二：手动打包

```bash
# 1. 安装打包依赖
pip install pyinstaller

# 2. 执行打包脚本
python build.py
```

---

## 🎯 打包选项

### 自动检测平台打包
```bash
python build.py
```

### 指定目标平台
```bash
# 打包 macOS 应用
python build.py --platform mac

# 打包 Windows 应用
python build.py --platform windows

# 打包 Linux 应用
python build.py --platform linux
```

### 清理构建文件
```bash
python build.py --clean
```

---

## 📁 输出文件

打包完成后，在 `dist/` 目录下会生成：

### macOS
```
dist/
├── WebPConverter.app/      # macOS 应用包
└── README.txt              # 安装说明
```

**使用方法**:
- 双击 `WebPConverter.app` 运行
- 或拖到 Applications 文件夹

### Windows
```
dist/
├── WebPConverter.exe       # Windows 可执行文件
└── README.txt              # 安装说明
```

**使用方法**:
- 双击 `WebPConverter.exe` 运行

### Linux
```
dist/
├── WebPConverter           # Linux 可执行文件
└── README.txt              # 安装说明
```

**使用方法**:
```bash
chmod +x WebPConverter
./WebPConverter
```

---

## 🔧 常见问题

### Q1: PyInstaller 未安装
**错误**: `ModuleNotFoundError: No module named 'PyInstaller'`

**解决**:
```bash
pip install pyinstaller
```

### Q2: Pillow WebP 支持问题
**错误**: `WebP支持: False`

**解决**:

**macOS**:
```bash
brew install webp
pip uninstall Pillow
pip install --no-cache-dir Pillow
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install libwebp-dev
pip install --no-cache-dir Pillow
```

**Windows**:
```bash
pip uninstall Pillow
pip install --upgrade Pillow
```

### Q3: macOS "无法验证开发者"
**错误**: 打开应用时提示无法验证开发者

**解决**:
1. 右键点击应用 -> 选择"打开"
2. 点击"打开"按钮确认
3. 或在终端执行: `xattr -cr WebPConverter.app`

### Q4: Windows Defender 误报
**错误**: Windows Defender 阻止运行

**解决**:
1. 点击"更多信息"
2. 点击"仍要运行"
3. 将应用添加到排除列表

### Q5: 打包文件过大
**问题**: 生成的文件太大（>100MB）

**优化**:
1. 使用 `--exclude-module` 排除不需要的模块
2. 修改 `build.py` 中的 `pyinstaller_args`：
```python
"--exclude-module", "numpy",  # 如果不需要numpy
"--exclude-module", "scipy",  # 如果不需要scipy
```

---

## 🎨 自定义打包

### 添加应用图标

1. **准备图标文件**:
   - macOS: `icon.icns` (512x512)
   - Windows: `icon.ico` (256x256)

2. **修改 build.py**:
```python
# macOS
"--icon", "resources/icon.icns",

# Windows
"--icon", "resources/icon.ico",
```

### 修改应用信息

编辑 `build.py` 顶部配置:
```python
PROJECT_NAME = "WebP图片转换器"
APP_NAME = "WebPConverter"
VERSION = "1.0.0"
AUTHOR = "Your Name"
```

---

## 📊 打包大小参考

| 平台 | 文件大小 | 启动时间 |
|------|---------|---------|
| macOS (.app) | ~40-60 MB | <2秒 |
| Windows (.exe) | ~30-50 MB | <3秒 |
| Linux (binary) | ~35-55 MB | <2秒 |

*注: 实际大小取决于包含的依赖和Python版本*

---

## 🚀 分发应用

### macOS
1. 压缩应用:
   ```bash
   cd dist
   zip -r WebPConverter-macOS.zip WebPConverter.app
   ```

2. (可选) 创建 DMG:
   ```bash
   # 需要安装 create-dmg
   brew install create-dmg
   create-dmg WebPConverter.app
   ```

### Windows
1. 创建安装包（可选）:
   - 使用 Inno Setup 创建安装向导
   - 或使用 NSIS

2. 或直接分发 exe:
   ```bash
   # 压缩为 zip
   Compress-Archive -Path dist\WebPConverter.exe -DestinationPath WebPConverter-Windows.zip
   ```

### Linux
```bash
cd dist
tar -czf WebPConverter-Linux.tar.gz WebPConverter README.txt
```

---

## 📝 完整构建流程

```bash
# 1. 克隆代码
git clone <repository-url>
cd webpexchange

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 运行测试
PYTHONPATH=. pytest tests/ -v

# 5. 打包应用
python build.py

# 6. 测试打包后的应用
cd dist
# macOS
open WebPConverter.app
# Windows
WebPConverter.exe
# Linux
./WebPConverter

# 7. 分发
# 将 dist/ 目录中的文件分发给用户
```

---

## 🔐 代码签名（可选）

### macOS
```bash
# 需要 Apple Developer 账号
codesign --deep --force --sign "Developer ID Application: Your Name" dist/WebPConverter.app
```

### Windows
```bash
# 需要代码签名证书
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/WebPConverter.exe
```

---

## 💡 提示

1. **首次打包**: 可能需要较长时间（5-10分钟），PyInstaller 需要分析所有依赖
2. **后续打包**: 使用 `--clean` 参数可以清理缓存，确保打包干净
3. **测试**: 在目标平台上测试打包后的应用，确保功能正常
4. **更新**: 每次发布新版本时，记得更新 `VERSION` 变量

---

## 📞 获取帮助

**问题反馈**: https://github.com/your-org/webpexchange/issues

**打包文档**: https://pyinstaller.org/

---

**最后更新**: 2025-10-22
