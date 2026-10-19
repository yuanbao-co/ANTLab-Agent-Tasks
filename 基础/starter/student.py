import json
def prepare_messages(question, passages):
    passage_blocks = []
    for p in passages:
        passage_blocks.append(f"[{p['id']}] {p['text']}")
    joined = "\n\n".join(passage_blocks)

    system = (
        "你是一个文档核验助手。只根据下面提供的段落回答问题。"
        "如果段落不足以回答问题，回答“证据不足”。"
        "必须只返回一个 JSON 对象，格式为："
        '{"answer": "简短答案", "citations": ["段落ID"]}。'
        "citations 中只放你实际用到的段落 ID。不要输出 JSON 以外的任何内容。"
    )
    user = f"问题：{question}\n\n可用段落：\n{joined}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

def improve(question, passages):
    # 改进：把段落倒序，测试模型抗位置干扰能力
    return list(reversed(passages))