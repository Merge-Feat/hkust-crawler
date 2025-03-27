import os
import shutil
import json

# 디렉토리 경로 설정
output_dir = './ustspace_output'
used_file_path = os.path.join(output_dir, 'AA_used.json')
extracted_dir = './extracted_files'

# extracted_files 디렉토리가 없으면 생성
if not os.path.exists(extracted_dir):
    os.makedirs(extracted_dir)

# used.json 파일 읽기
with open(used_file_path, 'r', encoding='utf-8') as f:
    used_files = json.load(f)  # used.json은 JSON 리스트 형태여야 합니다.

# ustspace_output 디렉토리 내의 모든 파일 확인
for filename in os.listdir(output_dir):
    file_path = os.path.join(output_dir, filename)

    # 파일인지 확인하고, used.json에 없는 파일인지 확인
    if os.path.isfile(file_path) and filename.endswith('.json') and filename not in used_files:
        # extracted_files 디렉토리로 파일 이동
        shutil.move(file_path, os.path.join(extracted_dir, filename))
        print(f'Moved: {filename}')

print("File extraction completed.")