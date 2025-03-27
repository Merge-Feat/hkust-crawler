import asyncio
import sys
import os
import json
import logging
from datetime import datetime
from urllib.parse import urlparse, urlunparse, urljoin
import tiktoken  # 토큰 계산을 위한 라이브러리
from bs4 import BeautifulSoup

from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from openai import AzureOpenAI

import test

# OpenAI API 키 설정
# openai.api_key = 'YOUR_OPENAI_API_KEY'

# 도메인 및 제외할 문자열 설정
# valid_domains = ["hkust.edu.hk", "ust.hk"]
SHRL_DOMAIN = ["shrl-admission.ust.hk", "shrl-jockeyclubhall.ust.hk", "shrl-ughall1.ust.hk", "shrl-ughall7.ust.hk", "shrl-ughall8.ust.hk", "shrl.hkust.edu.hk", "shrl.ust.hk"]
UROP_DOMAIN = ["urop.hkust.edu.hk"]
SFAO_DOMAIN = ["sfao.hkust.edu.hk"]
CAMPUS_SERVICES_DOMAIN = ["cso.hkust.edu.hk"]
valid_domains = SHRL_DOMAIN
# exclude_strings = ["mailto:", "GZ", "zh-hans", "zh-hant", "pathadvisor", "events", "news", "sponsor", "faculty", "lbdiscover", "roombook", "repository", "digitalimages", "publication", "photo-gallery", "exchange/outbound-exchange/exchange-choices/", "zh-hk", "hall_of_fame_profile", "souvenir", "zh-cn", "zh-CN", "people", "ourgraduates"]
exclude_strings = []
# 추후에 학습할 확장자 리스트
useful_extensions = [
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", "jpg", "jpeg",
    "png", ".gif", ".xls", ".xlsx", ".csv", ".json", ".xml", "zip"
]

# external links 저장용 딕셔너리
graph = {}
# visited는 파일로부터 로드하거나 새로 생성 (중복 방문 방지)
visited = set()
useful_urls = set()

# output 디렉토리 설정
OUTPUT_DIR = "raw_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# log 디렉토리 설정
LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "raw_p_crawler{}.log".format(datetime.now().strftime("%Y%m%d-%H%M%S")))),
        logging.StreamHandler()
    ]
)

client = AzureOpenAI(
    api_key="d98a813b821d4b2a9743129a8ce774c7",
    api_version="2024-10-21",
    azure_endpoint="https://hkust.azure-api.net"
)

SYSTEM_PROMPT_HTML = '''
Please adhere to the following guidelines:

1. Accurately translate the original content.
Identify and remove all non-essential UI elements from the following Markdown document. Keep only the main content while excluding:  
- Navigation menus (e.g., "MORE ABOUT HKUST", "Menu", repeated link lists)  
- Headers and footers (e.g., "Sitemap", "Privacy", copyright notices)  
- Social media links and icons  
- Logos and redundant images  
- Cookie consent messages  

Return only the cleaned content relevant for RAG processing.  
'''

# 토큰 계산을 위한 인코더 초기화
encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 및 GPT-3.5용 인코더

def count_tokens(text: str) -> int:
    """텍스트의 토큰 수를 계산합니다."""
    return len(encoding.encode(text))

def remove_markdown_links_with_text(text: str) -> str:
    """마크다운 문서에서 링크와 텍스트를 제거합니다."""
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith("[") and not line.startswith("("):
            new_lines.append(line)
    return "\n".join(new_lines)

def clean_markdown(text: str, system_prompt: str = SYSTEM_PROMPT_HTML) -> str:
    if not text:
        return ""
    
    prompt = f"{system_prompt}\n\n## Input:\n{text}\n\n## Output:"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=16000,
        )
        
        content = response.choices[0].message.content
        if "```markdown" in content:
            temp = content.split("```markdown")[1]
            if "```" in temp:
                return temp.split("```")[0]
        return content
    except Exception as e:
        print(f"API 오류 발생: {str(e)}")
        return ""

# URL 필터링 함수
def is_valid_url(url, valid_domains, exclude_strings):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # 크롤링할 확장자 확인
    if any(path.endswith(ext) for ext in useful_extensions):
        # 크롤링할 확장자에 해당하는 URL은 따로 저장
        useful_urls.add(url)
        return False  # 크롤링은 하지 않지만 저장만 합니다.
    
    # 제외할 문자열 확인
    for ex_str in exclude_strings:
        if ex_str in url:
            return False

    # 도메인 확인 
    if any(domain.endswith(vd) for vd in valid_domains):
        return True

    return False

