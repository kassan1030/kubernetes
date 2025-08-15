from app.main import add, subtract

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_subtract_basic():
    assert subtract(5, 2) == 3

# 失敗するテストの例（後で確認のため）
def test_add_negative_numbers_fail_example():
    assert add(-1, -1) == -1 # 実際は-2だが、あえて失敗させる
