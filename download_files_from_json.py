import requests
import os
import json

cookies={
    "SSESSfe30da18b42a62535d0d4114fca3282b": "ilXds911ORxHtrkeFUutObivZO7DiqlJA3S4a4Bh6H9%2CiCnv"
}

def download_files_from_json(json_file_path, download_folder="downloaded_files"):
    """JSON 파일에서 URL 목록을 읽어 파일을 다운로드합니다."""

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    try:
        with open(json_file_path, 'r') as f:
            urls = json.load(f)

            for url in urls:
                try:
                    response = requests.get(url, cookies=cookies, stream=True)
                    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

                    filename = os.path.join(download_folder, url.split("/")[-1])
                    with open(filename, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                    print(f"Downloaded: {filename}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {url}: {e}")

    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")

# JSON 파일 경로
json_file_path = "raw_output/files.json"

# 파일 다운로드 실행
download_files_from_json(json_file_path)