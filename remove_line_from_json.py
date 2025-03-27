import json

target_file = "raw_output/visited.json"

# JSON 파일 읽기
with open(target_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 삭제할 단어
target_word = "zh-cn"

# 배열에서 특정 단어 포함 항목 삭제
if isinstance(data, list):
    data = [item for item in data if target_word not in str(item)]
# 객체에서 특정 단어 포함 키-값 쌍 삭제
# elif isinstance(data, dict):
#     data = {k: v for k, v in data.items() if target_word not in str(k) and target_word not in str(v)}

# 수정된 JSON 파일 저장
with open(target_file, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print("DONE")