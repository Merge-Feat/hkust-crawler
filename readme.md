## check_duplicate_url_from_json

## 개요
이 스크립트는 JSON 파일에서 중복된 요소를 검사하는 Python 프로그램입니다.

## 사용법
1. 확인하려는 JSON 파일을 준비합니다. (예: `visited.json`)
2. `check_duplicates_in_json(file_path)` 함수를 실행합니다.
3. 중복된 요소가 있는 경우 개수와 목록을 출력합니다.

## 실행 방법
```sh
python check_duplicate_url_from_json.py
```

## 오류 처리
- 파일이 존재하지 않을 경우 오류 메시지를 출력합니다.
- JSON 형식이 올바르지 않으면 오류 메시지를 출력합니다.

## 파일 경로 변경
기본 경로는 `./raw_output/visited.json`입니다. 필요에 따라 수정하세요.

---

## download_files_from_json

## 개요
이 스크립트는 JSON 파일에서 URL 목록을 읽어 해당 파일들을 다운로드합니다.

## 사용법
1. 다운로드할 파일 URL 목록이 담긴 JSON 파일을 준비합니다. (예: `files.json`)
2. `download_files_from_json(json_file_path)` 함수를 실행합니다.
3. 다운로드된 파일은 `downloaded_files` 폴더에 저장됩니다.

## 실행 방법
```sh
python download_files_from_json.py
```

## 주의 사항
- `cookies` 값이 필요할 수 있습니다. (해당 웹사이트의 인증이 필요한 경우)
- `requests` 라이브러리가 필요합니다. 없을 경우 `pip install requests`로 설치하세요.

## 오류 처리
- 파일이 존재하지 않을 경우 오류 메시지를 출력합니다.
- JSON 형식이 올바르지 않으면 오류 메시지를 출력합니다.
- 다운로드 중 오류가 발생하면 해당 URL을 출력합니다.

---

## extract_specific_files

## 개요
이 스크립트는 `ustspace_output` 디렉토리에서 사용되지 않은 JSON 파일을 `extracted_files` 디렉토리로 이동합니다.

## 사용법
1. `ustspace_output` 폴더에 JSON 파일과 `AA_used.json` 파일을 준비합니다.
2. `AA_used.json` 파일에는 사용된 파일 목록(JSON 리스트)이 포함되어야 합니다.
3. 스크립트를 실행하면 사용되지 않은 JSON 파일이 `extracted_files` 폴더로 이동됩니다.

## 실행 방법
```sh
python extract_specific_files.py
```

## 주의 사항
- `AA_used.json` 파일이 존재해야 합니다.
- `extracted_files` 폴더가 없으면 자동 생성됩니다.
- 사용된 파일 목록에 없는 JSON 파일만 이동됩니다.

## 오류 처리
- `AA_used.json` 파일이 없거나 형식이 잘못된 경우 오류가 발생할 수 있습니다.

-----

## extract.py

## 개요
이 스크립트는 `extract_target` 디렉토리에서 `.html` 파일을 추출하여 `extracted` 디렉토리에 저장하고, 중복된 파일을 찾아 삭제 여부를 선택할 수 있도록 합니다.

## 사용법
1. `extract_target` 폴더에 `.html` 파일이 포함된 디렉토리를 준비합니다.
2. 스크립트를 실행하면 `.html` 파일이 `extracted` 폴더로 복사됩니다.
3. 중복된 파일이 감지되면 삭제 여부를 선택할 수 있습니다.

## 실행 방법
```sh
python extract.py
```

## 기능
- `.html` 파일을 특정 폴더에서 추출
- 중복된 파일 탐색 (파일 크기 및 해시 기반)
- 중복된 파일 삭제 여부 선택

## 주의 사항
- `extracted` 폴더가 자동 생성됩니다.
- 삭제를 선택한 경우 중복 파일이 제거됩니다.

## 오류 처리
- 파일이 없거나 접근할 수 없을 경우 오류 메시지를 출력합니다.

------

## general_crawler
## parallel_crawler(병렬)
## parallel_crawler_raw_html (병렬, raw_html)

