# PDF功能安装说明

## 问题说明

如果您尝试生成PDF格式时遇到"PDF功能不可用"的提示，这是因为缺少必要的依赖库。

## 解决方案

### 方法一：使用系统包管理器（推荐）

#### Ubuntu/Debian系统
```bash
sudo apt update
sudo apt install python3-markdown python3-pdfkit wkhtmltopdf
# 安装中文字体支持（解决PDF中文显示问题）
sudo apt install fonts-noto-cjk fonts-wqy-zenhei fonts-wqy-microhei
```

#### CentOS/RHEL系统
```bash
sudo yum install python3-markdown python3-pdfkit wkhtmltopdf
# 安装中文字体支持（解决PDF中文显示问题）
sudo yum install google-noto-cjk-fonts wqy-zenhei-fonts wqy-microhei-fonts
```

#### macOS系统
```bash
brew install python-markdown pdfkit wkhtmltopdf
```

### 方法二：使用pip（需要虚拟环境）

由于现代Linux系统使用外部管理的Python环境，建议使用虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv nfo_parser_env

# 激活虚拟环境
source nfo_parser_env/bin/activate

# 安装依赖
pip install markdown pdfkit

# 安装wkhtmltopdf工具（系统级安装）
# Ubuntu/Debian: sudo apt install wkhtmltopdf
# CentOS/RHEL: sudo yum install wkhtmltopdf
# macOS: brew install wkhtmltopdf

# 使用程序
python3 nfo_parser.py -f pdf

# 退出虚拟环境
deactivate
```

## 验证安装

安装完成后，可以运行以下命令验证：

```bash
# 测试Python库
python3 -c "import markdown, pdfkit; print('依赖安装成功')"

# 测试wkhtmltopdf工具
wkhtmltopdf --version
```

## 使用PDF功能

安装依赖后，您就可以使用PDF功能了：

```bash
# 生成PDF格式
python3 nfo_parser.py -f pdf

# 生成所有格式（包括PDF）
python3 nfo_parser.py -f all
```

## 替代方案

如果无法安装PDF依赖，您仍然可以：

1. **使用HTML格式**：`python3 nfo_parser.py -f html`
2. **使用Markdown格式**：`python3 nfo_parser.py -f md`
3. **在浏览器中打印HTML为PDF**：生成HTML后，在浏览器中打开并选择"打印为PDF"

## 故障排除

### 常见问题

1. **权限不足**：确保有sudo权限来安装系统包
2. **网络问题**：确保网络连接正常，可以下载包
3. **包不存在**：某些旧版本系统可能没有这些包，请更新系统

### PDF中文显示问题

如果生成的PDF文件中中文显示为方块或乱码，这是字体问题：

#### 问题原因
- 系统中没有安装中文字体
- wkhtmltopdf无法找到合适的中文字体

#### 解决方案

**Ubuntu/Debian系统：**
```bash
# 安装中文字体包
sudo apt install fonts-noto-cjk fonts-wqy-zenhei fonts-wqy-microhei

# 刷新字体缓存
sudo fc-cache -fv

# 验证字体安装
fc-list :lang=zh
```

**CentOS/RHEL系统：**
```bash
# 安装中文字体包
sudo yum install google-noto-cjk-fonts wqy-zenhei-fonts wqy-microhei-fonts

# 刷新字体缓存
sudo fc-cache -fv
```

**macOS系统：**
```bash
# macOS通常已包含中文字体，如果仍有问题：
brew install font-noto-cjk
```

**Windows系统：**
- Windows系统通常已包含中文字体（Microsoft YaHei、SimSun等）
- 如果仍有问题，请确保系统语言设置为中文

#### 验证修复
安装字体后，重新运行程序生成PDF：
```bash
python3 nfo_parser.py -f pdf
```

程序会自动检测中文字体支持并给出相应提示。

### 获取帮助

如果遇到问题，可以：
1. 查看程序的详细错误信息
2. 检查系统版本和包管理器
3. 尝试使用虚拟环境安装

---

*最后更新：2025-09-30*
