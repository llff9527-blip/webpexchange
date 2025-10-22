# 跨平台打包指南

## ❌ PyInstaller 的限制

**重要**: PyInstaller **不支持交叉编译**
- 在 Mac 上只能打包 Mac 应用 (.app)
- 在 Windows 上只能打包 Windows 应用 (.exe)
- 在 Linux 上只能打包 Linux 应用 (binary)

---

## ✅ 解决方案对比

| 方案 | 难度 | 自动化 | 推荐度 | 说明 |
|------|------|--------|--------|------|
| GitHub Actions | ⭐ | ✅ | ⭐⭐⭐⭐⭐ | 最推荐，免费云端打包 |
| Docker | ⭐⭐ | ✅ | ⭐⭐⭐⭐ | 本地容器化打包 |
| 虚拟机 | ⭐⭐⭐ | ❌ | ⭐⭐⭐ | 资源占用大 |
| 借用机器 | ⭐ | ❌ | ⭐⭐ | 需要多台机器 |

---

## 方案1: GitHub Actions（推荐）⭐⭐⭐⭐⭐

### 优点
- ✅ **完全免费**（公开仓库）
- ✅ **自动化**：提交代码自动打包
- ✅ **同时打包** Mac/Windows/Linux
- ✅ **无需本地环境**
- ✅ **自动发布** Release

### 使用步骤

#### 1. 推送代码到 GitHub
```bash
cd /Users/llff/Projects/webpexchange

# 初始化git（如果还没有）
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/webpexchange.git
git push -u origin main
```

#### 2. 手动触发打包
在 GitHub 仓库页面：
1. 点击 **Actions** 标签
2. 选择 **Build Multi-Platform Apps** workflow
3. 点击 **Run workflow**
4. 选择分支，点击 **Run workflow** 按钮

#### 3. 下载打包文件
- 打包完成后，在 Actions 页面点击对应的运行
- 在 **Artifacts** 区域下载：
  - `WebPConverter-macOS.zip`
  - `WebPConverter-Windows.zip`
  - `WebPConverter-Linux.tar.gz`

#### 4. 自动发布（可选）
创建 git tag 自动发布：
```bash
git tag v1.0.0
git push origin v1.0.0
```

会自动创建 GitHub Release 并上传所有平台的打包文件。

### 配置文件
已创建: `.github/workflows/build.yml`

---

## 方案2: Docker 容器打包 ⭐⭐⭐⭐

### 优点
- ✅ 本地打包，无需GitHub
- ✅ 可以打包 Windows 和 Linux 应用
- ✅ 环境隔离，不污染本地

### 缺点
- ❌ Docker Desktop 占用资源
- ❌ Windows 容器镜像很大（~5GB）
- ⚠️ Mac M1/M2 芯片可能有兼容性问题

### 使用步骤

#### 1. 安装 Docker Desktop
下载并安装: https://www.docker.com/products/docker-desktop

#### 2. 打包 Windows 应用
```bash
# 方式1：使用脚本（推荐）
./docker-build.sh

# 方式2：手动执行
docker build -f Dockerfile.windows -t webp-builder-windows .
docker run --rm -v "$(pwd)/dist:/app/dist" webp-builder-windows
```

#### 3. 获取打包文件
打包完成后，在 `dist/` 目录找到 `WebPConverter.exe`

### 已创建文件
- `Dockerfile.windows` - Windows 打包配置
- `docker-build.sh` - 打包脚本

### ⚠️ 重要限制
**Docker 方案在 Mac 上无法工作！**

❌ **Mac（包括 Intel 和 M1/M2）**：
- Docker Desktop for Mac 只支持 Linux 容器
- **无法运行 Windows 容器**
- Windows 容器需要 Windows 内核

✅ **仅在 Linux 上可用**：
- 可以在 Linux 上使用 Docker 运行 Windows 容器
- 需要安装 Docker Engine with Windows support

**结论**: Mac 用户请使用 GitHub Actions 方案！

---

## 方案3: 虚拟机 ⭐⭐⭐

### 使用 Parallels Desktop / VMware
在 Mac 上运行 Windows 虚拟机来打包。

#### 步骤
1. **安装虚拟机软件**:
   - Parallels Desktop (付费)
   - VMware Fusion (免费/付费)
   - VirtualBox (免费)

2. **创建 Windows 虚拟机**:
   - 安装 Windows 10/11
   - 分配至少 4GB 内存
   - 分配至少 20GB 磁盘

3. **在虚拟机中打包**:
```cmd
# 在 Windows 虚拟机中
git clone <repository-url>
cd webpexchange
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
python build.py --platform windows
```

