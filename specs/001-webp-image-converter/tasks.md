# Tasks: WebP图片转换器

**Input**: Design documents from `/specs/001-webp-image-converter/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Organization**: 任务按用户故事分组,支持独立实施和测试

**Tests**: 遵循TDD流程(宪章要求),所有测试先行

---

## Format: `[ID] [P?] [Story] Description`
- **[P]**: 可并行执行(不同文件,无依赖关系)
- **[Story]**: 所属用户故事(US1, US2, US3)
- 包含具体文件路径

---

## Phase 1: Setup (项目初始化)

**目的**: 建立项目基础结构和开发环境

- [ ] T001 创建项目根目录结构(src/, tests/, specs/)
- [ ] T002 创建requirements.txt,添加Pillow>=10.0.0依赖
- [ ] T003 [P] 创建requirements-dev.txt,添加pytest>=7.4.0, pytest-mock>=3.11.0
- [ ] T004 [P] 创建pytest.ini配置文件
- [ ] T005 [P] 创建.gitignore文件(忽略__pycache__, venv/, *.pyc等)
- [ ] T006 验证Pillow的WebP支持:`python -c "from PIL import features; print(features.check('webp'))"`

---

## Phase 2: Foundational (基础组件 - 阻塞所有用户故事)

**目的**: 实现所有用户故事都依赖的核心数据模型和工具类

**⚠️ 关键**: 本阶段必须完成后才能开始任何用户故事的实施

### 测试(先行 - TDD要求)

- [ ] T007 [P] 创建tests/unit/__init__.py
- [ ] T008 [P] 创建tests/integration/__init__.py
- [ ] T009 [P] 创建tests/contract/__init__.py
- [ ] T010 [P] 创建tests/fixtures/__init__.py
- [ ] T011 [P] 创建tests/fixtures/sample_images/目录并添加测试图片(JPEG, PNG, GIF各1张,约5MB)
- [ ] T012 [P] 编写ImageFile模型测试 tests/unit/test_models.py::test_image_file_from_path_valid
- [ ] T013 [P] 编写ImageFile验证测试 tests/unit/test_models.py::test_image_file_validate_file_not_found
- [ ] T014 [P] 编写ImageFile软性限制测试 tests/unit/test_models.py::test_image_file_exceeds_soft_limit
- [ ] T015 [P] 编写ImageMetadata提取测试 tests/unit/test_models.py::test_image_metadata_has_metadata
- [ ] T016 [P] 编写QualityPreset枚举测试 tests/unit/test_models.py::test_quality_preset_values
- [ ] T017 [P] 编写ConversionTask状态转换测试 tests/unit/test_models.py::test_conversion_task_state_transitions
- [ ] T018 [P] 编写FileService路径解决测试 tests/unit/test_file_service.py::test_resolve_output_path_no_conflict
- [ ] T019 [P] 编写FileService磁盘空间检查测试 tests/unit/test_file_service.py::test_check_disk_space_sufficient
- [ ] T020 [P] 编写FileService文件验证测试 tests/unit/test_file_service.py::test_validate_file_path_valid

### 实现(核心数据模型和工具)

- [ ] T021 [P] 创建src/models/__init__.py
- [ ] T022 [P] 创建src/services/__init__.py
- [ ] T023 [P] 创建src/utils/__init__.py
- [ ] T024 [P] 实现ImageMetadata模型 src/models/image_metadata.py (from_pil_image(), to_save_params())
- [ ] T025 [P] 实现QualityPreset枚举 src/models/quality_preset.py (HIGH_COMPRESSION=60, NORMAL=80, LOW_COMPRESSION=95)
- [ ] T026 实现ImageFile模型 src/models/image_file.py (依赖T024: from_path(), validate(), exceeds_soft_limit属性)
- [ ] T027 实现TaskStatus枚举和ConversionTask模型 src/models/conversion_task.py (start(), complete(), fail(), cancel()方法)
- [ ] T028 [P] 实现BatchConversionJob模型 src/models/batch_conversion_job.py (add_task(), get_pending_tasks(), cancel_pending_tasks())
- [ ] T029 [P] 实现跨平台路径工具 src/utils/path_utils.py (使用pathlib.Path,确保Windows/Unix兼容)
- [ ] T030 [P] 实现文件验证器 src/utils/validator.py (质量参数范围验证,文件格式验证)
- [ ] T031 实现FileService服务 src/services/file_service.py (依赖T029: resolve_output_path(), check_disk_space(), validate_file_path())
- [ ] T032 运行T012-T020测试,确认所有测试通过

**Checkpoint**: 基础组件完成 - 用户故事实施现在可以并行开始

---

## Phase 3: User Story 1 - 基础图片转换 (优先级: P1) 🎯 MVP

**Goal**: 用户可以通过图形界面选择本地图片文件,使用预设的压缩质量(高压缩/普通/低压缩),一键将图片转换为WebP格式并保存到本地。

**Independent Test**: 选择一张PNG或JPEG图片,选择"普通"压缩质量,点击转换按钮,验证成功生成WebP文件(文件存在、大小合理、压缩比30%-70%)。

### 测试(先行 - TDD要求)

**契约测试**:
- [ ] T033 [P] [US1] 编写MetadataService.extract_metadata()契约测试 tests/contract/test_service_contracts.py::test_metadata_service_extract_metadata
- [ ] T034 [P] [US1] 编写MetadataService.embed_metadata()契约测试 tests/contract/test_service_contracts.py::test_metadata_service_embed_metadata
- [ ] T035 [P] [US1] 编写ConverterService.convert_image()契约测试 tests/contract/test_service_contracts.py::test_converter_service_convert_image_success
- [ ] T036 [P] [US1] 编写ConverterService取消机制契约测试 tests/contract/test_service_contracts.py::test_converter_service_convert_cancelled

**单元测试**:
- [ ] T037 [P] [US1] 编写元数据提取单元测试 tests/unit/test_metadata_service.py::test_extract_metadata_with_exif
- [ ] T038 [P] [US1] 编写元数据嵌入单元测试 tests/unit/test_metadata_service.py::test_embed_metadata_filters_none
- [ ] T039 [P] [US1] 编写WebP转换成功测试 tests/unit/test_converter_service.py::test_convert_image_success
- [ ] T040 [P] [US1] 编写WebP转换文件不存在测试 tests/unit/test_converter_service.py::test_convert_image_file_not_found
- [ ] T041 [P] [US1] 编写WebP转换保留元数据测试 tests/unit/test_converter_service.py::test_convert_image_preserve_metadata
- [ ] T042 [P] [US1] 编写WebP转换取消测试 tests/unit/test_converter_service.py::test_convert_image_cancelled

**集成测试**:
- [ ] T043 [US1] 编写端到端转换流程集成测试 tests/integration/test_conversion_workflow.py::test_end_to_end_single_conversion (测试选择文件→转换→验证输出完整流程)

### 实现(服务层)

- [ ] T044 [US1] 实现MetadataService服务 src/services/metadata_service.py (extract_metadata(), embed_metadata(), validate_metadata_preservation())
- [ ] T045 [US1] 实现ConverterService服务 src/services/converter_service.py (convert_image()方法,支持quality参数、元数据保留、stop_event取消)
- [ ] T046 [US1] 运行T033-T043测试,确认所有US1服务层测试通过

### 实现(GUI - 核心界面)

- [ ] T047 [P] [US1] 创建src/gui/__init__.py
- [ ] T048 [P] [US1] 创建src/gui/components/__init__.py
- [ ] T049 [P] [US1] 创建src/gui/handlers/__init__.py
- [ ] T050 [US1] 实现图片选择组件 src/gui/components/image_selector.py (tkinter.filedialog.askopenfilename(),显示预览和文件信息)
- [ ] T051 [US1] 实现质量控制组件(预设模式) src/gui/components/quality_control.py (三个单选按钮:高压缩/普通/低压缩)
- [ ] T052 [US1] 实现进度显示组件 src/gui/components/progress_display.py (ttk.Progressbar + 状态标签,支持取消按钮)
- [ ] T053 [US1] 实现转换处理器 src/gui/handlers/conversion_handler.py (单张转换:threading.Thread + queue.Queue更新进度,调用ConverterService.convert_image())
- [ ] T054 [US1] 实现取消处理器 src/gui/handlers/cancel_handler.py (设置threading.Event,通知工作线程停止)
- [ ] T055 [US1] 实现主窗口 src/gui/main_window.py (整合image_selector, quality_control, progress_display,布局使用grid管理器)
- [ ] T056 [US1] 实现应用入口 src/main.py (创建tkinter.Tk根窗口,启动main_window,设置窗口标题和大小)

### 实现(GUI测试 - 可选手动测试)

- [ ] T057 [US1] 手动测试:运行`python src/main.py`,验证界面正常显示(中文标签、三个质量预设、选择图片按钮)
- [ ] T058 [US1] 手动测试:选择JPEG图片,点击"普通"质量,转换成功,验证输出WebP文件存在
- [ ] T059 [US1] 手动测试:选择PNG图片,点击"高压缩"质量,验证压缩比>60%
- [ ] T060 [US1] 手动测试:选择大图片(>50MB),转换中途点击"取消",验证停止且不生成文件
- [ ] T061 [US1] 手动测试:选择TXT文件,验证错误提示"不支持的文件格式,请选择图片文件(JPEG, PNG, GIF等)"

**Checkpoint**: User Story 1 (MVP)完成 - 应用已可交付,支持单张图片转换

---

## Phase 4: User Story 2 - 自定义压缩质量 (优先级: P2)

**Goal**: 用户可以通过滑块或输入框自定义压缩质量参数(0-100),实现对输出文件大小和质量的精确控制。

**Independent Test**: 选择图片后,切换到"自定义"模式,设置质量值为85,转换后验证输出文件使用了质量85(通过压缩比和文件大小推断)。

### 测试(先行 - TDD要求)

**单元测试**:
- [ ] T062 [P] [US2] 编写自定义质量验证测试 tests/unit/test_validator.py::test_validate_quality_in_range
- [ ] T063 [P] [US2] 编写自定义质量超出范围测试 tests/unit/test_validator.py::test_validate_quality_out_of_range
- [ ] T064 [P] [US2] 编写质量滑块同步测试 tests/unit/test_quality_control.py::test_slider_sync_with_input (使用pytest-mock模拟tkinter事件)

**集成测试**:
- [ ] T065 [US2] 编写自定义质量转换集成测试 tests/integration/test_conversion_workflow.py::test_custom_quality_conversion (质量=85,验证输出文件质量)

### 实现(扩展质量控制组件)

- [ ] T066 [US2] 扩展质量控制组件 src/gui/components/quality_control.py (添加"自定义"单选按钮、ttk.Scale滑块0-100、tk.Spinbox数值输入框,实现双向同步)
- [ ] T067 [US2] 在主窗口中集成自定义质量UI src/gui/main_window.py (当选择"自定义"时,启用滑块和输入框;选择预设时禁用)
- [ ] T068 [US2] 实现质量参数验证 src/utils/validator.py::validate_quality_range() (范围[0,100],超出范围自动修正并提示)
- [ ] T069 [US2] 运行T062-T065测试,确认所有US2测试通过

### 实现(GUI测试 - 可选手动测试)

- [ ] T070 [US2] 手动测试:选择图片,点击"自定义",拖动滑块到75,验证输入框同步显示75
- [ ] T071 [US2] 手动测试:在输入框输入90,验证滑块同步移动到90
- [ ] T072 [US2] 手动测试:输入框输入150,失去焦点时验证自动修正为100并显示提示"质量参数已修正为100"
- [ ] T073 [US2] 手动测试:使用自定义质量40转换图片,验证输出文件极小(高压缩)

**Checkpoint**: User Story 1+2完成 - 应用支持预设和自定义质量

---

## Phase 5: User Story 3 - 批量转换 (优先级: P3)

**Goal**: 用户可以一次选择多张图片,使用相同的压缩设置批量转换为WebP格式,并查看转换进度和每张图片的转换结果。

**Independent Test**: 选择包含10张图片的文件夹,设置"普通"质量,点击批量转换,验证所有图片都成功转换并显示进度"10/10 已完成"。

### 测试(先行 - TDD要求)

**契约测试**:
- [ ] T074 [P] [US3] 编写ConverterService.batch_convert()契约测试 tests/contract/test_service_contracts.py::test_converter_service_batch_convert
- [ ] T075 [P] [US3] 编写批量转换进度回调契约测试 tests/contract/test_service_contracts.py::test_batch_convert_progress_callback
- [ ] T076 [P] [US3] 编写批量转换取消契约测试 tests/contract/test_service_contracts.py::test_batch_convert_cancelled_mid_way

**单元测试**:
- [ ] T077 [P] [US3] 编写批量转换成功测试 tests/unit/test_converter_service.py::test_batch_convert_success
- [ ] T078 [P] [US3] 编写批量转换部分失败测试 tests/unit/test_converter_service.py::test_batch_convert_partial_failure (某张图片失败,其他继续)
- [ ] T079 [P] [US3] 编写批量转换取消测试 tests/unit/test_converter_service.py::test_batch_convert_cancelled_after_2_tasks
- [ ] T080 [P] [US3] 编写BatchConversionJob进度计算测试 tests/unit/test_models.py::test_batch_job_progress_percentage

**集成测试**:
- [ ] T081 [US3] 编写批量转换集成测试 tests/integration/test_batch_conversion.py::test_batch_convert_10_images (10张5MB图片,总耗时<60秒)

### 实现(服务层扩展)

- [ ] T082 [US3] 实现ConverterService批量转换方法 src/services/converter_service.py::batch_convert() (ThreadPoolExecutor(max_workers=3), 支持progress_callback和stop_event)
- [ ] T083 [US3] 运行T074-T081测试,确认所有US3服务层测试通过

### 实现(GUI - 批量转换界面)

- [ ] T084 [P] [US3] 扩展图片选择组件支持多选 src/gui/components/image_selector.py (tkinter.filedialog.askopenfilenames(),显示图片列表和缩略图)
- [ ] T085 [US3] 实现批量转换处理器 src/gui/handlers/batch_conversion_handler.py (创建BatchConversionJob,调用ConverterService.batch_convert(),更新进度"X/Y 已完成")
- [ ] T086 [US3] 扩展进度显示组件支持批量进度 src/gui/components/progress_display.py (显示"已完成X/总数Y",每张图片的转换状态:✅成功/❌失败)
- [ ] T087 [US3] 在主窗口中集成批量转换UI src/gui/main_window.py (添加"批量选择"按钮,切换单张/批量模式,批量模式下显示图片列表)
- [ ] T088 [US3] 实现批量转换取消逻辑 src/gui/handlers/cancel_handler.py (设置stop_event,停止后续未开始任务,已完成文件保留)

### 实现(GUI测试 - 可选手动测试)

- [ ] T089 [US3] 手动测试:点击"批量选择",选择5张图片,验证显示5张缩略图和文件信息
- [ ] T090 [US3] 手动测试:批量转换5张图片(质量80),验证进度条实时更新"1/5 已完成"→"2/5 已完成"
- [ ] T091 [US3] 手动测试:批量转换10张图片,完成2张后点击"取消",验证停止后续转换,已完成2张文件保留,显示"批量转换已取消(已完成2/10)"
- [ ] T092 [US3] 手动测试:批量转换包含1张损坏图片和4张正常图片,验证损坏图片标记失败,其他4张成功转换
- [ ] T093 [US3] 手动测试:批量转换10张5MB图片,验证总耗时<60秒(性能要求SC-007)

**Checkpoint**: 所有用户故事(US1+US2+US3)完成 - 应用功能完整

---

## Phase 6: Polish & Cross-Cutting Concerns (完善和跨故事功能)

**目的**: 完善影响多个用户故事的功能和质量改进

### 边界情况和错误处理

- [ ] T094 [P] 实现所有中文错误消息 src/utils/error_messages.py (集中管理所有错误提示,确保符合FR-009)
- [ ] T095 [P] 实现软性限制警告对话框 src/gui/components/warning_dialog.py (图片>200MB或>8000x8000时显示警告,允许继续/取消)
- [ ] T096 [P] 实现文件名冲突重命名 src/services/file_service.py::resolve_output_path() (output.webp → output_1.webp → output_2.webp)
- [ ] T097 [P] 实现磁盘空间预检查 src/services/file_service.py::check_disk_space() (预估输出文件大小,检查可用空间>预估大小+100MB)
- [ ] T098 添加全局异常处理器 src/gui/main_window.py::handle_uncaught_exception() (捕获所有未处理异常,显示友好中文错误对话框)

### 元数据保留增强

- [ ] T099 [P] 实现元数据验证 tests/integration/test_metadata_preservation.py::test_exif_preserved_after_conversion (使用exiftool外部工具验证)
- [ ] T100 [P] 添加ICC配置文件保留 src/services/metadata_service.py::extract_metadata() (提取icc_profile并在转换时嵌入)

### 跨平台测试

- [ ] T101 [P] 编写跨平台路径处理测试 tests/unit/test_path_utils.py::test_windows_path_compatibility (模拟Windows路径`C:\Users\...`)
- [ ] T102 [P] 编写跨平台路径处理测试 tests/unit/test_path_utils.py::test_unix_path_compatibility (模拟Unix路径`/home/user/...`)
- [ ] T103 验证WebP支持检测 src/main.py::check_webp_support() (启动时检查Pillow WebP支持,不支持时显示安装指南)

### 用户体验改进

- [ ] T104 [P] 实现进度百分比显示 src/gui/components/progress_display.py (显示"转换中... 45%")
- [ ] T105 [P] 实现转换耗时显示 src/gui/components/progress_display.py (完成后显示"转换完成,耗时3.2秒")
- [ ] T106 [P] 实现压缩比可视化 src/gui/components/progress_display.py (显示"压缩比: 58.6% (2.5MB → 1.0MB)")
- [ ] T107 添加应用图标和窗口配置 src/gui/main_window.py (设置窗口标题"WebP图片转换器", 最小尺寸800x600)

### 文档和部署

- [ ] T108 [P] 创建README.md (项目说明、安装指南、快速开始,参考quickstart.md)
- [ ] T109 [P] 验证quickstart.md中的所有使用场景 (手动执行quickstart.md中的每个示例,确保准确性)
- [ ] T110 [P] 创建打包脚本 scripts/build.py (使用PyInstaller打包为可执行文件,支持Windows/macOS/Linux)

### 最终验证

- [ ] T111 运行完整测试套件:`pytest tests/ -v`(确认所有单元/集成/契约测试通过)
- [ ] T112 运行跨平台兼容性检查 (在至少两个平台上测试:Windows+macOS 或 macOS+Linux)
- [ ] T113 性能基准测试 (验证SC-003: 10MB图片<5秒, SC-007: 10张5MB图片<60秒)
- [ ] T114 用户验收测试 (邀请1-2名用户测试,验证SC-005: 90%用户无需文档即可完成转换)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 立即开始
- **Foundational (Phase 2)**: 依赖Setup完成 - **阻塞所有用户故事**
- **User Stories (Phase 3-5)**: 所有用户故事依赖Foundational完成
  - User Story 1 (P1): Foundational完成后立即开始 - **MVP优先**
  - User Story 2 (P2): Foundational完成后可开始,可与US1并行(不同UI组件)
  - User Story 3 (P3): Foundational完成后可开始,可与US1/US2并行(不同Handler)
- **Polish (Phase 6)**: 依赖所有期望的用户故事完成

### User Story Dependencies

- **User Story 1 (P1)**: 依赖Foundational (Phase 2) - 无其他用户故事依赖
- **User Story 2 (P2)**: 依赖Foundational (Phase 2) - 扩展US1的质量控制组件,但独立可测
- **User Story 3 (P3)**: 依赖Foundational (Phase 2) - 复用US1的ConverterService,但独立可测

### Within Each User Story

- **TDD流程**: 测试 → 实现 → 测试通过 → 重构
- **契约测试**优先(定义服务接口)
- **单元测试**次之(验证单个函数逻辑)
- **实现**: 模型 → 服务 → GUI组件 → 集成
- **集成测试**最后(验证完整流程)

### Parallel Opportunities

**Setup阶段并行(Phase 1)**:
- T003, T004, T005 可并行(不同文件)

**Foundational测试并行(Phase 2)**:
- T007-T011 可并行(创建测试目录结构)
- T012-T020 可并行(不同测试文件)

**Foundational实现并行(Phase 2)**:
- T021-T023 可并行(创建__init__.py)
- T024, T025 可并行(独立模型)
- T029, T030 可并行(独立工具类)

**User Story 1测试并行**:
- T033-T036 契约测试可并行(不同测试方法)
- T037-T042 单元测试可并行(不同测试文件)

**User Story 1 GUI组件并行**:
- T047-T049 可并行(创建__init__.py)
- T050, T051, T052 可并行(独立GUI组件)

**跨用户故事并行**:
- 一旦Foundational完成,US1/US2/US3可由不同开发者并行实施(不同模块)

**Polish阶段并行**:
- T094-T097, T099-T102, T104-T106, T108-T110 均可并行(不同文件或独立任务)

---

## Parallel Example: User Story 1

```bash
# 契约测试并行(定义服务接口)
Task: "编写MetadataService.extract_metadata()契约测试 tests/contract/test_service_contracts.py::test_metadata_service_extract_metadata"
Task: "编写MetadataService.embed_metadata()契约测试 tests/contract/test_service_contracts.py::test_metadata_service_embed_metadata"
Task: "编写ConverterService.convert_image()契约测试 tests/contract/test_service_contracts.py::test_converter_service_convert_image_success"

