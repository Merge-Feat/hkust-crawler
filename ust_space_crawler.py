import requests
import os
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# 코드 리스트
code_list = [
    "BIEN", "BMED", "CENG", "CIVL", "COMP", "CPEG", "ELEC", "ENGG", "IEDA", "IELM",
    "ISDN", "MECH", "SUST", "BIBU", "BIPH", "CHEM", "DASC", "ENVS", "LIFS", "MATH",
    "OCES", "PHYS", "SCED", "SCIE", "ACCT", "ECON", "FINA", "GBUS", "ISOM", "MARK",
    "MGMT", "SBMT", "HART", "HUMA", "PPOL", "SHSS", "SOSC", "EMIA", "ENVR", "LAGR",
    "RMBI", "CORE", "ENTR", "GNED", "HLTH", "LABU", "LANG", "TEMG", "UROP"
]

# 출력 디렉토리 설정
output_dir = "./ustspace_output"
os.makedirs(output_dir, exist_ok=True)

# 쿠키 및 헤더 설정
cookies = {
    "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d": "eyJpdiI6IjR3bXd3bjRXaXRGWFBOODRlaGVWc2c9PSIsInZhbHVlIjoiQzJxOUxnUVdnZi9FSTVBZ0c1RUhhUHdBcVdrZFpDOHEvK0hJUWpFK3VHTkxGdXlUdlhSa0YzMVJuNGdGSzRqYUV4QXJaY1g4ZGZraFFOUHpNRjM4QU0xK2t0b0tFQWF1bVhlVzBkTHhyK2h2WEYwbjNpOUd4MWNZZEcrdnhFNGZOWjVYNFpLQkNLcUxDSlBhZUN3ckN3R01ZbUx5ZlR1VndXK3A3eDEvMXU4c2t5SnFnUmxxaC9JeXpuMTV4REVCZzg5dzlFWnlTRUliSEd0TmxKVzU2UDRlVCt3cXd1TkxXRk9TdTJRaXhVRT0iLCJtYWMiOiI0ZDQxNzRjMjFiNGNmZjczYWI5YWUzYmNhMDk5ZjNlNzA4YTYxZWJkNzczNDY5OWVhODM2MGQxNGM1NmVhNzhiIiwidGFnIjoiIn0%3D",
    "ustspace_session": "eyJpdiI6IncrSk9MdFNOdnZ3OFU3WU1zMDFaMmc9PSIsInZhbHVlIjoibEFRZk1ORXRHTTVPVzVYZFZmOUJtRndUTnBHS3R4WUJJU1YzaTByR3NTMlpqSXRudzY3N09oNFM5MkJTdWpZVmM5U01WYnFPUGEzZkdDTm01OURZUkxVTEtjamVIRW90a0ZKbUpBRzZULzl0VUFVSUx4ckVxcHVvWWhER2labEIiLCJtYWMiOiI5YWUxYjNiNjA4Y2FhZjI1NTU4MDU0MmQ4Y2U2YWE4NWVhMmM3ODQ5NzRlYzQwOTZhMzYyMWFhZTRhNmJlNTBhIiwidGFnIjoiIn0%3D"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# 데이터 가져오기 함수
def fetch_data(url):
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# 강의 리뷰 데이터 저장 함수
def save_review_data(course_value, review_data):
    file_path = os.path.join(output_dir, f"{course_value}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(review_data, f, ensure_ascii=False)
        print(f"Saved: {course_value}")
    except Exception as e:
        print(f"File save failed for {course_value}: {e}")

# 강의 리뷰 데이터 가져오기 함수
def fetch_reviews(course_value):
    review_url = f"https://ust.space/review/{course_value}/get?single=false&composer=false&preferences%5Bsort%5D=0&preferences%5BfilterInstructor%5D=0&preferences%5BfilterSemester%5D=0&preferences%5BfilterRating%5D=0"
    review_data = fetch_data(review_url)
    if review_data:
        save_review_data(course_value, review_data)

# 병렬 처리 함수
def process_subject(code):
    subject_url = f"https://ust.space/selector/query?page=review&type=subject&value={code}"
    subject_data = fetch_data(subject_url)
    
    if not subject_data or subject_data.get("error", True):
        print(f"Skipping {code} due to error")
        return []
    
    course_list = subject_data.get("list", [])
    return [course.get("value") for course in course_list if course.get("value")]

# 메인 함수
def main():
    with ThreadPoolExecutor(max_workers=10) as executor:  # 동시에 처리할 최대 스레드 수
        # 각 과목 코드에 대해 병렬로 처리
        future_to_code = {executor.submit(process_subject, code): code for code in code_list}
        
        for future in as_completed(future_to_code):
            code = future_to_code[future]
            try:
                course_values = future.result()
                if course_values:
                    # 각 강의 리뷰 데이터를 병렬로 가져오기
                    review_futures = [executor.submit(fetch_reviews, course_value) for course_value in course_values]
                    for review_future in as_completed(review_futures):
                        review_future.result()  # 결과 대기 (에러 처리 포함)
            except Exception as e:
                print(f"Error processing {code}: {e}")

if __name__ == "__main__":
    main()