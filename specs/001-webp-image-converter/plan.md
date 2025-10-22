# Implementation Plan: WebP图片转换器

**Branch**: `001-webp-image-converter` | **Date**: 2025-10-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-webp-image-converter/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

开发一个跨平台(Windows/macOS/Linux)的WebP图片转换器,支持通过图形界面选择本地图片文件,使用预设或自定义的有损压缩质量参数将图片转换为WebP格式,同时保留原始元数据(EXIF/IPTC/XMP)。支持单张和批量转换,提供实时进度显示和取消操作功能。

## Technical Context

**Language/Version**: Python 3.10+ (用户指定使用Python,3.10+确保现代特性支持和广泛平台兼容性)
**Primary Dependencies**: tkinter(Python内置) + Pillow>=10.0.0 (零额外GUI依赖,仅需Pillow处理图片)
**Storage**: 本地文件系统 (无需数据库,转换任务状态仅在内存中维护)
**Testing**: pytest (Python标准测试框架,符合简洁原则)
**Target Platform**: Windows 10+, macOS 11+, Ubuntu 20.04+ (跨平台桌面应用)
**Project Type**: single (单一桌面应用项目)
**Performance Goals**: 单张图片(<10MB)转换时间<5秒,批量转换10张图片(每张5MB)总耗时<60秒
**Constraints**: 支持软性限制(200MB文件或8000x8000像素),转换过程中允许取消操作,内存使用需合理
**Scale/Scope**: 单用户桌面应用,支持单张/批量转换,3个主要用户故事(基础转换P1/自定义质量P2/批量转换P3)

**技术决策总结**(基于Phase 0研究):
1. **GUI框架**: tkinter (Python内置,零第三方依赖,完美符合"尽可能少依赖"要求)
2. **WebP转换库**: Pillow>=10.0.0 (原生支持WebP有损压缩和EXIF/XMP元数据,成熟稳定)
3. **元数据处理**: Pillow内置API (Image.getexif() + save(exif=..., xmp=...), 无需额外库)
4. **异步处理**: threading.Thread + threading.Event (单张转换) / ThreadPoolExecutor(max_workers=3) (批量转换)
5. **跨平台路径**: pathlib.Path (Python标准库,自动处理Windows/Unix分隔符)

**依赖清单**:
```
# requirements.txt
Pillow>=10.0.0  # WebP转换和元数据保留

# requirements-dev.txt
pytest>=7.4.0
pytest-mock>=3.11.0
PyInstaller>=5.13.0  # 打包工具(可选)
```

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

根据 `.specify/memory/constitution.md` 检查以下关键原则:

### ✅ 中文优先
- [x] 所有文档和注释已使用中文 (spec.md和plan.md已使用中文)
- [x] 提交信息使用中文 (将在开发过程中执行)
- [x] 错误消息使用中文 (FR-009/FR-011已明确要求中文错误提示和界面文本)

### ✅ 多平台支持
- [x] 未使用平台特定API(或已提供跨平台抽象) (将使用跨平台GUI框架和库)
- [x] 文件路径使用跨平台库处理 (FR-012明确要求,Python的pathlib.Path提供跨平台支持)
- [x] 计划在至少两个平台上测试 (SC-004要求在Windows/macOS/Linux上测试)

### ✅ 测试优先
- [x] 已规划单元测试、集成测试、契约测试 (将在Phase 1设计阶段详细规划测试策略)
- [x] 遵循TDD流程:测试先行 (宪章要求的TDD流程将在实施阶段执行)

### ✅ 渐进式开发
- [x] 功能已拆分为独立的用户故事(P1/P2/P3) (spec.md定义了3个独立故事:基础转换P1/自定义质量P2/批量转换P3)
- [x] 每个故事可独立交付 (每个用户故事都有独立测试场景,P1即为MVP)

### ✅ 简洁优于复杂
- [x] 选择了成熟、广泛使用的技术栈 (Python 3.10+, pytest,将在研究阶段确认GUI和WebP库选择)
- [x] 避免过早抽象 (将从最简单的实现开始,仅在必要时引入抽象)
- [x] 新依赖已记录理由 (所有依赖选择将在research.md中记录决策理由)

**违规记录**: 无违规项。所有宪章原则均已满足。

**GATE状态**: ✅ 通过 - 可以进入Phase 0研究阶段

---

## 设计后宪章检查 (Phase 1完成后)

**重新评估日期**: 2025-10-21

### ✅ 中文优先 (再确认)
- [x] 所有设计文档(data-model.md, contracts/, quickstart.md)使用中文 ✅
- [x] 服务契约中的错误消息均为中文 ✅
- [x] quickstart.md为中文用户手册 ✅