# 单元测试并行
Task: "编写元数据提取单元测试 tests/unit/test_metadata_service.py::test_extract_metadata_with_exif"
Task: "编写元数据嵌入单元测试 tests/unit/test_metadata_service.py::test_embed_metadata_filters_none"
Task: "编写WebP转换成功测试 tests/unit/test_converter_service.py::test_convert_image_success"

# GUI组件并行(依赖服务层实现完成)
Task: "实现图片选择组件 src/gui/components/image_selector.py"
Task: "实现质量控制组件(预设模式) src/gui/components/quality_control.py"
Task: "实现进度显示组件 src/gui/components/progress_display.py"
```

---

## Implementation Strategy

### MVP First (仅User Story 1)

1. ✅ **Complete Phase 1**: Setup (T001-T006) - 项目初始化
2. ✅ **Complete Phase 2**: Foundational (T007-T032) - **关键阻塞阶段**
3. ✅ **Complete Phase 3**: User Story 1 (T033-T061) - MVP功能
4. **STOP and VALIDATE**: 独立测试US1,运行`python src/main.py`,验证单张转换功能
5. 如果US1测试通过,可立即交付/演示MVP

**MVP交付清单**:
- [x] 用户可以选择图片文件(JPEG/PNG/GIF/BMP)
- [x] 用户可以选择三种预设质量(高压缩/普通/低压缩)
- [x] 用户可以点击转换按钮,生成WebP文件
- [x] 用户可以看到转换进度和结果(输出路径、压缩比)
- [x] 用户可以在转换中途取消操作
- [x] 所有界面文本使用中文
- [x] 元数据(EXIF/XMP)被保留

### Incremental Delivery (渐进式交付)

1. **Phase 1+2**: Setup + Foundational → 基础就绪
2. **Phase 3**: User Story 1 → 独立测试 → **交付MVP** 🎯
3. **Phase 4**: User Story 2 → 独立测试 → 交付增强版(自定义质量)
4. **Phase 5**: User Story 3 → 独立测试 → 交付完整版(批量转换)
5. **Phase 6**: Polish → 最终优化 → 正式发布

每个阶段交付后,前面的功能不会被破坏(独立可测保证)。

### Parallel Team Strategy (多人协作)

如果有多名开发者:

1. **团队共同完成**: Setup (Phase 1) + Foundational (Phase 2)
2. **Foundational完成后分工**:
   - **Developer A**: User Story 1 (T033-T061) - MVP核心
   - **Developer B**: User Story 2 (T062-T073) - 自定义质量
   - **Developer C**: User Story 3 (T074-T093) - 批量转换
3. **各故事独立完成后集成测试**
4. **团队共同完成**: Polish (Phase 6) - 最终优化

**并行优势**: 一旦Foundational完成,3个用户故事可同时推进,缩短总开发时间。

---

## Notes

- **[P] 标记**: 不同文件,无依赖,可并行执行
- **[Story] 标记**: 映射到spec.md中的用户故事,便于追踪
- **TDD流程**: 遵循宪章要求,所有测试先行(红灯 → 绿灯 → 重构)
- **独立可测**: 每个用户故事完成后应能独立验证,不依赖其他故事
- **Checkpoint验证**: 每个阶段结束时停止验证,确保功能正确
- **提交策略**: 每完成一个任务或逻辑组提交一次(使用中文提交信息)
- **避免**: 模糊任务、同文件冲突、跨故事强依赖破坏独立性

---

## Summary

**总任务数**: 114个任务
- Phase 1 (Setup): 6个任务
- Phase 2 (Foundational): 26个任务 ⚠️ 阻塞所有用户故事
- Phase 3 (US1 - MVP): 29个任务 🎯
- Phase 4 (US2): 12个任务
- Phase 5 (US3): 20个任务
- Phase 6 (Polish): 21个任务

**User Story任务分布**:
- US1 (基础图片转换): 29个任务 (MVP)
- US2 (自定义压缩质量): 12个任务
- US3 (批量转换): 20个任务

**并行机会**: 约45%的任务标记为[P],可在各自阶段内并行执行,显著缩短开发时间。

**独立测试标准**:
- **US1**: 选择图片 → 选择预设质量 → 转换 → 验证WebP输出
- **US2**: 选择图片 → 自定义质量85 → 转换 → 验证质量参数生效
- **US3**: 批量选择10张图片 → 转换 → 验证所有图片成功且进度显示正确

**建议MVP范围**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 61个任务,实现核心单张转换功能,可快速交付价值。

---

**Format Validation**: ✅ 所有任务遵循`- [ ] [ID] [P?] [Story?] Description with file path`格式
