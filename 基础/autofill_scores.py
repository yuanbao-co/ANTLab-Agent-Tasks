import csv
import os

# 设定文件路径
csv_path = os.path.join('results', 'results.csv')

if not os.path.exists(csv_path):
    print("找不到 results/results.csv 文件，请检查路径！")
    exit()

# 读取数据
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

# 如果表里没有 scoring 和 reason，就自动加上
if 'scoring' not in fieldnames:
    fieldnames.extend(['scoring', 'reason'])

# 自动判分逻辑
for row in rows:
    status = row.get('status', '').strip()
    content = row.get('content', '').strip()
    
    if status != 'ok':
        row['scoring'] = '0'
        row['reason'] = '非正式有效请求或网络错误'
    elif '证据不足' in content:
        row['scoring'] = '0'
        row['reason'] = '模型判定证据不足'
    elif 'answer' in content:
        row['scoring'] = '1'
        row['reason'] = '模型给出回答且附带引用'
    else:
        row['scoring'] = '0'
        row['reason'] = '格式异常或未解析到答案'

# 保存回文件
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("搞定！已经自动填好 scoring 和 reason 列，并保存到 results.csv")