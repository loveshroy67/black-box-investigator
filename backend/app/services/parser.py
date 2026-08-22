from pathlib import Path


TEXT_EXTENSIONS = {
    ".log",
    ".txt",
    ".csv",
    ".json",
    ".md"
}


def detect_file_type(filename: str) -> str:
    extension = Path(filename).suffix.lower()

    if extension in TEXT_EXTENSIONS:
        return "text"

    if extension in {".png", ".jpg", ".jpeg", ".webp"}:
        return "image"

    if extension == ".pdf":
        return "pdf"

    return "unknown"


def extract_text(file_path: str, file_type: str) -> str:
    if file_type != "text":
        return ""

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:
            return file.read()

    except Exception:
        return ""