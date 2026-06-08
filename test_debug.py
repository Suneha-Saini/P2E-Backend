def test_search():
    import os
    print("=== SEARCHING FOR paddleocr/PaddleOCR IMPORTS ===")
    root_dir = r"d:\pdf-excel\backend\app"
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".py"):
                full_path = os.path.join(dirpath, f)
                try:
                    with open(full_path, "r", encoding="utf-8") as file:
                        for line_num, line in enumerate(file, 1):
                            if "paddleocr" in line or "PaddleOCR" in line:
                                print(f"Found in {full_path}:{line_num} -> {line.strip()}")
                except Exception:
                    pass

if __name__ == "__main__":
    test_search()
