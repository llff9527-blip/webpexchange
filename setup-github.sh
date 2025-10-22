#!/bin/bash
# GitHub Actions 自动设置脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo ""
    echo -e "${BLUE}${BOLD}========================================${NC}"
    echo -e "${BLUE}${BOLD}  $1${NC}"
    echo -e "${BLUE}${BOLD}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_header "GitHub Actions 自动设置"

# 步骤1: 检查是否已经有远程仓库
print_info "检查远程仓库..."
if git remote get-url origin >/dev/null 2>&1; then
    REMOTE_URL=$(git remote get-url origin)
    print_success "已配置远程仓库: $REMOTE_URL"

    # 提取仓库信息
    if [[ $REMOTE_URL =~ github.com[:/]([^/]+)/([^/]+)(\.git)?$ ]]; then
        USERNAME="${BASH_REMATCH[1]}"
        REPO="${BASH_REMATCH[2]}"
        REPO="${REPO%.git}"  # 移除.git后缀
        print_success "GitHub用户名: $USERNAME"
        print_success "仓库名: $REPO"
    fi
else
    print_warning "未配置远程仓库"
    echo ""
    print_info "请按照以下步骤操作:"
    echo ""
    echo -e "${YELLOW}步骤1: 创建GitHub仓库${NC}"
    echo "  1. 访问: https://github.com/new"
    echo "  2. 仓库名: webpexchange (或自定义)"
    echo "  3. 可见性: Public (公开) 或 Private (私有)"
    echo "  4. ❌ 不要勾选 'Initialize this repository with a README'"
    echo "  5. 点击 'Create repository'"
    echo ""
    echo -e "${YELLOW}步骤2: 获取仓库URL${NC}"
    echo "  创建后会看到一个URL，类似："
    echo "  https://github.com/YOUR_USERNAME/webpexchange.git"
    echo ""

    # 询问用户
    read -p "$(echo -e ${BLUE}请输入你的GitHub用户名: ${NC})" USERNAME
    read -p "$(echo -e ${BLUE}请输入仓库名 [webpexchange]: ${NC})" REPO
    REPO=${REPO:-webpexchange}

    # 构建URL
    REMOTE_URL="https://github.com/${USERNAME}/${REPO}.git"

    echo ""
    print_info "将添加远程仓库: $REMOTE_URL"
    read -p "$(echo -e ${YELLOW}确认正确吗? (y/n): ${NC})" -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "已取消"
        exit 1
    fi

    # 添加远程仓库
    print_info "添加远程仓库..."
    git remote add origin "$REMOTE_URL"
    print_success "远程仓库已添加"
fi

# 步骤2: 确保在正确的分支
print_info "检查分支..."
CURRENT_BRANCH=$(git branch --show-current)
print_info "当前分支: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    print_warning "当前分支不是 main 或 master"
    read -p "$(echo -e ${YELLOW}是否切换到 main 分支? (y/n): ${NC})" -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -M main
        CURRENT_BRANCH="main"
        print_success "已切换到 main 分支"
    fi
fi

# 步骤3: 推送代码
print_info "推送代码到 GitHub..."
echo ""
print_warning "如果这是第一次推送，可能需要输入 GitHub 凭据"
print_info "GitHub 现在需要使用 Personal Access Token (PAT)，而不是密码"
print_info "如何获取 PAT: https://github.com/settings/tokens"
echo ""

if git push -u origin "$CURRENT_BRANCH"; then
    print_success "代码推送成功！"
else
    print_error "推送失败"
    echo ""
    print_info "常见问题解决:"
    echo "  1. 如果提示认证失败:"
    echo "     - 访问: https://github.com/settings/tokens"
    echo "     - 点击 'Generate new token (classic)'"
    echo "     - 勾选 'repo' 权限"
    echo "     - 生成后复制token"
    echo "     - 在密码处粘贴这个token（不是GitHub密码）"
    echo ""
    echo "  2. 如果仓库不存在:"
    echo "     - 访问: https://github.com/new"
    echo "     - 创建仓库: $REPO"
    echo ""
    echo "  3. 或者使用 SSH:"
    echo "     git remote set-url origin git@github.com:${USERNAME}/${REPO}.git"
    echo "     git push -u origin $CURRENT_BRANCH"
    echo ""
    exit 1
fi

# 步骤4: 提供访问链接
print_header "✅ GitHub Actions 设置完成！"

REPO_URL="https://github.com/${USERNAME}/${REPO}"
ACTIONS_URL="${REPO_URL}/actions"

echo ""
print_success "🎉 恭喜！所有文件已推送到GitHub"
echo ""
print_info "下一步操作:"
echo ""
echo -e "${BOLD}1. 访问 GitHub Actions:${NC}"
echo -e "   ${BLUE}${ACTIONS_URL}${NC}"
echo ""
echo -e "${BOLD}2. 触发自动打包:${NC}"
echo "   a) 点击左侧 'Build Multi-Platform Apps'"
echo "   b) 点击右侧 'Run workflow' 按钮"
echo "   c) 选择分支: $CURRENT_BRANCH"
echo "   d) 点击绿色 'Run workflow' 按钮"
echo ""
echo -e "${BOLD}3. 等待打包完成 (约5-10分钟)${NC}"
echo "   - macOS 应用 (.app)"
echo "   - Windows 应用 (.exe) ✅"
echo "   - Linux 应用 (binary)"
echo ""
echo -e "${BOLD}4. 下载打包文件:${NC}"
echo "   a) 打包完成后，点击完成的workflow运行"
echo "   b) 向下滚动到 'Artifacts' 区域"
echo "   c) 下载所需的平台文件"
echo ""
print_info "或者使用浏览器打开: $ACTIONS_URL"
echo ""

# 尝试自动打开浏览器
if command_exists open; then
    read -p "$(echo -e ${YELLOW}是否现在打开GitHub Actions页面? (y/n): ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$ACTIONS_URL"
        print_success "已在浏览器中打开"
    fi
fi

echo ""
print_success "🚀 GitHub Actions 已经准备就绪！"
echo ""
print_info "提示: 以后每次推送代码后，都可以在 Actions 页面手动触发打包"
print_info "或者通过创建 tag 自动触发: git tag v1.0.0 && git push origin v1.0.0"
echo ""