### ✅ 多平台支持 (再确认)
- [x] 技术选型(tkinter, Pillow)均为跨平台方案 ✅
- [x] FileService契约明确使用pathlib.Path处理路径 ✅
- [x] quickstart.md包含所有平台的安装指南(Windows/macOS/Linux) ✅

### ✅ 测试优先 (再确认)
- [x] 所有服务契约包含详细的测试用例定义 ✅
- [x] data-model.md定义了验证规则和边界情况测试 ✅
- [x] contracts/包含单元测试和集成测试规范 ✅

### ✅ 渐进式开发 (再确认)
- [x] 设计支持P1→P2→P3渐进实施(基础转换→自定义质量→批量转换) ✅
- [x] 每个用户故事对应独立的服务接口(convert_image vs batch_convert) ✅

### ✅ 简洁优于复杂 (再确认)
- [x] 最终技术选型:tkinter(内置)+Pillow(仅1个依赖),符合"尽可能少依赖"要求 ✅
- [x] 数据模型简洁:5个核心实体,无过度抽象 ✅
- [x] 服务接口简单明了:3个服务(Converter/Metadata/File),职责清晰 ✅

**最终GATE状态**: ✅ 通过 - 设计完全符合宪章要求,可进入实施阶段(/speckit.tasks)

## Project Structure

### Documentation (this feature)

```
specs/001-webp-image-converter/
├── spec.md              # 功能规格(已存在)
├── plan.md              # 本文件(/speckit.plan命令输出)
├── research.md          # Phase 0输出(技术选择研究)
├── data-model.md        # Phase 1输出(数据模型定义)
├── quickstart.md        # Phase 1输出(快速开始指南)
├── contracts/           # Phase 1输出(API契约/内部接口定义)
└── tasks.md             # Phase 2输出(/speckit.tasks命令生成 - 本命令不生成)
```

### Source Code (repository root)

```
webpexchange/               # 项目根目录
├── src/                    # 源代码
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── image_file.py   # 图片文件实体
│   │   ├── conversion_task.py  # 转换任务实体
│   │   └── quality_preset.py   # 质量预设实体
│   ├── services/           # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── converter_service.py  # WebP转换核心服务
│   │   ├── metadata_service.py   # 元数据提取/嵌入服务
│   │   └── file_service.py       # 文件路径处理服务
│   ├── gui/                # 图形界面
│   │   ├── __init__.py
│   │   ├── main_window.py        # 主窗口
│   │   ├── components/           # UI组件
│   │   │   ├── __init__.py
│   │   │   ├── image_selector.py    # 图片选择组件
│   │   │   ├── quality_control.py   # 质量控制组件
│   │   │   └── progress_display.py  # 进度显示组件
│   │   └── handlers/             # 事件处理器
│   │       ├── __init__.py
│   │       ├── conversion_handler.py  # 转换操作处理
│   │       └── cancel_handler.py      # 取消操作处理
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── path_utils.py         # 跨平台路径工具
│   │   └── validator.py          # 输入验证工具
│   └── main.py             # 应用程序入口
├── tests/                  # 测试
│   ├── unit/               # 单元测试
│   │   ├── __init__.py
│   │   ├── test_converter_service.py
│   │   ├── test_metadata_service.py
│   │   ├── test_file_service.py
│   │   └── test_models.py
│   ├── integration/        # 集成测试
│   │   ├── __init__.py
│   │   ├── test_conversion_workflow.py
│   │   └── test_batch_conversion.py
│   ├── contract/           # 契约测试(内部接口契约)
│   │   ├── __init__.py
│   │   └── test_service_contracts.py
│   └── fixtures/           # 测试固件
│       ├── sample_images/  # 测试用图片
│       └── __init__.py
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── pytest.ini             # pytest配置
├── .gitignore
└── README.md              # 项目说明
```

**Structure Decision**: 采用单项目结构(Option 1),因为这是一个独立的桌面应用程序,不涉及前后端分离或移动端开发。结构遵循以下原则:
- `models/`: 定义核心数据实体(图片文件、转换任务、质量预设)
- `services/`: 业务逻辑分离(转换、元数据、文件处理各自独立)
- `gui/`: GUI代码与业务逻辑分离,便于测试和潜在的CLI扩展
- `tests/`: 按测试类型(单元/集成/契约)组织,每个测试文件对应源代码模块
- 使用Python包结构(`__init__.py`),确保模块可导入和测试

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

无违规项,本节留空。

