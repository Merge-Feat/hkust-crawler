import json

def check_duplicates_in_json(file_path):
    try:
        # JSON 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 데이터가 리스트인지 확인
        if not isinstance(data, list):
            print("Error: JSON 데이터가 리스트 형식이 아닙니다.")
            return False

        # 중복 확인 (set과 원래 리스트 길이 비교)
        original_length = len(data)
        unique_length = len(set(data))

        if original_length > unique_length:
            print(f"중복 요소가 존재합니다. 총 {original_length - unique_length}개의 중복 발견.")
            # 중복 요소 찾기
            seen = set()
            duplicates = set()
            for item in data:
                if item in seen:
                    duplicates.add(item)
                else:
                    seen.add(item)
            print(f"중복된 요소: {duplicates}")
            return True
        else:
            print("중복 요소가 없습니다.")
            return False

    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return False
    except json.JSONDecodeError:
        print(f"JSON 파싱 오류: {file_path}")
        return False
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

# 사용 예시
if __name__ == "__main__":
    json_file = "./raw_output/visited.json"  # 확인하려는 JSON 파일 경로
    has_duplicates = check_duplicates_in_json(json_file)