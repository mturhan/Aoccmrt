"""Ana modele tek bir soru gönderip yanıtı ve token kullanımını yazdırır.

Repo kökünden çalıştırın: python scripts/first_call.py
"""

import sys
from pathlib import Path

# Script doğrudan çalıştırıldığında sys.path[0] scripts/ olur; backend paketinin
# bulunabilmesi için repo kökünü ekliyoruz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.llm import MODEL, client

QUESTION = "Bir havalimanı operasyon merkezi asistanının görevini tek cümleyle anlat"


def main() -> None:
    response = client.messages.create(
        model=MODEL,
        # Thinking de çıktı token'ı harcadığı için düşük bir sınır yanıtı kesebilir.
        max_tokens=16000,
        messages=[{"role": "user", "content": QUESTION}],
    )

    # Yanıtta thinking blokları da olabilir; yalnızca metin bloklarını alıyoruz.
    answer = "".join(block.text for block in response.content if block.type == "text")

    print(f"Yanıt: {answer}")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Durma sebebi: {response.stop_reason}")


if __name__ == "__main__":
    main()
