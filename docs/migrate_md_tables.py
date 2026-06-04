#!/usr/bin/env python3
"""
迁移标书内容：将MD格式表格转换为HTML格式
直接修改数据库中的content字段
"""

import subprocess
import re

def convert_md_tables_in_content(content):
    """将<p>|col1|col2|</p>格式的MD表格转换为HTML表格"""
    if not content or '<p>|' not in content:
        return content, 0
    
    # 查找所有表头行+分隔行的位置
    header_pattern = re.compile(r'<p>\|([^<]+)\|</p>\s*<p>\|[-:|\s]+\|</p>')
    
    tables_converted = 0
    result = content
    offset = 0  # 因为替换后内容长度变化，需要跟踪偏移
    
    # 使用finditer来跟踪位置
    for match in header_pattern.finditer(content):
        header_line = match.group(1).strip()
        # 确认是有效的表头（多个|）
        if '|' not in header_line:
            continue
        
        headers = [c.strip() for c in header_line.split('|') if c.strip()]
        if len(headers) < 2:
            continue
        
        # 表头匹配的开始位置（考虑已替换的偏移）
        table_start = match.start() + offset
        table_end = match.end() + offset
        
        # 从分隔行之后继续收集数据行
        pos = match.end()
        rows = []
        max_rows = 50
        
        while pos < len(content) and len(rows) < max_rows:
            # 找下一个<p>
            next_p = content.find('<p>', pos)
            if next_p == -1:
                break
            
            next_p_end = content.find('</p>', next_p)
            if next_p_end == -1:
                break
            
            cell_line = content[next_p + 3:next_p_end].strip()
            next_pos = next_p_end + 4
            
            # 检查是否是表格行
            if '|' in cell_line:
                # 跳过分隔行
                if re.match(r'^[-:|\s]+$', cell_line):
                    pos = next_pos
                    continue
                
                # 数据行
                cells = [c.strip() for c in cell_line.split('|') if c.strip()]
                if cells:
                    rows.append(cells)
                    pos = next_pos
                    continue
            
            # 遇到非表格内容，停止
            break
        
        if not rows:
            continue
        
        # 生成HTML表格
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
        
        # 替换原内容
        original_block = content[match.start():pos]
        result = result[:table_start] + table_html + result[table_start + len(original_block):]
        offset += len(table_html) - len(original_block)
        tables_converted += 1
    
    return result, tables_converted

def main():
    print("=== 迁移标书MD表格为HTML ===\n")
    
    # 查询所有包含MD表格的标书
    result = subprocess.run([
        'psql', '-U', 'postgres', '-d', 'ai_bid', '-h', 'localhost',
        '-t', '-c',
        "SELECT id, name FROM bid_project WHERE content LIKE '%<p>|%' AND deleted = 0;"
    ], capture_output=True, text=True, env={'PGPASSWORD': 'postgres'})
    
    bids = []
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                bids.append((parts[0].strip(), parts[1].strip()))
    
    print(f"找到 {len(bids)} 个标书需要检查\n")
    
    migrated = 0
    failed = 0
    
    for bid_id, bid_name in bids:
        # 获取content
        content_result = subprocess.run([
            'psql', '-U', 'postgres', '-d', 'ai_bid', '-h', 'localhost',
            '-t', '-c', f"SELECT content FROM bid_project WHERE id = {bid_id};"
        ], capture_output=True, text=True, env={'PGPASSWORD': 'postgres'})
        
        content = content_result.stdout.strip()
        
        if '<p>|' not in content:
            print(f"⏭️  {bid_name}: 无MD表格")
            continue
        
        # 转换
        new_content, tables_count = convert_md_tables_in_content(content)
        
        if tables_count == 0:
            print(f"⚠️  {bid_name}: 未能转换表格")
            continue
        
        # 检查是否还有MD表格残留
        remaining_md = len(re.findall(r'<p>\|[^<]+\|[^<]*\|', new_content))
        
        # 更新数据库
        update_result = subprocess.run([
            'psql', '-U', 'postgres', '-d', 'ai_bid', '-h', 'localhost',
            '-c', f"UPDATE bid_project SET content = $${new_content}$$ WHERE id = {bid_id};"
        ], capture_output=True, text=True, env={'PGPASSWORD': 'postgres'})
        
        if update_result.returncode == 0:
            print(f"✅ {bid_name}: 转换了{tables_count}个表格" + (f", 残留{remaining_md}处" if remaining_md else ""))
            migrated += 1
        else:
            print(f"❌ {bid_name}: 失败")
            failed += 1
    
    print(f"\n迁移完成: {migrated}成功, {failed}失败")

if __name__ == "__main__":
    main()