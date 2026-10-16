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
    """返回重新组织/选择的原段落列表，不能修改id/source/text或使用答案标签。
    默认恒等映射仅用于联通，不算已完成改进。可自行扩展结构/调用，须披露与记录。"""
    return passages
