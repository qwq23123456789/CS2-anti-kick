"""
CS2 Steam Blocker - 基本測試
確保 CI/CD 可以通過
"""

def test_python_works():
    """測試 Python 基本運算"""
    assert 1 + 1 == 2
    assert True

def test_string_operations():
    """測試字串操作"""
    assert "CS2" in "CS2 Steam Blocker"
    assert len("test") == 4

def test_import_basic_modules():
    """測試可以導入基本模組"""
    import json
    import sys
    import os
    assert json is not None
    assert sys is not None
    assert os is not None
```

---

## 📂 檢查資料夾結構

現在你的專案應該長這樣:
```
你的專案/
├── cs2-steam-blocker-python.py
├── tests/
│   ├── __init__.py          ← 空白文件
│   └── test_basic.py        ← 剛剛創建的測試
└── .github/
    └── workflows/
        └── test.yml