# 방문한 사이트 로드 함수
def load_visited():
    visited_path = os.path.join(OUTPUT_DIR, "visited.json")
    if os.path.exists(visited_path):
        with open(visited_path, "r", encoding="utf-8") as f:
            return set(json.load(f))  # 리스트를 집합(set)으로 변환
    return set()

# 방문한 사이트 저장 함수
def save_visited():
    logging.info(f"Saving visited: {len(visited)} entries")
    visited_path = os.path.join(OUTPUT_DIR, "visited.json")
    with open(visited_path, "w", encoding="utf-8") as f:
        json.dump(list(visited), f, indent=4, ensure_ascii=False)
        
# queue 저장 함수 (목록으로 변환하여 저장)
def save_queue(queue_list):
    queue_path = os.path.join(OUTPUT_DIR, "queue.json")
    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump(queue_list, f, indent=4, ensure_ascii=False)

# 크롤링할 URL을 queue.json에 저장하는 함수
def save_useful_urls():
    useful_urls_path = os.path.join(OUTPUT_DIR, "files.json")
    with open(useful_urls_path, "w", encoding="utf-8") as f:
        json.dump(list(useful_urls), f, indent=4, ensure_ascii=False)

# queue 로드 함수
def load_queue():
    queue_path = os.path.join(OUTPUT_DIR, "queue.json")
    if os.path.exists(queue_path):
        with open(queue_path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# 파일 저장 경로 생성 함수
def create_file_path(url, extension):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path_parts = parsed_url.path.strip('/').split('/')
    
    if not path_parts[-1]:
        path_parts[-1] = 'index'
    
    file_name = f"{path_parts[-1]}.{extension}"
    dir_path = os.path.join(OUTPUT_DIR, domain, *path_parts[:-1])  # 도메인을 유지한 채 경로 생성
    
    os.makedirs(dir_path, exist_ok=True)
    
    return os.path.join(dir_path, file_name)

def normalize_url(url):
    parsed_url = urlparse(url)
    # fragment 제거 (예: #main-content)
    normalized_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", parsed_url.query, ""))
    # url 마지막에 /가 있으면 제거
    if normalized_url.endswith('/'):
        normalized_url = normalized_url[:-1]
    return normalized_url

# 병렬(BFS) 크롤링 함수 (중복 크롤링 방지를 위해 URL enqueue 시점에 visited에 추가)
async def bfs_crawl(start_url, valid_domains, exclude_strings):
    browser_config = BrowserConfig()
    run_config = CrawlerRunConfig(
        # raw html을 캐싱하기 위해 설정
        # excluded_tags=["nav", "footer", "header", "script", "style", "form", "input", "button", "iframe", "chat-widget"],
        # excluded_selector=".cookieinfo, .view-news-sidebar, .slick-arrow, .slide-popup__caption, #calendar, .view-hkust-social-media-fb-ig, #fontTestBed, #fontInstalledTest, .eu-cookie-compliance-banner, .visually-hidden, .category__text, .banner"
    )
    
    # 기존 상태 로드
    global visited  # 모듈 전역의 visited 업데이트
    visited = load_visited()
    loaded_queue = load_queue()
    
    # 비동기 큐와 락 생성
    queue = asyncio.Queue()
    visited_lock = asyncio.Lock()
    token_lock = asyncio.Lock()
    total_tokens = 0
    
    # 초기 큐 등록 (중복 방지를 위해 visited에 추가)
    async with visited_lock:
        if loaded_queue:
            for url in loaded_queue:
                if url not in visited:
                    visited.add(url)
                    await queue.put(url)
        else:
            visited.add(start_url)
            await queue.put(start_url)
    
    start_time = datetime.now()
    logging.info(f"Crawling started at: {start_time}")
    
    async def worker():
        nonlocal total_tokens
        # 각 워커는 독립적인 crawler 인스턴스를 사용
        async with AsyncWebCrawler(config=browser_config) as crawler:
            while True:
                try:
                    url = await asyncio.wait_for(queue.get(), timeout=5)
                except asyncio.TimeoutError:
                    break  # 일정 시간동안 새 URL이 없으면 종료
                
                result = await crawler.arun(url=url, config=run_config)
                if result.error_message:
                    logging.error(f"Error crawling {url}: {result.error_message}")
                    queue.task_done()
                    continue
                
                file_path = create_file_path(url, "html")
                tokens = count_tokens(result.cleaned_html)
                if tokens < 100:
                    logging.info(f"Skipping: {url} | Tokens: {tokens}")
                    queue.task_done()
                    continue
                async with token_lock:
                    total_tokens += tokens
                logging.info(f"Crawled: {url} | Tokens: {tokens}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result.cleaned_html)
                
                # 추출한 링크 처리: enqueue 전에 visited에 추가하여 중복 방지
                for link_type in ['internal', 'external']:
                    for link in result.links[link_type]:
                        new_url = normalize_url(link["href"])
                        async with visited_lock:
                            if new_url not in visited:
                                if is_valid_url(new_url, valid_domains, exclude_strings):
                                    visited.add(new_url)
                                    await queue.put(new_url)
                                else:
                                    base_domain = link["base_domain"]
                                    if base_domain not in graph:
                                        graph[base_domain] = []
                                    graph[base_domain].append(new_url)
                
                save_visited()
                save_useful_urls()
                queue.task_done()
    
    # 다수의 워커 태스크 생성 (예: 5개)
    workers = [asyncio.create_task(worker()) for _ in range(5)]
    await queue.join()  # 큐가 완전히 소진될 때까지 대기
    for w in workers:
        w.cancel()
    
    end_time = datetime.now()
    logging.info(f"Crawling ended at: {end_time}")
    logging.info(f"Total pages crawled: {len(visited)}")
    logging.info(f"Total tokens crawled: {total_tokens}")
    logging.info(f"Visited pages: {visited}")
    
    # 남은 큐 상태 저장 (목록으로 변환)
    remaining_urls = []
    while not queue.empty():
        remaining_urls.append(queue.get_nowait())
    
    save_visited()
    save_queue(remaining_urls)
    save_useful_urls()
    
    GRAPH_PATH = os.path.join(OUTPUT_DIR, "graph.json")
    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4, ensure_ascii=False)

async def remove_a_and_li_with_content(url):
    # 크롤러 설정
    crawler_config = CrawlerRunConfig(
        excluded_tags=["a", "li"],  # <a>와 <li> 태그와 내용 제외
        cache_mode="BYPASS"
    )

    async with AsyncWebCrawler(verbose=True) as crawler:
        # HTML 직접 제공하여 크롤링
        result = await crawler.arun(
            url='file://' + url,
            config=crawler_config
        )
        
        # Markdown 결과 후처리
        markdown_lines = result.markdown.splitlines()
        cleaned_lines = []
        i = 0
        
        while i < len(markdown_lines):
            line = markdown_lines[i].strip()
            
            # 제목 태그인지 확인 (#로 시작)
            if line.startswith('#'):
                # 제목 태그와 그 아래 유효한 줄을 수집
                title = line
                content_lines = []
                i += 1
                
                # 제목 아래 줄들을 확인
                while i < len(markdown_lines) and not markdown_lines[i].strip().startswith('#'):
                    content_line = markdown_lines[i].strip()
                    if content_line:  # 빈 줄 제외
                        word_count = len(content_line.split())
                        # 10단어 이상인 줄만 추가 & copy right 제외
                        if word_count >= 10 and "Copyright" not in content_line:
                            content_lines.append(content_line)
                    i += 1
                
                # 유효한 내용이 있으면 제목과 함께 추가
                if content_lines:
                    cleaned_lines.append(title)
                    cleaned_lines.extend(content_lines)
            else:
                # 제목이 아닌 줄은 10단어 이상일 때만 추가
                if line:
                    word_count = len(line.split())
                    if word_count >= 10:
                        cleaned_lines.append(line)
                i += 1
        
        # 최종 Markdown 문자열로 결합
        cleaned_markdown = '\n'.join(cleaned_lines)
        return cleaned_markdown

# 실행 부분
if __name__ == "__main__":
    try:
        test.run_tests()  # 테스트 실행
    except AssertionError as e:
        sys.exit(1)  # 실패하면 프로그램 종료
    
    start_url = "https://shrl.hkust.edu.hk/"
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # --reset 옵션이 있으면 queue.json 및 visited.json 삭제 후 시작
        queue_path = os.path.join(OUTPUT_DIR, "queue.json")
        visited_path = os.path.join(OUTPUT_DIR, "visited.json")
        if os.path.exists(queue_path):
            os.remove(queue_path)
        if os.path.exists(visited_path):
            os.remove(visited_path)
        print("크롤링 상태 초기화 (queue.json, visited.json 삭제됨)")
    
    asyncio.run(bfs_crawl(start_url, valid_domains, exclude_strings))
