#!/bin/bash

# NFO文件解析器依赖安装脚本
# 此脚本帮助安装HTML和PDF功能所需的依赖

echo "=========================================="
echo "NFO文件解析器依赖安装脚本"
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
    echo "未识别的系统类型，请手动安装依赖"
    exit 1
fi

echo ""
echo "正在安装Python依赖包..."

# 安装Python包
case $SYSTEM_TYPE in
    "debian")
        echo "使用apt安装依赖..."
        sudo apt update
        sudo apt install -y python3-markdown python3-pdfkit
        echo "安装wkhtmltopdf..."
        sudo apt install -y wkhtmltopdf
        echo "安装中文字体支持..."
        sudo apt install -y fonts-noto-cjk fonts-wqy-zenhei fonts-wqy-microhei
        ;;
    "redhat")
        echo "使用yum安装依赖..."
        sudo yum install -y python3-markdown python3-pdfkit
        echo "安装wkhtmltopdf..."
        sudo yum install -y wkhtmltopdf
        echo "安装中文字体支持..."
        sudo yum install -y google-noto-cjk-fonts wqy-zenhei-fonts wqy-microhei-fonts
        ;;
    "macos")
        echo "使用brew安装依赖..."
        brew install python-markdown pdfkit
        echo "安装wkhtmltopdf..."
        brew install wkhtmltopdf
        ;;
esac

echo ""
echo "=========================================="
echo "依赖安装完成！"
echo "=========================================="

# 测试安装
echo "测试依赖安装..."

python3 -c "
try:
    import markdown
    print('✓ markdown库安装成功')
except ImportError:
    print('✗ markdown库安装失败')

try:
    import pdfkit
    print('✓ pdfkit库安装成功')
except ImportError:
    print('✗ pdfkit库安装失败')

try:
    import subprocess
    result = subprocess.run(['wkhtmltopdf', '--version'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print('✓ wkhtmltopdf工具安装成功')
    else:
        print('✗ wkhtmltopdf工具安装失败')
except Exception as e:
    print(f'✗ wkhtmltopdf工具测试失败: {e}')
"

echo ""
echo "现在您可以使用以下命令生成PDF："
echo "python3 nfo_parser.py -f pdf"
echo ""
echo "或者生成所有格式："
echo "python3 nfo_parser.py -f all"
