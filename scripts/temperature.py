"""Sıcaklığın (temperature) yanıt çeşitliliğine etkisini gösteren deney.

Aynı soru her sıcaklıkta üç kez sorulur. Model varsayılan olarak .env'deki
ANTHROPIC_TEMP_MODEL'dir; --model ile başka bir model verilebilir.
Güncel modeller (ör. claude-opus-5-5, claude-sonnet-5-5) temperature'ı kabul etmez
ve 400 döner; API hataları yakalanıp yazdırılır, deney bir sonraki çağrıyla devam eder.

Repo kökünden çalıştırın: python scripts/temperature.py [--model MODEL]
"""

import argparse
import sys
from pathlib import Path

# Script doğrudan çalıştırıldığında sys.path[0] scripts/ olur; backend paketinin
# bulunabilmesi için repo kökünü ekliyoruz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic

from backend.llm import TEMP_MODEL, client

PROMPT = "4 Kelimelik havalimanı operasyon merkezi sloganı yaz"
TEMPERATURES = (0.2, 0.7, 1.0)
REPEATS = 3


def answer_text(response) -> str:
    # Yanıtta thinking blokları da olabilir; yalnızca metin bloklarını alıyoruz.
    return "".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--model", default=TEMP_MODEL, help="Varsayılan: ANTHROPIC_TEMP_MODEL"
    )
    model = parser.parse_args().model

    print(f"Model: {model}")
    print(f"Soru: {PROMPT}")

    for temperature in TEMPERATURES:
        print()
        print(f"── T={temperature} ──")
        for attempt in range(1, REPEATS + 1):
            try:
                # SDK 1.x temperature'ı parametre olarak kaldırdı; onu hâlâ kabul eden
                # modeller için değer istek gövdesine doğrudan eklenir.
                response = client.messages.create(
                    model=model,
                    max_tokens=16000,
                    messages=[{"role": "user", "content": PROMPT}],
                    extra_body={"temperature": temperature},
                )
            except anthropic.APIStatusError as error:
                # 400 (ör. modelin temperature'ı desteklememesi), 401, 404, 429, 5xx...
                print(f"{attempt}. HATA {error.status_code}: {error.message}")
                continue
            except anthropic.APIConnectionError as error:
                print(f"{attempt}. BAĞLANTI HATASI: {error}")
                continue

            print(f"{attempt}. {answer_text(response).strip()}")


if __name__ == "__main__":
    main()
