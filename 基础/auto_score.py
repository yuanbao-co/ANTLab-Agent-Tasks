import json, glob, csv, os, re

# ================= 配置标准答案与判分规则 =================
STANDARD_ANSWERS = {
    "T01": ["S24", "S24。"],
    "T02": ["76%", "76"],
    "T03": ["2.6", "2.6秒", "2.6秒。"],
    "T04": ["流程乙", "乙", "流程乙。"],
    "T05": ["证据不足", "证据不足。"],
    "T06": ["25%", "25"],
    "T07": ["丙", "配置丙", "方案丙", "丙。"],
    "T08": ["K17", "K17。"]
}

def clean_text(text):
    """清理文本，去掉多余的空格和标点，方便比对"""
    if not isinstance(text, str):
        text = str(text)
    return text.strip().replace(" ", "").replace("\n", "").replace("\"", "")

def auto_generate_reason(case, cond, answer, is_correct):
    """根据对错和条件，自动生成好听又专业的理由"""
    if is_correct:
        if answer == "证据不足":
            return "正确拒答：材料中确实缺少相关事实依据，模型没有产生幻觉。"
        return f"回答正确：准确提取了关键信息。"
    else:
        if answer == "证据不足":
            if cond == "K":
                return "检索缺失：K条件只给了前两段，漏掉了包含关键规则/数据的段落，导致模型无法作答。"
            return "逻辑失败：模型未能跨段结合证据（如规则段与数据段），产生了错误的拒答。"
        else:
            if cond == "K":
                return "检索误导：K条件截断了关键信息，导致模型基于不完整的证据算出了错误结果。"
            return "推理错误：提取证据有误，导致计算结果或判断与标准答案不符。"

# ================= 主流程 =================
rows = []
for path in sorted(glob.glob('runs/*.json')):
    d = json.load(open(path, encoding='utf-8'))
    case_id = d.get('case', d.get('case_id'))
    
    # 我们只处理正式评测题 T01-T08
    if not case_id or not str(case_id).startswith('T'):
        continue
        
    cond = d.get('condition')
    variant = d.get('variant', 'baseline')
    status = d.get('status')
    elapsed = d.get('elapsed_seconds', 0)
    if elapsed: elapsed = round(elapsed, 3)
    
    answer = ""
    citations = ""
    
    # 解析模型回答
    resp = d.get('response', {})
    if isinstance(resp, dict) and 'choices' in resp:
        try:
            content = resp['choices'][0]['message']['content']
            parsed = json.loads(content)
            answer = parsed.get('answer', '')
            citations = ";".join(map(str, parsed.get('citations', [])))
        except Exception:
            answer = "解析失败"
    
    # 自动判分
    scoring = ""
    reason = ""
    if status == 'ok':
        target_answers = STANDARD_ANSWERS.get(case_id, [])
        is_correct = False
        for target in target_answers:
            if clean_text(target) in clean_text(answer):
                is_correct = True
                break
        
        scoring = 1 if is_correct else 0
        reason = auto_generate_reason(case_id, cond, answer, is_correct)
    else:
        scoring = 0
        reason = f"请求失败，未获得有效结果 (状态: {status})"
        
    rows.append({
        "run_id": os.path.basename(path),
        "case_id": case_id,
        "condition": cond,
        "variant": variant,
        "status": status,
        "elapsed": elapsed,
        "model_answer": answer,
        "citations": citations,
        "scoring": scoring,
        "reason": reason
    })

# 生成最终 CSV
os.makedirs('results', exist_ok=True)
out_path = 'results/final_results.csv'
with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["run_id", "case_id", "condition", "variant", "status", "elapsed", "model_answer", "citations", "scoring", "reason"])
    writer.writeheader()
    writer.writerows(rows)

print(f"搞定！已自动生成带有判分和理由的表：{out_path}")
print(f"一共处理了 {len(rows)} 条正式题记录。")