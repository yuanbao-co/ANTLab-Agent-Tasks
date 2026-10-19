import json
import glob
import os

print("### 📊 基础题 R0 vs Improved 配对对照表\n")
# ================= 1. 处理基础题 =================
b_dict, i_dict = {}, {}

for path in glob.glob('基础/runs/*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    case = d.get('case') or d.get('case_id')
    # 只提取评测题 T01-T08
    if not case or not str(case).startswith('T'): continue
    
    # 提取答案
    ans = ""
    resp = d.get('response', {})
    if isinstance(resp, dict) and 'choices' in resp:
        try:
            content = resp['choices'][0]['message']['content']
            ans = json.loads(content).get('answer', '')
        except: pass
        
    record = {
        'answer': ans,
        'elapsed': float(d.get('elapsed_seconds', 0) or 0)
    }
    
    if d.get('variant') == 'improved': i_dict[case] = record
    else: b_dict[case] = record

print("| 题目 | 基线答案 | 改进答案 | 结论变化 | 基线耗时(s) | 改进耗时(s) | 耗时差异 |")
print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
for task in sorted(b_dict.keys()):
    if task not in i_dict: continue
    b, i = b_dict[task], i_dict[task]
    change = "未变" if b['answer'] == i['answer'] else "**改变**"
    diff = i['elapsed'] - b['elapsed']
    print(f"| {task} | {str(b['answer'])[:15]} | {str(i['answer'])[:15]} | {change} | {b['elapsed']:.2f} | {i['elapsed']:.2f} | {diff:+.2f} |")


print("\n### 📊 进阶A题 Baseline vs Improved 配对对照表\n")
# ================= 2. 处理进阶题 =================
b_adv, i_adv = {}, {}

# 进阶题的 JSON 都在 runs_adv 里
for path in glob.glob('进阶/runs_adv/*.json'):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    task = d.get('task_id')
    if not task: continue
    
    record = {
        'status': d.get('support_status', 'N/A'),
        'elapsed': float(d.get('elapsed_ms', 0) or 0),
        'page': d.get('evidence', {}).get('page', 'N/A')
    }
    
    if d.get('mode') == 'improved': i_adv[task] = record
    else: b_adv[task] = record

print("| 题目 | 基线状态 | 改进状态 | 结论变化 | 基线定位 | 改进定位 | 耗时差异(ms) |")
print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
for task in sorted(b_adv.keys()):
    if task not in i_adv: continue
    b, i = b_adv[task], i_adv[task]
    change = "未变" if b['status'] == i['status'] else "**改变**"
    diff = i['elapsed'] - b['elapsed']
    print(f"| {task} | {b['status']} | {i['status']} | {change} | {b['page']} | {i['page']} | {diff:+.0f} |")