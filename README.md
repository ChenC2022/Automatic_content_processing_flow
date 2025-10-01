# NFO文件解析器使用说明

## 功能简介

这个自动化程序可以帮您扫描指定目录下的所有nfo文件，提取其中的标题(title)、分类(tag)、概要(plot)信息，并自动生成多种格式的汇总文件。

## 主要特性

- 🔍 **自动扫描**：递归扫描指定目录及其子目录中的所有.nfo文件
- 📝 **智能解析**：支持多种nfo文件格式（XML格式和文本格式）
- 📊 **分类整理**：按tag字段自动分类整理内容
- 📄 **多格式输出**：支持Markdown、HTML、PDF三种格式输出
- 🎨 **美观样式**：HTML和PDF格式包含专业的样式设计
- 🔗 **目录导航**：自动生成可点击的目录（HTML格式支持跳转）
- 🛡️ **错误处理**：对无效文件进行跳过处理，确保程序稳定运行

## 使用方法

### 基本用法

```bash
# 使用默认目录和Markdown格式
python3 nfo_parser.py

# 指定要扫描的目录
python3 nfo_parser.py /path/to/your/directory

# 指定输出格式
python3 nfo_parser.py -f html

# 指定输出文件路径
python3 nfo_parser.py -o /path/to/output.html
```

### 参数说明

- `directory`：要扫描的目录路径（可选，默认为当前项目目录）
- `-f, --format`：输出格式，可选值：`md`（Markdown）、`html`（HTML）、`pdf`（PDF）、`all`（所有格式）
- `-o, --output`：输出文件路径（可选，默认为目录下的"心理科普视频内容汇总.{format}"）
- `--open`：生成HTML后自动在浏览器中打开（仅HTML格式）

### 使用示例

```bash
# 示例1：生成Markdown格式（默认）
python3 nfo_parser.py

# 示例2：生成HTML格式
python3 nfo_parser.py -f html

# 示例3：生成PDF格式
python3 nfo_parser.py -f pdf

# 示例4：生成所有格式
python3 nfo_parser.py -f all

# 示例5：指定目录和输出文件
python3 nfo_parser.py /home/user/videos -f html -o /home/user/视频汇总.html

# 示例6：生成HTML并在浏览器中打开
python3 nfo_parser.py -f html --open

# 示例7：完整参数
python3 nfo_parser.py /home/user/videos -f all -o /home/user/汇总
```

## 输出格式

### Markdown格式 (.md)
- 标准的markdown格式，兼容所有markdown编辑器
- 包含目录结构（跳转功能取决于编辑器支持）
- 适合在GitHub、GitLab等平台查看

### HTML格式 (.html)
- 包含专业的CSS样式设计
- 响应式布局，支持移动设备
- 美观的视觉效果和排版
- 支持目录跳转功能
- 可直接在浏览器中查看

### PDF格式 (.pdf)
- 基于HTML转换生成
- 适合打印和分享
- 保持HTML的样式和布局
- 包含PDF书签导航功能
- 需要安装wkhtmltopdf工具

### 输出示例

```markdown
# 心理科普视频内容汇总

生成时间: 2025-09-30 11:09:45
总计视频数量: 10

## 个人成长

### 1. 指责还是关心 别读错了爱

1) 要点
- 对话围绕某人对另一人能力的不确定性展开。
- 有人表示自己"太没用了"。
- 双方决定共同解决问题。

2) 关键信息与金句
- "你为什么连这点事情都搞不定啊？"
- "你真是不太有用了。"

3) 行动建议
- 遇到困难时，可以寻求他人的帮助。
- 共同面对问题，一起寻找解决方案。

**文件路径**: `/path/to/file.nfo`

---
```

## 支持的NFO文件格式

程序支持两种nfo文件格式：

### 1. 标准XML格式
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
  <title>视频标题</title>
  <tag>分类标签</tag>
  <plot>详细内容描述...</plot>
</movie>
```

### 2. 简化格式
```xml
<movie>
    <title>视频标题</title>
    <tag>分类标签</tag>
    <plot>详细内容描述...</plot>
</movie>
```

## 安装依赖

### 基础功能
程序使用Python标准库，无需安装额外依赖即可使用Markdown格式输出。

### HTML和PDF功能
如需使用HTML和PDF格式，请安装以下依赖：

```bash
# 安装Python依赖
pip install markdown pdfkit

# 或者使用requirements.txt
pip install -r requirements.txt
```

### PDF功能额外要求
生成PDF需要安装wkhtmltopdf工具：

```bash
# Ubuntu/Debian
sudo apt install python3-markdown python3-pdfkit wkhtmltopdf

# CentOS/RHEL
sudo yum install python3-markdown python3-pdfkit wkhtmltopdf

# macOS
brew install python-markdown pdfkit wkhtmltopdf

# Windows
# 下载并安装：https://wkhtmltopdf.org/downloads.html
```

**注意**：如果遇到权限问题或外部管理环境错误，请参考 `PDF功能安装说明.md` 文件获取详细解决方案。

## 已知问题

### 当前版本限制

1. **PDF内部跳转**：PDF文件中的目录链接跳转功能不完善，建议使用PDF阅读器的书签功能进行导航
2. **Markdown跳转**：Markdown文件中的目录跳转功能取决于编辑器的支持程度，某些编辑器可能不支持中文锚点

### 临时解决方案

- **PDF导航**：使用PDF阅读器的书签/大纲面板进行章节导航
- **Markdown导航**：使用支持中文锚点的编辑器（如Typora、Mark Text等）

详细问题记录请参考 [KNOWN_ISSUES.md](KNOWN_ISSUES.md) 文件。

## 注意事项

1. **文件编码**：确保nfo文件使用UTF-8编码
2. **必要字段**：每个nfo文件必须包含`<title>`标签，否则会被跳过
3. **目录权限**：确保程序对目标目录有读取权限
4. **输出权限**：确保程序对输出目录有写入权限
5. **依赖检查**：程序会自动检查依赖并给出相应提示

## 错误处理

- 如果某个nfo文件解析失败，程序会显示错误信息并继续处理其他文件
- 没有title字段的文件会被自动跳过
- 程序会显示处理进度和最终统计信息

## 技术实现

- **语言**：Python 3
- **依赖**：仅使用Python标准库，无需安装额外依赖
- **解析方式**：XML解析 + 正则表达式备用方案
- **文件处理**：递归目录扫描，支持大量文件处理

## 更新和维护

如需修改程序功能，主要可以调整以下部分：

1. **输出格式**：修改`generate_markdown`方法中的markdown模板
2. **解析字段**：在`_parse_xml_nfo`和`_parse_text_nfo`方法中添加新字段
3. **分类逻辑**：修改`generate_markdown`方法中的分类逻辑
4. **文件过滤**：在`find_nfo_files`方法中添加文件过滤条件

## 联系支持

如果您在使用过程中遇到问题，请检查：

1. Python版本是否为3.6+
2. 文件路径是否正确
3. 文件权限是否足够
4. nfo文件格式是否符合要求

---

*最后更新：2025-10-01*

## 版本历史

- **v1.0** (2025-10-01)
  - 修复PDF首页空白页问题
  - 修复PDF锚点链接指向临时文件问题
  - 记录已知的跳转功能问题
  - 完善文档和说明
