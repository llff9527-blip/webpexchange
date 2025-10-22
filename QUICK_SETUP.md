# 🚀 GitHub Actions 快速设置（3分钟完成）

## 📋 你需要什么

- ✅ GitHub 账号（如果没有，访问 https://github.com/signup 免费注册）
- ✅ 项目代码已提交（已完成 ✅）

---

## 🎯 方法1: 自动设置（推荐）

### 运行自动化脚本

```bash
./setup-github.sh
```

然后按照提示：
1. **输入GitHub用户名**: 例如 `llff` 或 `yourname`
2. **输入仓库名**: 按回车使用默认 `webpexchange`
3. **确认**: 输入 `y`

脚本会自动：
- ✅ 添加远程仓库
- ✅ 推送代码
- ✅ 打开 GitHub Actions 页面

---

## 🎯 方法2: 手动设置（3步）

### 步骤1: 创建GitHub仓库 (1分钟)

1. **打开浏览器访问**: https://github.com/new

2. **填写信息**:
   - Repository name: `webpexchange`
   - Description: `WebP图片转换器 - 跨平台桌面应用`
   - 可见性: ✅ Public（公开，免费使用Actions）
   - ❌ **不要**勾选 "Add a README file"
   - ❌ **不要**选择 .gitignore
   - ❌ **不要**选择 license

3. **点击**: `Create repository`

### 步骤2: 推送代码 (1分钟)

**重要**: 替换下面的 `YOUR_USERNAME` 为你的GitHub用户名

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/webpexchange.git

# 推送代码
git push -u origin 001-webp-image-converter
```

**如果提示需要认证**:
- 用户名: 你的GitHub用户名
- 密码: **不是**GitHub密码，需要使用 Personal Access Token
  - 获取Token: https://github.com/settings/tokens
  - 点击 "Generate new token (classic)"
  - 勾选 `repo` 权限
  - 生成后复制，在密码处粘贴

### 步骤3: 触发打包 (30秒)

1. **访问**: https://github.com/YOUR_USERNAME/webpexchange/actions

2. **点击左侧**: `Build Multi-Platform Apps`

3. **点击右侧**: `Run workflow` 按钮

4. **选择分支**: `001-webp-image-converter`

5. **点击**: 绿色的 `Run workflow` 按钮

6. **等待**: 5-10分钟，自动打包完成

---

## 📥 下载打包文件

打包完成后（显示绿色 ✅）:

1. **点击完成的 workflow 运行**

2. **向下滚动到 Artifacts 区域**

3. **下载文件**:
   - `WebPConverter-macOS` → 解压得到 .app
   - `WebPConverter-Windows` → 解压得到 .exe ✅
   - `WebPConverter-Linux` → 解压得到 binary

---

## 🎉 完成！

现在你可以：
- ✅ 在Mac上开发
- ✅ 自动打包 Windows/Mac/Linux 应用
- ✅ 无需 Windows 电脑
- ✅ 完全免费

---

## 💡 提示

### 以后如何打包新版本？

#### 方法A: 手动触发（推荐）
```bash
# 1. 修改代码并提交
git add .
git commit -m "修复bug"
git push

# 2. 访问 Actions 页面手动触发
# https://github.com/YOUR_USERNAME/webpexchange/actions
```

#### 方法B: 自动触发
```bash
# 创建版本标签，自动触发打包和发布
git tag v1.0.1
git push origin v1.0.1

# GitHub 会自动:
# 1. 打包所有平台
# 2. 创建 Release
# 3. 上传文件
```

---

## ❓ 常见问题

### Q1: 推送时提示 "Authentication failed"
**A**: 你需要使用 Personal Access Token，不是密码
- 访问: https://github.com/settings/tokens
- 生成新token
- 勾选 `repo` 权限
- 复制token，在密码处粘贴

### Q2: 推送时提示 "Permission denied"
**A**: 使用 HTTPS 而不是 SSH
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/webpexchange.git
```

### Q3: 找不到 "Run workflow" 按钮
**A**:
1. 确保代码已推送成功
2. 刷新 Actions 页面
3. 点击左侧的 "Build Multi-Platform Apps" workflow
4. 按钮在右侧上方

### Q4: Actions 打包失败
**A**:
1. 点击失败的运行
2. 查看红色的步骤
3. 查看错误日志
4. 常见原因:
   - 依赖安装失败 → 检查 requirements.txt
   - 文件路径错误 → 检查 build.py

### Q5: 我想用私有仓库
**A**: 可以！
- 创建 Private 仓库
- 每月有 2000 分钟免费额度
- 足够使用（一次打包约10-15分钟）

---

## 📞 需要帮助？

**遇到问题**:
1. 查看上面的常见问题
2. 查看 GITHUB_ACTIONS_GUIDE.md
3. GitHub Issues: https://github.com/YOUR_USERNAME/webpexchange/issues

---

## 🎯 现在就开始！

**选择你的方式**:

### 🤖 自动设置（最简单）
```bash
./setup-github.sh
```

### ✋ 手动设置（完全控制）
参考上面的"方法2: 手动设置"

---

**预计耗时**: 3-5分钟
**难度**: ⭐⭐ (非常简单)

**开始吧！** 🚀
