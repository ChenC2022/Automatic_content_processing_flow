#!/bin/bash

# 中文字体安装脚本
# 解决PDF生成中文显示问题

echo "=========================================="
echo "中文字体安装脚本"
echo "解决PDF中文显示问题"
echo "=========================================="

# 检查系统类型
if command -v apt &> /dev/null; then
    echo "检测到Debian/Ubuntu系统"
    SYSTEM_TYPE="debian"
elif command -v yum &> /dev/null; then
    echo "检测到RedHat/CentOS系统"
    SYSTEM_TYPE="redhat"
elif command -v brew &> /dev/null; then
    echo "检测到macOS系统"
    SYSTEM_TYPE="macos"
else
    echo "未识别的系统类型，请手动安装中文字体"
    exit 1
fi

echo ""
echo "正在安装中文字体..."

# 安装中文字体
case $SYSTEM_TYPE in
    "debian")
        echo "使用apt安装中文字体..."
        sudo apt update
        sudo apt install -y fonts-noto-cjk fonts-wqy-zenhei fonts-wqy-microhei
        echo "刷新字体缓存..."
        sudo fc-cache -fv
        ;;
    "redhat")
        echo "使用yum安装中文字体..."
        sudo yum install -y google-noto-cjk-fonts wqy-zenhei-fonts wqy-microhei-fonts
        echo "刷新字体缓存..."
        sudo fc-cache -fv
        ;;
    "macos")
        echo "macOS系统通常已包含中文字体"
        echo "如果需要额外字体，请运行："
        echo "brew install font-noto-cjk"
        ;;
esac

echo ""
echo "=========================================="
echo "字体安装完成！"
echo "=========================================="

# 验证字体安装
echo "验证中文字体安装..."
if command -v fc-list &> /dev/null; then
    font_count=$(fc-list :lang=zh | wc -l)
    if [ $font_count -gt 0 ]; then
        echo "✓ 检测到 $font_count 个中文字体"
        echo "可用的中文字体："
        fc-list :lang=zh | head -5
    else
        echo "✗ 未检测到中文字体"
    fi
else
    echo "无法验证字体安装（fc-list命令不可用）"
fi

echo ""
echo "现在您可以重新生成PDF文件："
echo "python3 nfo_parser.py -f pdf"
echo ""
echo "如果PDF中文仍然显示异常，请："
echo "1. 重启系统"
echo "2. 检查PDF阅读器是否支持中文字体"
echo "3. 尝试使用不同的PDF阅读器"
