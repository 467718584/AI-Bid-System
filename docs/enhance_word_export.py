#!/usr/bin/env python3
"""
增强Word导出功能 - 支持HTML表格和模板样式
修改 ai-bid-ai 的 ExportDocumentStage，使用 styled_exporter 的 HTML 解析能力
"""

import os
import sys
import re

# 查找 pipeline_stages.py
def find_file(name):
    for root, dirs, files in os.walk('/home/zzy/.openclaw/workspace/workspace-bid'):
        if name in files:
            return os.path.join(root, name)
    return None

pipeline_file = find_file('pipeline_stages.py')
print(f"Found pipeline_stages.py: {pipeline_file}")

if not pipeline_file:
    print("ERROR: pipeline_stages.py not found")
    sys.exit(1)

# 读取文件
with open(pipeline_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经增强
if 'add_html_content' in content:
    print("Already has HTML export capability")
else:
    print("Need to enhance Word export")

# 找到 ExportDocumentStage 类
export_pattern = r'class ExportDocumentStage.*?(?=\n\nclass |\Z)'
match = re.search(export_pattern, content, re.DOTALL)
if not match:
    print("Could not find ExportDocumentStage class")
    sys.exit(1)

old_class = match.group(0)
print(f"Found class length: {len(old_class)}")

# 打印当前的 process 方法
process_pattern = r'def process\(self, state\):.*?(?=\n        (?:def |class |\Z))'
process_match = re.search(process_pattern, old_class, re.DOTALL)
if process_match:
    print(f"Found process method:\n{process_match.group(0)[:500]}")
else:
    print("Could not find process method")