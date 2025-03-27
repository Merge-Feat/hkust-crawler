import os
import shutil
import hashlib

OUTPUT_DIR = "extract_target"
EXTRACT_DIR = "extracted"

def find_duplicate_files(directory):
    """
    주어진 디렉토리에서 중복된 파일을 찾아 반환합니다.

    Args:
        directory (str): 파일을 검색할 디렉토리 경로

    Returns:
        dict: 중복된 파일 그룹을 값으로 갖는 딕셔너리 (키는 파일 크기)
    """

    file_sizes = {}
    duplicates = {}

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_size = os.path.getsize(filepath)

            if file_size in file_sizes:
                file_sizes[file_size].append(filepath)
            else:
                file_sizes[file_size] = [filepath]

    for size, paths in file_sizes.items():
        if len(paths) > 1:
            hashes = {}
            for path in paths:
                file_hash = calculate_file_hash(path)
                if file_hash in hashes:
                    if size not in duplicates:
                        duplicates[size] = []
                    duplicates[size].append(path)
                else:
                    hashes[file_hash] = path

    return duplicates

def calculate_file_hash(filepath, hash_algorithm="sha256", buffer_size=65536):
    """
    주어진 파일의 해시 값을 계산합니다.

    Args:
        filepath (str): 파일 경로
        hash_algorithm (str): 사용할 해시 알고리즘 (기본값: "sha256")
        buffer_size (int): 파일을 읽을 버퍼 크기 (기본값: 65536)

    Returns:
        str: 파일의 해시 값
    """

    hash_obj = hashlib.new(hash_algorithm)
    with open(filepath, "rb") as f:
        while chunk := f.read(buffer_size):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def extract_md_files():
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    
    for root, _, files in os.walk(OUTPUT_DIR):
        for file in files:
            if file.endswith(".html"):
                src_path = os.path.join(root, file)
                parent_dir = os.path.basename(root)
                new_file_name = f"{parent_dir}-{file}"
                dest_path = os.path.join(EXTRACT_DIR, new_file_name)
                shutil.copy2(src_path, dest_path)
                print(f"Copied: {src_path} -> {dest_path}")
    
    duplicate_groups = find_duplicate_files(EXTRACT_DIR)
    
    if duplicate_groups:
        print(f"{EXTRACT_DIR} 디렉토리에서 중복된 파일 그룹:")
        for size, files in duplicate_groups.items():
            print(f"  파일 크기: {size} 바이트")
            for file in files:
                print(f"    - {file}")
        
        user_input = input("중복된 파일을 삭제하시겠습니까? (y/n): ")
        if user_input.lower() == 'y':
            for size, files in duplicate_groups.items():
                # 중복된 파일 그룹에서 첫 번째 파일을 제외하고 삭제
                for file_to_delete in files[1:]:
                    try:
                        os.remove(file_to_delete)
                        print(f"삭제됨: {file_to_delete}")
                    except OSError as e:
                        print(f"삭제 실패: {file_to_delete} - {e}")
            print("중복된 파일이 모두 삭제되었습니다.")
        else:
            print("중복된 파일 삭제를 취소했습니다.")
    else:
        print(f"{EXTRACT_DIR} 디렉토리에서 중복된 파일이 없습니다.")

extract_md_files()