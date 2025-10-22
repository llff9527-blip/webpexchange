<!--
Sync Impact Report:
===================
Version Change: [UNVERSIONED] → 1.0.0
Modified Principles: N/A (initial ratification)
Added Sections:
  - Core Principles (5 principles defined)
  - 技术约束 (Technical Constraints)
  - 开发工作流 (Development Workflow)
  - Governance
Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section aligned
  ✅ spec-template.md - Requirements aligned with Chinese documentation principle
  ✅ tasks-template.md - Task structure supports multi-platform testing
  ✅ All command files reviewed - generic guidance confirmed
Follow-up TODOs: None
Rationale: Initial constitution ratification establishing core principles for WebPExchange project
===================
-->

# WebPExchange 项目宪章

## 核心原则

### I. 中文优先 (Chinese-First Documentation)

**要求**:
- 所有项目文档、代码注释、提交信息、README、API文档必须使用中文
- 函数名、变量名、类名可使用英文(遵循编程语言惯例)
- 用户界面文本必须支持国际化(i18n),但中文为默认语言
- 技术术语可保留英文,但需在首次使用时提供中文解释

**理由**: 确保团队成员高效沟通,降低理解成本,提高开发效率和文档可维护性。

### II. 多平台支持 (Multi-Platform Compatibility)

**要求**:
- 所有功能必须支持主流平台: Windows、macOS、Linux
- 禁止使用平台特定API,除非有跨平台抽象层
- 文件路径处理必须使用跨平台库(如Node.js的`path`模块)
- 测试必须在至少两个不同平台上验证
- 构建脚本必须能在所有目标平台上执行

**理由**: 扩大用户覆盖面,避免平台锁定,确保产品可移植性和长期可维护性。

### III. 测试优先 (Test-First) - 不可协商

**要求**:
- 采用TDD方法论:先写测试 → 用户批准 → 测试失败(红灯) → 实现功能 → 测试通过(绿灯) → 重构
- 每个功能必须包含:
  - 单元测试(覆盖核心逻辑)
  - 集成测试(覆盖组件交互)
  - 契约测试(验证API接口)
- 测试覆盖率要求: 核心业务逻辑 ≥ 80%
- 禁止跳过失败的测试,必须修复或移除

**理由**: 确保代码质量,减少回归问题,建立可信赖的持续集成流程。

### IV. 渐进式开发 (Incremental Development)

**要求**:
- 将复杂功能拆分为3-5个独立可测试的用户故事
- 每个提交必须:
  - 能够成功编译
  - 通过所有现有测试
  - 不破坏已有功能
- 采用MVP(最小可行产品)策略: P1故事先行,逐步添加P2、P3
- 每个用户故事必须独立可交付和可演示

**理由**: 降低风险,快速获得反馈,保持主分支始终可发布状态。

### V. 简洁优于复杂 (Simplicity Over Complexity)

**要求**:
- 优先选择"无聊"的解决方案(成熟、广泛使用的技术栈)
- 避免过早抽象,遵循YAGNI(你不会需要它)原则
- 函数职责单一,类遵循单一职责原则(SRP)
- 每引入一个新依赖必须记录理由
- 复杂度违规必须在`plan.md`的"复杂度追踪"表中正当化

**理由**: 提高可维护性,降低认知负担,便于新成员快速上手。

## 技术约束

### 依赖管理
- 优先使用项目已有的包管理器和构建工具
- 新增依赖需评估:
  - 跨平台兼容性
  - 维护活跃度(最近6个月有更新)
  - 许可证合规性
  - 包大小(避免引入超大依赖)

### 代码规范
- 必须通过项目配置的Linter和格式化工具检查
- 提交前运行: `npm run lint` 或等效命令
- 文件编码统一使用UTF-8
- 行结束符统一使用LF(配置Git自动转换)

### 错误处理
- 快速失败,提供描述性中文错误消息
- 错误对象必须包含:
  - 错误类型/代码
  - 中文描述
  - 上下文信息(用于调试)
- 禁止静默捕获异常(除非有明确日志记录)

## 开发工作流

### 实施流程
1. **理解 (Understand)**: 研究代码库现有模式,必要时使用Gemini进行深度分析
2. **规划 (Plan)**: 在`specs/[###-feature]/plan.md`中记录实施计划
3. **测试 (Test)**: 先编写测试用例,确保测试失败(红灯)
4. **实现 (Implement)**: 编写最少代码使测试通过(绿灯)
5. **重构 (Refactor)**: 在测试保护下优化代码
6. **审查 (Review)**: 使用zen mcp调用Gemini进行代码审查
7. **提交 (Commit)**: 使用清晰的中文提交信息

### 分支策略
- 功能开发使用`###-feature-name`格式分支名
- 主分支(`main`)保持始终可部署状态
- 合并前必须通过所有CI检查

### 陷入困境时
最多尝试3次后:
1. 记录失败原因(中文)
2. 研究2-3个替代方案
3. 质疑是否选择了正确的抽象层级
4. 使用zen mcp调用Gemini的`explain_with_thinking`寻求新思路
5. 尝试完全不同的角度(不同库/架构模式/移除抽象)

## 治理 (Governance)

### 宪章优先级
本宪章优先于所有其他开发实践文档。发生冲突时,以宪章为准。

### 修订流程
- 宪章修订必须:
  1. 提出修订提案(在PR中)
  2. 团队评审和批准
  3. 更新版本号(遵循语义化版本)
  4. 更新所有依赖模板
  5. 记录修订影响报告

### 版本控制
- **MAJOR**: 向后不兼容的原则移除或重新定义
- **MINOR**: 新增原则或重大指导方针扩展
- **PATCH**: 澄清说明、措辞优化、错误修正

### 合规性检查
- 所有PR必须验证宪章合规性
- 功能规划阶段(`/speckit.plan`)必须包含"宪章检查"章节
- 引入复杂度必须有充分理由并记录在案

### 运行时指导
开发过程中的详细指导参见用户的全局配置文件(`~/.claude/CLAUDE.md`)。

---

**版本**: 1.0.0 | **批准日期**: 2025-10-21 | **最后修订**: 2025-10-21
