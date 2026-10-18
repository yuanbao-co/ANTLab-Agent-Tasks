import json
import os
import time
import uuid
import requests
import re
import csv
import random

# ========== 配置 ==========
API_KEY = os.environ.get("ASSESSMENT_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-chat"

# ========== 加载数据 ==========
with open('materials/a_tasks.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
with open('materials/sections.json', 'r', encoding='utf-8') as f:
    sections = json.load(f)
with open('materials/page_words.json', 'r', encoding='utf-8') as f:
    page_words_data = json.load(f)

os.makedirs('runs_adv', exist_ok=True)

# ========== 工具函数 ==========
def get_doc_text(doc_id, sections_data, mode="baseline"):
    text = ""
    doc_sections = [sec for sec in sections_data if sec['doc_id'] == doc_id]
    if mode == "improved":
        random.seed(42)
        random.shuffle(doc_sections)
    for sec in doc_sections:
        text += f"\n--- {sec['heading']} ---\n"
        for p in sec['paragraphs']:
            text += p + "\n"
    return text

def clean_word(w):
    return re.sub(r'[^a-z0-9]', '', str(w).lower())

def locate_evidence(evidence_text, doc_id):
    if not evidence_text:
        return None, "absent"
    words = [clean_word(w) for w in evidence_text.split()]
    words = [w for w in words if w][:8]
    if not words:
        return None, "absent"
    
    pages_text = {}
    for item in page_words_data:
        if item.get('doc_id') != doc_id:
            continue
        p = item.get('page')
        t = clean_word(item.get('text', ''))
        pages_text[p] = pages_text.get(p, "") + t
        
    for length in [8, 6, 4]:
        if length > len(words):
            continue
        target_phrase = "".join(words[:length])
        for p, text in pages_text.items():
            if target_phrase in text:
                return p, "valid"
    return None, "invalid"

def build_prompt(claim, doc_text):
    system_prompt = """You are a rigorous scientific fact-checker.
I will give you a CLAIM and a DOCUMENT.
Determine if the DOCUMENT supports the CLAIM.
Output strict JSON only, no markdown formatting. Format:
{
  "support_status": "supported" or "contradicted" or "insufficient",
  "evidence_text": "The exact English sentence(s) from the document that supports your verdict.",
  "reason": "Brief explanation in Chinese."
}
If the evidence is insufficient, set "evidence_text" to "". """
    user_prompt = f"【CLAIM】: {claim}\n\n【DOCUMENT】:\n{doc_text}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

# ========== 批量执行 ==========
csv_rows = []
print(f"总计要跑 {len(tasks)} 道题，每道题 2 种模式。预计 20 次请求...\n")

for task in tasks:
    task_id = task['id']
    claim = task['claim']
    doc_id = task['doc_ids'][0]
    
    for mode in ["baseline", "improved"]:
        print(f"正在跑: {task_id} [{mode}]...")
        doc_text = get_doc_text(doc_id, sections, mode)
        messages = build_prompt(claim, doc_text)
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.0
        }
        
        try:
            resp = requests.post(API_URL, headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            resp_json = resp.json()
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            content = resp_json['choices'][0]['message']['content']
            content = content.replace("```json", "").replace("```", "").strip()
            model_output = json.loads(content)
            
            evidence_text = model_output.get("evidence_text", "")
            page, locator_status = locate_evidence(evidence_text, doc_id)
            
            final_result = {
                "request_id": request_id,
                "task_id": task_id,
                "doc_ids": task['doc_ids'],
                "mode": mode,
                "claim": claim,
                "support_status": model_output.get("support_status", "not_checked"),
                "evidence": {
                    "doc_id": doc_id,
                    "original_text": evidence_text,
                    "page": page
                },
                "locator_status": locator_status,
                "elapsed_ms": elapsed_ms,
                "reason": model_output.get("reason", "")
            }
            
            # 存单次成功 JSON
            with open(f'runs_adv/{task_id}_{mode}_{request_id[:8]}.json', 'w', encoding='utf-8') as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
                
            # 存 CSV 行
            csv_rows.append({
                "task_id": task_id,
                "mode": mode,
                "status": model_output.get("support_status"),
                "page": page,
                "locator": locator_status,
                "elapsed_ms": elapsed_ms,
                "evidence": evidence_text
            })
            
            print(f"  -> 成功: {model_output.get('support_status')}, Page: {page}")
            time.sleep(1)
            
        except Exception as e:
            # 存单次失败 JSON（符合“失败分母必须保留”的要求）
            error_result = {
                "request_id": request_id,
                "task_id": task_id,
                "mode": mode,
                "status": "error",
                "error_message": str(e),
                "elapsed_ms": int((time.time() - start_time) * 1000)
            }
            with open(f'runs_adv/{task_id}_{mode}_ERROR_{request_id[:8]}.json', 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)
            print(f"  -> 失败: {e}")

# 保存 CSV
with open('results_adv.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["task_id", "mode", "status", "page", "locator", "elapsed_ms", "evidence"])
    writer.writeheader()
    writer.writerows(csv_rows)

print("\n全部跑完！结果已保存到 runs_adv/ 和 results_adv.csv")