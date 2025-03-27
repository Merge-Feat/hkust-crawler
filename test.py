from crawler import normalize_url, is_valid_url

# ANSI 색상 코드
GREEN = "\033[92m"
RESET = "\033[0m"

# URL 정규화 테스트
def test_normalize_url():
    print("\n" + "-" * 30)
    print("🔍 Running test: normalize_url")
    print("-" * 30)

    test_cases = [
        ("https://hkust.edu.hk/lifehkust#living-on-campus", "https://hkust.edu.hk/lifehkust"),
        ("https://hkust.edu.hk/lifehkust", "https://hkust.edu.hk/lifehkust"),
        ("https://hkust.edu.hk/lifehkust/", "https://hkust.edu.hk/lifehkust"),
    ]

    for url, expected in test_cases:
        result = normalize_url(url)
        print(f"\n🌐 Input: {url}")
        print(f"✅ Expected: {expected}")
        print(f"🟢 Got: {result}")
        assert result == expected, f"❌ Test failed for input: {url}"
    
    print(f"{GREEN}🎉 All normalize_url tests passed!{RESET}")



# URL 필터링 테스트
def test_is_valid_url():
    print("\n" + "-" * 30)
    print("🔍 Running test: is_valid_url")
    print("-" * 30)

    valid_domains = ["hkust.edu.hk", "ust.hk"]
    exclude_strings = ["mailto:", "GZ", "zh-hans", "zh-hant"]
    useful_extensions = [
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", "jpg", "jpeg",
        "png", ".gif", ".xls", ".xlsx", ".csv", ".json", ".xml"
    ]
    
    test_cases = [
        ("https://hkust.edu.hk/lifehkust#living-on-campus", valid_domains, exclude_strings, True),
        ("https://ust.hk/lifehkust", valid_domains, exclude_strings, True),
        ("https://ust.hk/lifehkust/", valid_domains, exclude_strings, True),
        ("https://ust.hk/lifehkust/file.png", valid_domains, exclude_strings, False),
        ("https://ust.hk/lifehkust/temp.pdf", valid_domains, exclude_strings, False),
        ("mailto: hkust.edu.hk", valid_domains, exclude_strings, False),
        ("https://hkust.edu.hk/GZ", valid_domains, exclude_strings, False),
        ("https://hkust.edu.hk/zh-hans", valid_domains, exclude_strings, False),
        ("https://hkust.edu.hk/zh-hant", valid_domains, exclude_strings, False),
        ("http://schina.hkust.edu.hk/zh-hant/activities/lectures/history-and-anthropology-lecture-series", valid_domains, exclude_strings, False),
    ]
    
    for url, valid_domains, exclude_strings, expected in test_cases:
        result = is_valid_url(url, valid_domains, exclude_strings)
        print(f"\n🌐 Input: {url}")
        print(f"✅ Expected: {expected}")
        print(f"🟢 Got: {result}")
        assert result == expected, f"❌ Test failed for input: {url}"
        
    print(f"{GREEN}🎉 All is_valid_url tests passed!{RESET}")


def run_tests():
    test_normalize_url()
    test_is_valid_url()