import requests
from urllib.parse import urlunparse


def get_word_info(word: str) -> dict:
    clean_word = word.strip().lower()
    if not clean_word:
        return {"word": "", "translation": "", "phonetic": ""}

    translation = ""
    phonetic = ""

    try:
        url = urlunparse(("https", "dictionary.skyeng.ru", "/api/public/v1/words/search", "", f"search={clean_word}", ""))
        response = requests.get(url, timeout=6)

        if response.status_code == 200:
            data = response.json()
            for entry in data:
                if entry.get("text", "").lower() == clean_word:
                    meanings = entry.get("meanings", [])
                    if meanings:
                        first_meaning = next(iter(meanings))
                        phonetic = first_meaning.get("transcription", "")
                        trans_obj = first_meaning.get("translation", {})
                        translation = trans_obj.get("text", "")
                        break
    except Exception as e:
        print(f"Ошибка при загрузке '{clean_word}': {e}")

    return {
        "word": clean_word,
        "translation": translation.lower() if translation else "Не найдено",
        "phonetic": f"[{phonetic}]" if phonetic else ""
    }


def import_word_list(raw_text: str) -> list[dict]:
    results = []
    for line in raw_text.strip().splitlines():
        word = line.strip()
        if word:
            results.append(get_word_info(word))
    return results


if __name__ == "__main__":
    print(get_word_info("serendipity"))
    for item in import_word_list("resilience\neloquent\nalgorithm"):
        print(f"{item['word']} {item['phonetic']} -> {item['translation']}")
