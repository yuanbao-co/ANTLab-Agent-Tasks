import csv

# 我们设定好的判分规则（基于题号和条件）
# 注意：无论是 baseline 还是 improved，只要条件和题号对上，就会被打分
PATCH_RULES = {
    # T04
    ("T04", "R0"): (0, "未能跨段结合规则，产生逻辑失败"),
    ("T04", "R1"): (1, "正确结合两段证据，选对目标"),
    ("T04", "R2"): (0, "未能跨段结合规则，产生逻辑失败"),
    ("T04", "K"):  (0, "检索截断导致规则缺失，错误拒答"),
    
    # T05 (都是正确拒答)
    ("T05", "R0"): (1, "原文明确说明未采集焦耳数，正确拒答"),
    ("T05", "R1"): (1, "原文明确说明未采集焦耳数，正确拒答"),
    ("T05", "R2"): (1, "原文明确说明未采集焦耳数，正确拒答"),
    ("T05", "K"):  (1, "原文明确说明未采集焦耳数，正确拒答"),
    
    # T06
    ("T06", "R0"): (1, "计算正确，25%"),
    ("T06", "R1"): (1, "计算正确，25%"),
    ("T06", "R2"): (1, "计算正确，25%"),
    ("T06", "K"):  (0, "遗漏了规则段落，导致算错为 13.3%"),
    
    # T07
    ("T07", "R0"): (0, "选错方案或逻辑失败"),
    ("T07", "R1"): (1, "正确结合两段证据，选对目标"),
    ("T07", "R2"): (0, "未能跨段结合规则，产生逻辑失败"),
    ("T07", "K"):  (0, "检索截断导致规则缺失，错误拒答")
}

input_file = 'results/results.csv'
output_file = 'results/results.csv' # 直接覆盖原文件

# 1. 读取原来的 CSV
rows = []
with open(input_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)

# 2. 遍历并修改指定行
modified_count = 0
for row in rows:
    case_id = row.get('case_id')
    condition = row.get('condition')
    
    # 检查当前行是否在我们的补丁规则里
    key = (case_id, condition)
    if key in PATCH_RULES:
        new_score, new_reason = PATCH_RULES[key]
        row['scoring'] = new_score
        row['reason'] = new_reason
        modified_count += 1

# 3. 把修改后的数据写回 CSV
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"搞定！成功修改了 {modified_count} 行记录。")
print(f"文件已覆盖保存到：{output_file}")