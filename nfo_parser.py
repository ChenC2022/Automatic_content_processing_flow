#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFO文件解析器
自动扫描指定目录下的所有nfo文件，提取title、tag、plot信息并生成markdown文件
"""

import os
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime
import webbrowser
import tempfile

# 尝试导入可选依赖
try:
    import markdown
    import pdfkit
    MARKDOWN_AVAILABLE = True
    PDFKIT_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    PDFKIT_AVAILABLE = False


class NfoParser:
    """NFO文件解析器类"""
    
    def __init__(self, base_directory: str):
        """
        初始化解析器
        
        Args:
            base_directory: 要扫描的基础目录路径
        """
        self.base_directory = Path(base_directory)
        self.video_data = []
        
    def find_nfo_files(self) -> List[Path]:
        """
        递归查找所有nfo文件
        
        Returns:
            nfo文件路径列表
        """
        nfo_files = []
        if not self.base_directory.exists():
            print(f"错误：目录 {self.base_directory} 不存在")
            return nfo_files
            
        # 递归查找所有.nfo文件
        for nfo_file in self.base_directory.rglob("*.nfo"):
            nfo_files.append(nfo_file)
            
        print(f"找到 {len(nfo_files)} 个nfo文件")
        return nfo_files
    
    def parse_nfo_file(self, nfo_path: Path) -> Optional[Dict[str, str]]:
        """
        解析单个nfo文件
        
        Args:
            nfo_path: nfo文件路径
            
        Returns:
            包含title、tag、plot的字典，解析失败返回None
        """
        try:
            with open(nfo_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # 尝试解析为XML
            try:
                root = ET.fromstring(content)
                return self._parse_xml_nfo(root, nfo_path)
            except ET.ParseError:
                # 如果不是标准XML，尝试正则表达式解析
                return self._parse_text_nfo(content, nfo_path)
                
        except Exception as e:
            print(f"解析文件 {nfo_path} 时出错: {e}")
            return None
    
    def _parse_xml_nfo(self, root: ET.Element, nfo_path: Path) -> Dict[str, str]:
        """
        解析XML格式的nfo文件
        
        Args:
            root: XML根元素
            nfo_path: 文件路径
            
        Returns:
            包含解析数据的字典
        """
        data = {
            'title': '',
            'tag': '',
            'plot': '',
            'file_path': str(nfo_path),
            'directory': str(nfo_path.parent)
        }
        
        # 提取title
        title_elem = root.find('title')
        if title_elem is not None and title_elem.text:
            data['title'] = title_elem.text.strip()
        
        # 提取tag
        tag_elem = root.find('tag')
        if tag_elem is not None and tag_elem.text:
            data['tag'] = tag_elem.text.strip()
        
        # 提取plot
        plot_elem = root.find('plot')
        if plot_elem is not None and plot_elem.text:
            data['plot'] = plot_elem.text.strip()
            
        return data
    
    def _parse_text_nfo(self, content: str, nfo_path: Path) -> Dict[str, str]:
        """
        使用正则表达式解析文本格式的nfo文件
        
        Args:
            content: 文件内容
            nfo_path: 文件路径
            
        Returns:
            包含解析数据的字典
        """
        data = {
            'title': '',
            'tag': '',
            'plot': '',
            'file_path': str(nfo_path),
            'directory': str(nfo_path.parent)
        }
        
        # 使用正则表达式提取信息
        title_pattern = r'<title>(.*?)</title>'
        tag_pattern = r'<tag>(.*?)</tag>'
        plot_pattern = r'<plot>(.*?)</plot>'
        
        title_match = re.search(title_pattern, content, re.DOTALL)
        if title_match:
            data['title'] = title_match.group(1).strip()
        
        tag_match = re.search(tag_pattern, content, re.DOTALL)
        if tag_match:
            data['tag'] = tag_match.group(1).strip()
        
        plot_match = re.search(plot_pattern, content, re.DOTALL)
        if plot_match:
            data['plot'] = plot_match.group(1).strip()
            
        return data
    
    def process_all_nfo_files(self) -> List[Dict[str, str]]:
        """
        处理所有nfo文件
        
        Returns:
            所有解析数据的列表
        """
        nfo_files = self.find_nfo_files()
        processed_data = []
        
        for nfo_file in nfo_files:
            print(f"正在处理: {nfo_file}")
            data = self.parse_nfo_file(nfo_file)
            if data and data['title']:  # 只添加有标题的数据
                processed_data.append(data)
            else:
                print(f"跳过无效文件: {nfo_file}")
        
        self.video_data = processed_data
        print(f"成功处理 {len(processed_data)} 个有效文件")
        return processed_data
    
    def _generate_anchor(self, text: str) -> str:
        """
        生成markdown锚点链接，与Markdown自动生成的锚点格式兼容
        
        Args:
            text: 要生成锚点的文本
            
        Returns:
            锚点字符串
        """
        import re
        # 移除特殊字符，保留中文、英文、数字和空格
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        # 将空格替换为连字符
        anchor = re.sub(r'\s+', '-', anchor.strip())
        return anchor.lower()
    
    def generate_markdown(self, output_file: str = None) -> str:
        """
        生成markdown文件
        
        Args:
            output_file: 输出文件路径，默认为当前目录下的汇总文件
            
        Returns:
            生成的markdown内容
        """
        if not self.video_data:
            print("没有数据可生成markdown")
            return ""
        
        # 生成markdown内容
        markdown_content = []
        markdown_content.append("# 心理科普视频内容汇总")
        markdown_content.append("")
        markdown_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_content.append(f"总计视频数量: {len(self.video_data)}")
        markdown_content.append("")
        
        # 生成目录（无跳转链接）
        markdown_content.append("## 📋 目录")
        markdown_content.append("")
        
        # 按类型分组生成目录
        categorized_data = {}
        for item in self.video_data:
            tag = item['tag'] if item['tag'] else '未分类'
            if tag not in categorized_data:
                categorized_data[tag] = []
            categorized_data[tag].append(item)
        
        # 生成目录结构（无跳转链接）
        for tag, items in sorted(categorized_data.items()):
            markdown_content.append(f"### {tag}")
            for item in items:
                markdown_content.append(f"- {item['title']}")
            markdown_content.append("")
        
        markdown_content.append("---")
        markdown_content.append("")
        
        # 按视频生成内容，每个视频一个独立章节
        for item in self.video_data:
            # 视频标题作为二级标题
            markdown_content.append(f"## 视频标题：{item['title']}")
            markdown_content.append("")
            
            # 类型作为三级标题
            tag = item['tag'] if item['tag'] else '未分类'
            markdown_content.append(f"### 视频类型：{tag}")
            markdown_content.append("")
            
            # 概要部分
            markdown_content.append("### 视频概要")
            if item['plot']:
                # 格式化plot内容，保持原有的换行和缩进
                plot_lines = item['plot'].split('\n')
                for line in plot_lines:
                    if line.strip():
                        markdown_content.append(line)
                    else:
                        markdown_content.append("")
            else:
                markdown_content.append("暂无概要信息")
            
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")
        
        markdown_text = '\n'.join(markdown_content)
        
        # 写入文件
        if output_file is None:
            output_file = self.base_directory / "心理科普视频内容汇总.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        print(f"Markdown文件已生成: {output_file}")
        return markdown_text
    
    def generate_html(self, output_file: str = None) -> str:
        """
        生成HTML文件
        
        Args:
            output_file: 输出文件路径，默认为当前目录下的汇总文件
            
        Returns:
            生成的HTML内容
        """
        if not self.video_data:
            print("没有数据可生成HTML")
            return ""
        
        # 首先生成带跳转功能的markdown内容
        markdown_content = self._generate_markdown_content_with_toc()
        
        if MARKDOWN_AVAILABLE:
            # 使用markdown库转换为HTML
            html_content = markdown.markdown(markdown_content, extensions=['toc', 'tables', 'fenced_code'])
            # 修复锚点格式
            html_content = self._fix_anchor_links(html_content)
        else:
            # 简单的markdown到HTML转换
            html_content = self._simple_markdown_to_html(markdown_content)
        
        # 添加HTML模板
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>心理科普视频内容汇总</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .toc {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .video-section {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
        }}
        ul, ol {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        .meta-info {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
        
        # 写入文件
        if output_file is None:
            output_file = self.base_directory / "心理科普视频内容汇总.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"HTML文件已生成: {output_file}")
        return full_html
    
    def generate_pdf(self, output_file: str = None) -> str:
        """
        生成PDF文件（无章节跳转功能）
        
        Args:
            output_file: 输出文件路径，默认为当前目录下的汇总文件
            
        Returns:
            生成的PDF文件路径
        """
        if not self.video_data:
            print("没有数据可生成PDF")
            return ""
        
        if not PDFKIT_AVAILABLE:
            print("错误：需要安装pdfkit库来生成PDF文件")
            print("请运行：pip install pdfkit")
            print("或者使用HTML格式输出")
            return ""
        
        # 生成无跳转功能的HTML内容
        html_content = self._generate_html_no_toc()
        
        # 写入文件
        if output_file is None:
            output_file = self.base_directory / "心理科普视频内容汇总.pdf"
        
        try:
            # 检查中文字体支持
            self._check_chinese_fonts()
            
            # 配置PDF选项，优化中文支持
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
                'print-media-type': None,  # 优化打印媒体类型
                'disable-smart-shrinking': None,  # 禁用智能缩放以保持格式
                'load-error-handling': 'ignore',  # 忽略加载错误
                'load-media-error-handling': 'ignore',  # 忽略媒体加载错误
                'no-outline': None,  # 禁用大纲
                'disable-external-links': None,  # 禁用外部链接
                'disable-forms': None,  # 禁用表单
                'disable-javascript': None,  # 禁用JavaScript
                'quiet': None,  # 静默模式
            }
            
            # 生成PDF
            pdfkit.from_string(html_content, str(output_file), options=options)
            print(f"PDF文件已生成: {output_file}")
            print("PDF包含目录结构，但不包含跳转功能")
            return str(output_file)
            
        except Exception as e:
            print(f"生成PDF时出错: {e}")
            print("请确保已安装wkhtmltopdf")
            return ""
    
    def _generate_markdown_content(self) -> str:
        """
        生成markdown内容（内部方法）
        
        Returns:
            markdown内容字符串
        """
        if not self.video_data:
            return ""
        
        # 生成markdown内容
        markdown_content = []
        markdown_content.append("# 心理科普视频内容汇总")
        markdown_content.append("")
        markdown_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_content.append(f"总计视频数量: {len(self.video_data)}")
        markdown_content.append("")
        
        # 生成目录（无跳转链接）
        markdown_content.append("## 📋 目录")
        markdown_content.append("")
        
        # 按类型分组生成目录
        categorized_data = {}
        for item in self.video_data:
            tag = item['tag'] if item['tag'] else '未分类'
            if tag not in categorized_data:
                categorized_data[tag] = []
            categorized_data[tag].append(item)
        
        # 生成目录结构（无跳转链接）
        for tag, items in sorted(categorized_data.items()):
            markdown_content.append(f"### {tag}")
            for item in items:
                markdown_content.append(f"- {item['title']}")
            markdown_content.append("")
        
        markdown_content.append("---")
        markdown_content.append("")
        
        # 按视频生成内容，每个视频一个独立章节
        for item in self.video_data:
            # 视频标题作为二级标题
            markdown_content.append(f"## 视频标题：{item['title']}")
            markdown_content.append("")
            
            # 类型作为三级标题
            tag = item['tag'] if item['tag'] else '未分类'
            markdown_content.append(f"### 视频类型：{tag}")
            markdown_content.append("")
            
            # 概要部分
            markdown_content.append("### 视频概要")
            if item['plot']:
                # 格式化plot内容，保持原有的换行和缩进
                plot_lines = item['plot'].split('\n')
                for line in plot_lines:
                    if line.strip():
                        markdown_content.append(line)
                    else:
                        markdown_content.append("")
            else:
                markdown_content.append("暂无概要信息")
            
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")
        
        return '\n'.join(markdown_content)
    
    def _generate_markdown_content_with_toc(self) -> str:
        """
        生成带跳转功能的markdown内容（用于HTML生成）
        
        Returns:
            markdown内容字符串
        """
        if not self.video_data:
            return ""
        
        # 生成markdown内容
        markdown_content = []
        markdown_content.append("# 心理科普视频内容汇总")
        markdown_content.append("")
        markdown_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_content.append(f"总计视频数量: {len(self.video_data)}")
        markdown_content.append("")
        
        # 生成目录
        markdown_content.append("## 📋 目录")
        markdown_content.append("")
        
        # 按类型分组生成目录
        categorized_data = {}
        for item in self.video_data:
            tag = item['tag'] if item['tag'] else '未分类'
            if tag not in categorized_data:
                categorized_data[tag] = []
            categorized_data[tag].append(item)
        
        # 生成目录结构（带跳转链接）
        for tag, items in sorted(categorized_data.items()):
            markdown_content.append(f"### {tag}")
            for item in items:
                anchor = self._generate_anchor(item['title'])
                markdown_content.append(f"- [{item['title']}](#{anchor})")
            markdown_content.append("")
        
        markdown_content.append("---")
        markdown_content.append("")
        
        # 按视频生成内容，每个视频一个独立章节
        for item in self.video_data:
            # 生成锚点ID
            anchor = self._generate_anchor(item['title'])
            
            # 视频标题作为二级标题，Markdown会自动生成锚点
            markdown_content.append(f"## 视频标题：{item['title']}")
            markdown_content.append("")
            
            # 类型作为三级标题
            tag = item['tag'] if item['tag'] else '未分类'
            markdown_content.append(f"### 视频类型：{tag}")
            markdown_content.append("")
            
            # 概要部分
            markdown_content.append("### 视频概要")
            if item['plot']:
                # 格式化plot内容，保持原有的换行和缩进
                plot_lines = item['plot'].split('\n')
                for line in plot_lines:
                    if line.strip():
                        markdown_content.append(line)
                    else:
                        markdown_content.append("")
            else:
                markdown_content.append("暂无概要信息")
            
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")
        
        return '\n'.join(markdown_content)
    
    def _simple_markdown_to_html(self, markdown_text: str) -> str:
        """
        简单的markdown到HTML转换（备用方案）
        
        Args:
            markdown_text: markdown文本
            
        Returns:
            HTML文本
        """
        html = markdown_text
        
        # 标题转换
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # 链接转换
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # 列表转换
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # 分隔线转换
        html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
        
        # 段落转换
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            if p.strip() and not p.strip().startswith('<'):
                html_paragraphs.append(f'<p>{p.strip()}</p>')
            else:
                html_paragraphs.append(p)
        html = '\n\n'.join(html_paragraphs)
        
        return html
    
    def _fix_anchor_links(self, html_content: str) -> str:
        """
        修复HTML中的锚点链接
        
        Args:
            html_content: HTML内容
            
        Returns:
            修复后的HTML内容
        """
        # 清理所有现有的锚点格式
        html_content = re.sub(r'\{#([^}]+)\}', '', html_content)
        html_content = re.sub(r'id="[^"]*"', '', html_content)
        
        # 为每个视频标题添加正确的锚点
        def add_title_anchor(match):
            title_text = match.group(1)
            anchor = self._generate_anchor(title_text)
            return f'<h2 id="{anchor}">视频标题：{title_text}</h2>'
        
        # 修复视频标题的锚点
        html_content = re.sub(r'<h2[^>]*>视频标题：([^<]+)</h2>', add_title_anchor, html_content)
        
        # 修复目录中的链接，确保指向正确的锚点
        def fix_toc_link(match):
            link_text = match.group(1)
            anchor = self._generate_anchor(link_text)
            return f'<a href="#{anchor}">{link_text}</a>'
        
        # 修复目录中的链接
        html_content = re.sub(r'<a href="#[^"]*">([^<]+)</a>', fix_toc_link, html_content)
        
        return html_content
    
    def _generate_html_no_toc(self) -> str:
        """
        生成无跳转功能的HTML内容（用于PDF生成）
        
        Returns:
            生成的HTML内容
        """
        if not self.video_data:
            return ""
        
        # 首先生成markdown内容（无跳转）
        markdown_content = self._generate_markdown_content()
        
        if MARKDOWN_AVAILABLE:
            # 使用markdown库转换为HTML
            html_content = markdown.markdown(markdown_content, extensions=['toc', 'tables', 'fenced_code'])
        else:
            # 简单的markdown到HTML转换
            html_content = self._simple_markdown_to_html(markdown_content)
        
        # 添加HTML模板
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>心理科普视频内容汇总</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        ul, ol {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        .meta-info {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
        
        return full_html
    
    def _generate_html_with_toc_for_pdf(self) -> str:
        """
        生成带跳转功能的HTML内容（专门用于PDF生成）
        
        Returns:
            生成的HTML内容
        """
        if not self.video_data:
            return ""
        
        # 生成HTML内容，不使用markdown库，直接构建HTML以确保PDF兼容性
        html_content = self._build_html_content_for_pdf()
        
        # 添加专门为PDF优化的HTML模板
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>心理科普视频内容汇总</title>
    <style>
        @font-face {{
            font-family: 'ChineseFont';
            src: local('Noto Sans CJK SC'), local('Source Han Sans SC'), local('PingFang SC'), local('Hiragino Sans GB'), local('Microsoft YaHei'), local('SimSun'), local('WenQuanYi Micro Hei');
        }}
        body {{
            font-family: 'ChineseFont', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            color: #333;
        }}
        .container {{
            background-color: white;
            padding: 30px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-after: avoid;
            margin-top: 0;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            page-break-after: avoid;
        }}
        h3 {{
            color: #7f8c8d;
            page-break-after: avoid;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .toc {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        .video-section {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        ul, ol {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
            page-break-after: avoid;
        }}
        .meta-info {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        /* PDF优化样式 */
        @media print {{
            body {{
                font-size: 12pt;
                line-height: 1.4;
            }}
            h1 {{
                font-size: 18pt;
                page-break-before: avoid;
            }}
            h2 {{
                font-size: 14pt;
                page-break-before: auto;
            }}
            h3 {{
                font-size: 12pt;
            }}
            .toc {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
        
        return full_html
    
    def _build_html_content_for_pdf(self) -> str:
        """
        直接构建HTML内容，确保PDF锚点链接正确工作
        
        Returns:
            HTML内容字符串
        """
        html_parts = []
        
        # 标题和元信息
        html_parts.append('<h1>心理科普视频内容汇总</h1>')
        html_parts.append(f'<div class="meta-info">生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>')
        html_parts.append(f'<div class="meta-info">总计视频数量: {len(self.video_data)}</div>')
        
        # 生成目录
        html_parts.append('<h2>📋 目录</h2>')
        html_parts.append('<div class="toc">')
        
        # 按类型分组生成目录
        categorized_data = {}
        for item in self.video_data:
            tag = item['tag'] if item['tag'] else '未分类'
            if tag not in categorized_data:
                categorized_data[tag] = []
            categorized_data[tag].append(item)
        
        # 生成目录结构（带跳转链接）
        for tag, items in sorted(categorized_data.items()):
            html_parts.append(f'<h3>{tag}</h3>')
            html_parts.append('<ul>')
            for item in items:
                anchor = self._generate_anchor(item['title'])
                # 使用简单的锚点链接，确保PDF兼容性
                html_parts.append(f'<li><a href="#{anchor}">{item["title"]}</a></li>')
            html_parts.append('</ul>')
        
        html_parts.append('</div>')
        html_parts.append('<hr>')
        
        # 按视频生成内容，每个视频一个独立章节
        for item in self.video_data:
            # 生成锚点ID
            anchor = self._generate_anchor(item['title'])
            
            # 视频标题作为二级标题，添加锚点
            html_parts.append(f'<h2 id="{anchor}">视频标题：{item["title"]}</h2>')
            
            # 类型作为三级标题
            tag = item['tag'] if item['tag'] else '未分类'
            html_parts.append(f'<h3>视频类型：{tag}</h3>')
            
            # 概要部分
            html_parts.append('<h3>视频概要</h3>')
            if item['plot']:
                # 格式化plot内容，保持原有的换行和缩进
                plot_lines = item['plot'].split('\n')
                for line in plot_lines:
                    if line.strip():
                        html_parts.append(f'<p>{line}</p>')
                    else:
                        html_parts.append('<br>')
            else:
                html_parts.append('<p>暂无概要信息</p>')
            
            html_parts.append('<hr>')
        
        return '\n'.join(html_parts)
    
    def _check_chinese_fonts(self):
        """
        检查系统中是否安装了中文字体
        """
        import subprocess
        import platform
        
        system = platform.system().lower()
        chinese_fonts = []
        
        try:
            if system == 'linux':
                # 检查Linux系统中的中文字体
                result = subprocess.run(['fc-list', ':lang=zh'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    chinese_fonts = result.stdout.strip().split('\n')
            elif system == 'darwin':  # macOS
                # 检查macOS系统中的中文字体
                result = subprocess.run(['system_profiler', 'SPFontsDataType'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # 简单的字体检查
                    chinese_fonts = ['PingFang SC', 'Hiragino Sans GB']  # macOS通常有这些字体
            elif system == 'windows':
                # Windows通常有中文字体
                chinese_fonts = ['Microsoft YaHei', 'SimSun']
            
            if not chinese_fonts:
                print("警告：未检测到中文字体，PDF中的中文可能显示为方块")
                print("建议安装中文字体：")
                print("  Ubuntu/Debian: sudo apt install fonts-noto-cjk")
                print("  CentOS/RHEL:   sudo yum install google-noto-cjk-fonts")
                print("  macOS:         系统通常已包含中文字体")
                print("  Windows:       系统通常已包含中文字体")
            else:
                print(f"检测到中文字体支持，共找到 {len(chinese_fonts)} 个字体")
                
        except Exception as e:
            print(f"字体检查失败: {e}")
            print("如果PDF中文显示异常，请确保系统已安装中文字体")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NFO文件解析器 - 生成心理科普视频内容汇总')
    parser.add_argument('directory', nargs='?', 
                       default='/run/user/1000/gvfs/smb-share:server=10.86.230.130,share=home/my_projects/ShenY',
                       help='要扫描的目录路径 (默认: 当前项目目录)')
    parser.add_argument('-o', '--output', 
                       help='输出文件路径 (默认: 目录下的心理科普视频内容汇总.{format})')
    parser.add_argument('-f', '--format', 
                       choices=['md', 'html', 'pdf', 'all'], 
                       default='md',
                       help='输出格式: md=Markdown, html=HTML, pdf=PDF, all=所有格式 (默认: md)')
    parser.add_argument('--open', action='store_true',
                       help='生成HTML后自动在浏览器中打开')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("NFO文件解析器启动")
    print("=" * 60)
    print(f"扫描目录: {args.directory}")
    print(f"输出格式: {args.format}")
    
    # 检查依赖
    if args.format in ['html', 'pdf', 'all'] and not MARKDOWN_AVAILABLE:
        print("警告：未安装markdown库，HTML和PDF功能可能受限")
        print("建议运行：pip install markdown")
    
    if args.format in ['pdf', 'all'] and not PDFKIT_AVAILABLE:
        print("警告：未安装pdfkit库，PDF功能不可用")
        print("")
        print("安装方法：")
        print("1. 使用系统包管理器（推荐）：")
        print("   Ubuntu/Debian: sudo apt install python3-pdfkit wkhtmltopdf")
        print("   CentOS/RHEL:   sudo yum install python3-pdfkit wkhtmltopdf")
        print("   macOS:         brew install pdfkit wkhtmltopdf")
        print("")
        print("2. 使用pip（需要虚拟环境）：")
        print("   pip install pdfkit")
        print("   然后安装wkhtmltopdf工具")
        print("")
        if args.format == 'pdf':
            print("将改为生成HTML格式")
            args.format = 'html'
    
    # 创建解析器实例
    nfo_parser = NfoParser(args.directory)
    
    # 处理所有nfo文件
    video_data = nfo_parser.process_all_nfo_files()
    
    if video_data:
        print("=" * 60)
        print("开始生成文件...")
        print("=" * 60)
        
        # 根据格式生成文件
        if args.format == 'md' or args.format == 'all':
            output_file = args.output
            if output_file and not output_file.endswith('.md'):
                output_file += '.md'
            nfo_parser.generate_markdown(output_file)
        
        if args.format == 'html' or args.format == 'all':
            output_file = args.output
            if output_file and not output_file.endswith('.html'):
                output_file += '.html'
            html_file = nfo_parser.generate_html(output_file)
            
            # 如果指定了--open参数，在浏览器中打开HTML文件
            if args.open and html_file:
                try:
                    webbrowser.open(f'file://{Path(html_file).absolute()}')
                    print(f"已在浏览器中打开: {html_file}")
                except Exception as e:
                    print(f"无法在浏览器中打开文件: {e}")
        
        if args.format == 'pdf' or args.format == 'all':
            if PDFKIT_AVAILABLE:
                output_file = args.output
                if output_file and not output_file.endswith('.pdf'):
                    output_file += '.pdf'
                nfo_parser.generate_pdf(output_file)
            else:
                print("跳过PDF生成（缺少依赖）")
        
        print("=" * 60)
        print("处理完成！")
        print("=" * 60)
        
        # 显示使用提示
        if args.format == 'all':
            print("已生成以下格式的文件：")
            print("- Markdown (.md)")
            print("- HTML (.html)")
            if PDFKIT_AVAILABLE:
                print("- PDF (.pdf)")
        elif args.format == 'html':
            print("提示：使用 --open 参数可以在生成HTML后自动在浏览器中打开")
    else:
        print("没有找到有效的nfo文件")


if __name__ == "__main__":
    main()