4. **共享文件夹**:
   - 配置虚拟机共享文件夹
   - 将打包好的 exe 复制到 Mac

### 优缺点
✅ 完全控制打包环境
❌ 占用大量资源（内存、磁盘）
❌ 需要 Windows 许可证
❌ 设置复杂

---

## 方案4: 借用 Windows 机器 ⭐⭐

### 使用朋友/同事的 Windows 电脑

#### 步骤
1. **克隆代码到 Windows 电脑**:
```cmd
git clone https://github.com/YOUR_USERNAME/webpexchange.git
cd webpexchange
```

2. **打包**:
```cmd
# 双击运行
build.bat

# 或手动执行
python build.py
```

3. **获取文件**:
   - 将 `dist/WebPConverter.exe` 复制到 U 盘
   - 或通过网络共享
   - 或上传到云盘

---

## 方案5: 云服务打包 ⭐⭐⭐

### 使用云 Windows 机器

#### AWS / Azure / Google Cloud
1. 创建 Windows 虚拟机实例
2. 通过远程桌面连接
3. 安装 Python 和依赖
4. 打包应用
5. 下载到本地

#### 优缺点
✅ 按需使用，不占用本地资源
❌ 需要付费
❌ 设置复杂

---

## 💡 最佳实践建议

### 个人项目（推荐顺序）
1. **GitHub Actions**（免费、自动化）
2. 借用 Windows 机器（临时方案）
3. Docker（如果有 Docker Desktop）

### 商业项目（推荐顺序）
1. **GitHub Actions + Private Repo**
2. **Jenkins + 专用打包机器**
3. **云服务**（AWS/Azure）

---

## 📊 方案成本对比

| 方案 | 成本 | 时间成本 | 适用场景 |
|------|------|---------|---------|
| GitHub Actions | 免费（公开仓库） | 5-10分钟 | 开源项目 |
| GitHub Actions | $4/月起（私有仓库） | 5-10分钟 | 私有项目 |
| Docker | 免费 | 10-20分钟 | 本地开发 |
| Parallels Desktop | $99/年 | 需要一次性设置 | 经常需要 |
| VirtualBox | 免费 | 需要一次性设置 | 偶尔需要 |
| 云服务 | $0.10-0.50/小时 | 按需 | 临时需要 |

---

## 🚀 快速开始：GitHub Actions

**最简单的跨平台打包方案**：

```bash
# 1. 推送到 GitHub
git remote add origin https://github.com/YOUR_USERNAME/webpexchange.git
git push -u origin main

# 2. 在 GitHub 网页上触发 Actions
# 访问: https://github.com/YOUR_USERNAME/webpexchange/actions
# 点击 "Build Multi-Platform Apps" -> "Run workflow"

# 3. 等待 5-10 分钟

# 4. 下载打包好的文件
# Mac: WebPConverter-macOS.zip
# Windows: WebPConverter-Windows.zip
# Linux: WebPConverter-Linux.tar.gz
```

**就这么简单！** 🎉

---

## ❓ 常见问题

### Q1: 我必须用 GitHub Actions 吗？
**A**: 不必须，但强烈推荐。GitHub Actions 是最简单、免费的多平台打包方案。

### Q2: GitHub Actions 收费吗？
**A**: 公开仓库完全免费。私有仓库每月有 2000 分钟免费额度。

### Q3: Docker 方案为什么不推荐？
**A**:
- Windows 容器镜像很大（5-10GB）
- Mac M1/M2 芯片兼容性问题
- 配置相对复杂

### Q4: 我能用 Wine 在 Mac 上运行 Windows Python 吗？
**A**: 理论上可以，但：
- 非常不稳定
- 兼容性差
- 不推荐生产使用

### Q5: 我应该如何选择？
**A**:
- **有 GitHub 仓库** → GitHub Actions
- **本地打包，有 Docker** → Docker 方案
- **偶尔需要** → 借用 Windows 机器
- **经常需要** → 虚拟机

---

## 📝 总结

**在 Mac 下构建 Windows exe 文件的最佳方案**:

🥇 **GitHub Actions**（推荐）
- 免费、自动化、支持所有平台
- 配置文件已创建: `.github/workflows/build.yml`

🥈 **Docker**（备选）
- 本地打包，但镜像较大
- 配置文件已创建: `Dockerfile.windows`, `docker-build.sh`

🥉 **虚拟机**（传统方案）
- 完全控制，但资源占用大

---

**推荐**: 直接使用 GitHub Actions，5 分钟搞定所有平台打包！

**下一步**: 参考上面的"快速开始"章节，立即体验 GitHub Actions 打包。

---

**最后更新**: 2025-10-22
