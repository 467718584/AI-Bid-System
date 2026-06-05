#!/usr/bin/env python3
"""彻底修复所有标书的MD表格 - 支持多种格式"""

import subprocess
import re

def convert_all_md_tables(content):
    """转换所有MD表格格式为HTML"""
    if not content:
        return content, 0
    
    tables_converted = 0
    offset = 0
    
    # 方法1: 处理 <p>|...|</p> 格式 (已经被<p>包裹)
    content, cnt1 = convert_p_wrapped_tables(content)
    tables_converted += cnt1
    
    # 方法2: 处理原始MD格式 |col1|col2| (没有<p>包裹)
    content, cnt2 = convert_raw_md_tables(content)
    tables_converted += cnt2
    
    return content, tables_converted

def convert_p_wrapped_tables(content):
    """转换 <p>|col1|col2|</p> 格式"""
    tables_converted = 0
    offset = 0
    
    header_pattern = re.compile(r'<p>\|([^<]+)\|</p>\s*<p>\|[-:|\s]+\|</p>')
    
    for match in header_pattern.finditer(content):
        header_line = match.group(1).strip()
        if '|' not in header_line:
            continue
        
        headers = [c.strip() for c in header_line.split('|') if c.strip()]
        if len(headers) < 2:
            continue
        
        # 收集数据行
        pos = match.end()
        rows = []
        max_rows = 50
        
        while pos < len(content) and len(rows) < max_rows:
            next_p = content.find('<p>', pos)
            if next_p == -1:
                break
            next_p_end = content.find('</p>', next_p)
            if next_p_end == -1:
                break
            
            cell_line = content[next_p + 3:next_p_end].strip()
            next_pos = next_p_end + 4
            
            if '|' in cell_line:
                if re.match(r'^[-:|\s]+$', cell_line):
                    pos = next_pos
                    continue
                cells = [c.strip() for c in cell_line.split('|') if c.strip()]
                if cells:
                    rows.append(cells)
                    pos = next_pos
                    continue
            break
        
        if not rows:
            continue
        
        # 生成HTML
        table_html = '<table style="border-collapse:collapse;width:100%;margin:16px 0;">'
        table_html += '<thead><tr>'
        for h in headers:
            table_html += f'<th style="border:1px solid #ddd;padding:8px 12px;background:#f5f5f5;font-weight:600;">{h}</th>'
        table_html += '</tr></thead><tbody>'
        for row in rows:
            table_html += '<tr>'
            for cell in row:
                table_html += f'<td style="border:1px solid #ddd;padding:8px 12px;">{cell}</td>'
            table_html += '</tr>'
        table_html += '</tbody></table>'
        
        original_block = content[match.start():pos]
        content = content[:match.start()] + table_html + content[pos:]
        tables_converted += 1
    
    return content, tables_converted

def convert_raw_md_tables(content):
    """转换原始MD格式 |col1|col2| (没有<p>包裹)"""
    tables_converted = 0
    
    # 匹配: | header1 | header2 | 后跟 |---|后跟 | val1 | val2 |
    # 这是标准的MD表格格式，行之间有换行
    raw_pattern = re.compile(r'\|([^\n|]+)\|\s*\n\s*\|[-:|\s]+\|\s*\n((?:\|[^\n|]+\|\s*\n?)*)')
    
    for match in raw_pattern.finditer(content):
        header_line = match.group(1).strip()
        body_lines = match.group(2).strip()
        
        if '|' not in header_line:
            continue
        
        headers = [c.strip() for c in header_line.split('|') if c.strip()]
        if len(headers) < 2:
            continue
        
        # 解析数据行
        rows = []
        for line in body_lines.split('\n'):
            line = line.strip()
            if not line or not line.startswith('|'):
                continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells and any('|' in c or '-' in c for c in cells):
                continue  # 跳过分隔行
            if cells and not re.match(r'^[-:|\s]+$', '|'.join(cells)):
                rows.append(cells)
        
        if not rows:
            continue
        
        # 生成HTML
        table_html = '<table style="border-collapse:collapse;width:100%;margin:16px 0;">'
        table_html += '<thead><tr>'
        for h in headers:
            table_html += f'<th style="border:1px solid #ddd;padding:8px 12px;background:#f5f5f5;font-weight:600;">{h}</th>'
        table_html += '</tr></thead><tbody>'
        for row in rows:
            table_html += '<tr>'
            for cell in row:
                table_html += f'<td style="border:1px solid #ddd;padding:8px 12px;">{cell}</td>'
            table_html += '</tr>'
        table_html += '</tbody></table>'
        
        content = content[:match.start()] + table_html + content[match.end():]
        tables_converted += 1
    
    return content, tables_converted

def main():
    print("=== 彻底修复所有MD表格 ===\n")
    
    # 查找所有标书
    result = subprocess.run([
        'psql', '-U', 'postgres', '-d', 'ai_bid', '-h', 'localhost',
        '-t', '-c', "SELECT id, name FROM bid_project WHERE deleted = 0;"
    ], capture_output=True, text=True, env={'PGPASSWORD': 'postgres'})
    
    bids = []
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                bids.append((parts[0].strip(), parts[1].strip()))
    
    print(f"检查 {len(bids)} 个标书...\n")
    
    total_converted = 0
    
    for bid_id, bid_name in bids:
        content_result = subprocess.run([
            'psql', '-U', 'postgres', '-d', 'ai_bid', '-h', 'localhost',
            '-t', '-c', f"SELECT content FROM bid_project WHERE id = {bid_id};"
        ], capture_output=True, text=True, env={'PGPASSWORD': 'postgres'})
        
        content = content_result.stdout.strip()
        if not content:
            continue
        
        new_content, cnt = convert_all_md_tables(content)
        
        if cnt > 0:
            subprocess.run([
                'psql', '-U', 'postgres', '-d', 'ai_bid', '-h', 'localhost',
                '-c', f"UPDATE bid_project SET content = $$ {new_content} $$ WHERE id = {bid_id};"
            ], capture_output=True, text=True, env={'PGPASSWORD': 'postgres'})
            print(f"✅ {bid_name}: 转换了{cnt}个表格")
            total_converted += cnt
    
    print(f"\n总计转换: {total_converted} 个表格")

if __name__ == "__main__":
    main()