## 개요
이 프로젝트는 HKUST 웹사이트를 크롤링하여 유용한 정보를 수집하고 정제하는 웹 크롤러입니다. 
크롤링한 데이터는 HTML 및 Markdown 형식으로 저장되며, 필요 없는 UI 요소를 제거하여 RAG 학습에 적합한 데이터로 가공됩니다.

## 주요 기능
- 지정된 도메인의 웹페이지 크롤링
- 불필요한 UI 요소(네비게이션, 푸터 등) 제거
- 텍스트 기반 토큰 수 계산
- 크롤링된 데이터 저장 및 관리
- 유용한 파일(URL) 목록 저장
- 외부 링크 그래프 저장

## 환경 설정
### 1. 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
Azure OpenAI API 키 및 엔드포인트를 설정해야 합니다.
```python
client = AzureOpenAI(
    api_key="YOUR_AZURE_OPENAI_API_KEY",
    api_version="2024-10-21",
    azure_endpoint="https://YOUR_AZURE_ENDPOINT"
)
```

## 실행 방법
기본 크롤링 실행:
```bash
python crawler.py
```

이전 크롤링 기록을 초기화하고 실행:
```bash
python crawler.py --reset
```

## 데이터 저장
- 크롤링된 HTML: `output/{도메인}/.../*.html`
- 방문한 URL 목록: `output/visited.json`
- 크롤링 대기 목록: `output/queue.json`
- 유용한 파일 목록: `output/files.json`
- 외부 링크 그래프: `output/graph.json`

## 로그 저장
크롤링 로그는 `log/crawlerYYYYMMDD-HHMMSS.log` 파일로 저장됩니다.

## 테스트 실행
코드를 실행하기 전, 테스트를 실행하여 정상 동작을 확인할 수 있습니다.
```bash
python -m test
```

## 주의 사항
- 크롤링 대상 사이트의 `robots.txt` 정책을 준수해야 합니다.
- 너무 많은 요청을 보내지 않도록 주의하세요.

-----

# sort_url_by_frequency

이 스크립트는 `visited.json` 파일에서 특정 단어(`zh-cn`)가 포함된 항목을 제거하는 Python 스크립트입니다.

## 사용 방법
1. `visited.json` 파일을 `raw_output/` 폴더에 준비합니다.
2. 스크립트를 실행하면 `zh-cn`이 포함된 항목이 제거됩니다.
3. 수정된 데이터는 다시 `visited.json` 파일로 저장됩니다.

## 필터링 방식
- JSON 데이터가 리스트일 경우: 특정 단어가 포함된 항목 제거
- JSON 데이터가 객체일 경우: 현재는 처리하지 않음 (코드 수정 필요)

## 실행 방법
```sh
python sort_url_by_frequency.py
```

## 주의사항
- 원본 데이터가 변경되므로 실행 전에 백업을 권장합니다.

-----

## ust_space_crawler

## 개요
이 스크립트는 UST Space 웹사이트에서 강의 리뷰 데이터를 수집하여 JSON 파일로 저장하는 프로그램입니다.

## 기능
- 주어진 강의 코드 리스트를 기반으로 강의 정보를 조회
- 각 강의의 리뷰 데이터를 수집하여 개별 JSON 파일로 저장
- 멀티스레딩을 활용한 빠른 데이터 수집

## 사용 방법
1. `requests`, `os`, `time`, `json`, `concurrent.futures` 패키지가 필요합니다.
2. `python`을 사용하여 스크립트를 실행합니다:
   ```sh
   python ust_space_crawler.py
   ```
3. 수집된 데이터는 `./ustspace_output` 디렉토리에 JSON 파일로 저장됩니다.

## 주의 사항
- 웹사이트의 정책을 준수하며 과도한 요청을 피하세요.
- 쿠키 값이 만료될 경우 업데이트해야 합니다.
- 실행 환경에 따라 최대 스레드 수(`max_workers`)를 조정할 수 있습니다.

## 라이선스
이 프로젝트는 자유롭게 수정 및 배포할 수 있습니다.


