import json
import os
from collections import Counter
from urllib.parse import urlparse

# 입력 파일 경로
input_file = "./raw_output/visited.json"

# 출력 디렉토리 및 파일 경로 설정
output_dir = "./processed_output"  # 저장할 디렉토리
output_file = os.path.join(output_dir, "sorted_domains.json")

# 디렉토리 없으면 생성
os.makedirs(output_dir, exist_ok=True)

def get_sorted_domains(urls):
    domain_count = Counter(urlparse(url).hostname for url in urls if urlparse(url).hostname)
    sorted_domains = sorted(domain_count.items(), key=lambda x: x[1], reverse=True)
    
    return [domain for domain, _ in sorted_domains]

# JSON 파일 로드
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 도메인 정렬 수행
sorted_domains = get_sorted_domains(data)

# 정렬된 도메인 출력
print(sorted_domains)

# 결과를 JSON 파일로 저장
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(sorted_domains, f, ensure_ascii=False, indent=4)

print(f"Sorted domains saved to: {output_file}")
