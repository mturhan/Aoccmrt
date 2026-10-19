"""Modelin aritmetikte ne kadar tutarlı olduğunu ölçen deney.

Aynı 12 sayının toplamı aynı istekle beş kez sorulur; her yanıt Python'un
hesapladığı gerçek toplamla karşılaştırılır.

Repo kökünden çalıştırın: python scripts/calc_number.py
"""

import re
import sys
from pathlib import Path

# Script doğrudan çalıştırıldığında sys.path[0] scripts/ olur; backend paketinin
# bulunabilmesi için repo kökünü ekliyoruz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.llm import MODEL, client

NUMBERS = [
    15000,
    18452,
    20917,
    17621,
    5000,
    6000,
    15000,
    18452,
    20917,
    17621,
    5000,
    6000,
]
ATTEMPTS = 5
MAX_TOKENS = 300

PROMPT = (
    "Şu sayıların toplamı kaçtır? "
    + ", ".join(str(n) for n in NUMBERS)
    + ". Yalnızca sonucu sayı olarak yaz."
)

# Binlik ayırıcılı ("165.980", "165,980", "165 980") ya da düz ("165980") sayılar.
NUMBER_PATTERN = re.compile(r"\d{1,3}(?:[.,\s ]\d{3})+|\d+")


def answer_text(response) -> str:
    # Yanıtta thinking blokları da olabilir; yalnızca metin bloklarını alıyoruz.
    return "".join(block.text for block in response.content if block.type == "text")


def parse_total(text: str) -> int | None:
    # Metindeki son sayı, modelin vardığı sonuç kabul edilir.
    matches = NUMBER_PATTERN.findall(text)
    if not matches:
        return None
    return int(re.sub(r"\D", "", matches[-1]))


def main() -> None:
    expected = sum(NUMBERS)
    print(f"Gerçek toplam (Python): {expected}")
    print(f"Soru: {PROMPT}")
    print()

    correct = 0
    for attempt in range(1, ATTEMPTS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": PROMPT}],
        )
        raw = answer_text(response)

        # Yanıt max_tokens'ta kesildiyse içindeki sayı nihai sonuç olmayabilir.
        parsed = None if response.stop_reason == "max_tokens" else parse_total(raw)
        if parsed is None:
            verdict = "AYRIŞTIRILMADI"
        elif parsed == expected:
            verdict = "DOĞRU"
            correct += 1
        else:
            verdict = "YANLIŞ"

        print(f"── Deneme {attempt} ──")
        print(f"Ham cevap: {raw!r}")
        print(f"Durma sebebi: {response.stop_reason}")
        print(f"Sonuç: {verdict}")
        print()

    print(f"{ATTEMPTS} denemeden {correct} doğru")


if __name__ == "__main__":
    main()
