import json, glob
from collections import Counter

def first_key(d, keys):
    for k in keys:
        if k in d:
            return d[k]
    return None

stats = Counter()
for f in glob.glob('runs/*.json'):
    d = json.load(open(f, encoding='utf-8'))
    case = first_key(d, ['case', 'case_id', 'task_id', 'question_id', 'id', 'case_name'])
    cond = first_key(d, ['condition', 'cond'])
    variant = first_key(d, ['variant', 'method', 'mode'])
    status = first_key(d, ['status', 'state'])
    has_resp = ('response' in d) or ('raw_response' in d) or ('answer' in d)
    stats[(case, cond, variant, status, has_resp)] += 1

for k, v in sorted(stats.items(), key=lambda x: str(x[0])):
    print(k, v)