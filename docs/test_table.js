#!/usr/bin/env node
/**
 * Test MD table parsing with the correct separator regex
 */

const content = '<p>| 目标类别 | 具体指标 |</p><p>|---------|---------|</p><p>| 数据汇聚 | 整合30+部门数据 |</p><p>| 政务服务 | 实现100% |</p><p>其他内容</p>';

console.log('=== Test 1: Separator regex fix ===');
// Old broken: <p>\|[-:\s]+\|</p>  
// New fixed: <p>\|[-:|\s]+\|</p>  (added | inside character class)
// Or even better: <p>\|[-: \t|-]+\|</p>

const sepTest = content.match(/<p>\|[-:|\s]+\|<\/p>/);
console.log('Fixed separator match:', sepTest);

// Header + separator match
const headerRegex = /<p>\|([^<]+)\|<\/p>\s*<p>\|[-:|\s]+\|<\/p>/g;
let match;
while ((match = headerRegex.exec(content)) !== null) {
  console.log('\nHeader+Sep found:', match[0]);
  const headers = match[1].split('|').map(c => c.trim()).filter(c => c);
  console.log('Headers:', headers);
  
  // Now find body rows - everything until next non-row element
  const startPos = match.index + match[0].length;
  const rest = content.substring(startPos);
  console.log('Rest after header+sep:', rest.substring(0, 80));
  
  // Find all <p>|cells|</p> until we hit something that is NOT a table row
  const bodyRows = [];
  const bodyRegex = /<p>\|([^<]+)\|<\/p>/g;
  let bodyMatch;
  let lastEnd = 0;
  while ((bodyMatch = bodyRegex.exec(rest)) !== null) {
    const line = bodyMatch[1].trim();
    // Stop if we hit separator line
    if (line.match(/^[-:|\s]+$/)) break;
    // Stop if we hit non-table content
    if (!line.includes('|')) break;
    const cells = line.split('|').map(c => c.trim()).filter(c => c);
    if (cells.length > 0) {
      bodyRows.push(cells);
    }
    lastEnd = bodyRegex.lastIndex;
  }
  console.log('Body rows:', bodyRows);
  
  // Build table
  if (headers.length > 0) {
    let tableHtml = '<table>';
    tableHtml += '<thead><tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr></thead>';
    tableHtml += '<tbody>';
    bodyRows.forEach(row => {
      tableHtml += '<tr>' + row.map(c => `<td>${c}</td>`).join('') + '</tr>';
    });
    tableHtml += '</tbody></table>';
    console.log('\nGenerated HTML:', tableHtml);
  }
}

console.log('\n=== Test 2: Full function simulation ===');

// Simulate the new approach
function parseMdTable(html) {
  const headerRegex = /<p>\|([^<]+)\|<\/p>\s*<p>\|[-:|\s]+\|<\/p>/g;
  let result = html;
  let match;
  
  while ((match = headerRegex.exec(html)) !== null) {
    const fullMatch = match[0];
    const headerLine = match[1];
    const headers = headerLine.split('|').map(c => c.trim()).filter(c => c);
    
    // Find body rows
    const startPos = match.index + fullMatch.length;
    const rest = html.substring(startPos);
    const bodyRows = [];
    
    const bodyRegex = /<p>\|([^<]+)\|<\/p>/g;
    let bodyMatch;
    while ((bodyMatch = bodyRegex.exec(rest)) !== null) {
      const line = bodyMatch[1].trim();
      if (line.match(/^[-:|\s]+$/) || !line.includes('|')) break;
      const cells = line.split('|').map(c => c.trim()).filter(c => c);
      if (cells.length > 0) bodyRows.push(cells);
    }
    
    if (headers.length === 0) continue;
    
    let tableHtml = '<table style="border-collapse:collapse;width:100%;margin:16px 0;">';
    tableHtml += '<thead><tr>';
    headers.forEach(h => { tableHtml += `<th style="border:1px solid #ddd;padding:8px 12px;background:#f5f5f5;font-weight:600;">${h}</th>`; });
    tableHtml += '</tr></thead><tbody>';
    bodyRows.forEach(row => {
      tableHtml += '<tr>';
      row.forEach(cell => { tableHtml += `<td style="border:1px solid #ddd;padding:8px 12px;">${cell}</td>`; });
      tableHtml += '</tr>';
    });
    tableHtml += '</tbody></table>';
    
    result = result.replace(fullMatch + rest.substring(0, bodyMatch.index + bodyMatch[0].length), tableHtml);
    break; // Only process first table for now
  }
  
  return result;
}

const input = '<p>| 目标类别 | 具体指标 |</p><p>|---------|---------|</p><p>| 数据汇聚 | 整合30+部门数据 |</p><p>| 政务服务 | 实现100% |</p><p>其他内容</p>';
const output = parseMdTable(input);
console.log('Input:', input);
console.log('Output:', output);
console.log('Success:', output.includes('<table') && output.includes('</table>'));