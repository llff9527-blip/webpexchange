# GitHub Actions 快速上手指南

## 🚀 5分钟完成所有平台打包

### 步骤1: 推送代码到 GitHub

```bash
cd /Users/llff/Projects/webpexchange

# 如果还没有远程仓库，创建一个
# 1. 访问 https://github.com/new
# 2. 创建仓库名为 "webpexchange"
# 3. 不要初始化 README

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/webpexchange.git

# 推送代码
git add .
git commit -m "Add GitHub Actions workflow"
git push -u origin main
```

如果遇到分支名问题：
```bash
# 如果你的默认分支是 master，改为 main
git branch -M main
git push -u origin main
```

### 步骤2: 手动触发打包

1. **访问你的仓库**: `https://github.com/YOUR_USERNAME/webpexchange`

2. **点击 Actions 标签页**

3. **选择 "Build Multi-Platform Apps" workflow**

4. **点击 "Run workflow" 按钮**
   - 选择分支: `main`
   - 点击绿色的 "Run workflow" 按钮

### 步骤3: 等待打包完成（约5-10分钟）

GitHub 会自动在3个平台上打包：
- ✅ macOS (macos-latest)
- ✅ Windows (windows-latest)
- ✅ Linux (ubuntu-latest)

你会看到3个任务同时运行：
```
Build on macos-latest   ⏳ 运行中...
Build on windows-latest ⏳ 运行中...
Build on ubuntu-latest  ⏳ 运行中...
```

### 步骤4: 下载打包文件

打包完成后（全部显示绿色✅）：

1. **点击完成的 workflow 运行**
2. **向下滚动到 "Artifacts" 区域**
3. **下载文件**:
   - `WebPConverter-macOS` (包含 .app)
   - `WebPConverter-Windows` (包含 .exe) ✅
   - `WebPConverter-Linux` (包含 binary)

---

## 🎯 自动发布版本（可选）

如果你想自动发布到 GitHub Releases：

```bash
# 创建并推送版本标签
git tag v1.0.0
git push origin v1.0.0
```

这会：
- ✅ 自动触发打包
- ✅ 创建 GitHub Release
- ✅ 上传所有平台的文件

---

## 📊 实时查看打包过程

在 Actions 页面，点击运行中的任务：
- 可以看到实时日志
- 查看每个步骤的进度
- 如果失败，可以看到详细错误

---

## ❓ 常见问题

### Q1: 我没有 GitHub 账号怎么办？
**A**:
1. 访问 https://github.com/signup
2. 免费注册
3. 验证邮箱即可

### Q2: Actions 额度够用吗？
**A**:
- **公开仓库**: 完全免费，无限制
- **私有仓库**: 每月 2000 分钟免费
- 一次打包约 10-15 分钟（3个平台并行）

### Q3: 如果打包失败怎么办？
**A**:
1. 点击失败的任务
2. 查看红色的步骤
3. 点击查看详细日志
4. 常见问题：
   - 依赖安装失败 → 检查 requirements.txt
   - 打包失败 → 检查 build.py 路径

### Q4: 能否在本地 Mac 上测试 workflow？
**A**:
可以使用 `act` 工具模拟 GitHub Actions：
```bash
brew install act
act -j build
```
但仍然无法运行 Windows 容器。

### Q5: 我想私密打包怎么办？
**A**:
创建私有仓库，每月有 2000 分钟免费额度，足够使用。

---

## 🎉 完成！

现在你可以：
- ✅ 在 Mac 上开发
- ✅ 推送到 GitHub
- ✅ 自动打包 Windows/Mac/Linux 应用
- ✅ 下载所有平台的文件

**无需 Windows 电脑，无需虚拟机，完全免费！**

---

## 📝 提示

**每次发布新版本**:
```bash
# 1. 修改代码
git add .
git commit -m "Update version to 1.0.1"
git push

# 2. 创建版本标签
git tag v1.0.1
git push origin v1.0.1

# 3. GitHub 自动打包并发布
```

**就这么简单！** 🚀
