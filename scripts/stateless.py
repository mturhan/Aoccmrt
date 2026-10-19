"""API'nin durumsuz olduğunu gösteren deney.

Model önceki çağrıları hatırlamaz; konuşma geçmişi her istekte istemci tarafından
yeniden gönderilmelidir. Üç çağrı yapılır:
  1. İsim söylenir.
  2. İsim, geçmiş olmadan sorulur (model bilemez).
  3. İsim, 1. adımın mesajı ve modelin yanıtıyla birlikte sorulur (model bilir).

Repo kökünden çalıştırın: python scripts/stateless.py
"""

import sys
from pathlib import Path

# Script doğrudan çalıştırıldığında sys.path[0] scripts/ olur; backend paketinin
# bulunabilmesi için repo kökünü ekliyoruz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.llm import MODEL, client

INTRODUCTION = "Benim adım Türkay bunu hatırla."
QUESTION = "Benim adım neydi?"


def ask(messages: list[dict]):
    return client.messages.create(model=MODEL, max_tokens=16000, messages=messages)


def answer_text(response) -> str:
    # Yanıtta thinking blokları da olabilir; yalnızca metin bloklarını alıyoruz.
    return "".join(block.text for block in response.content if block.type == "text")


def show(title: str, messages: list[dict], response) -> None:
    print(f"── {title} ──")
    print(f"Gönderilen mesaj sayısı: {len(messages)}")
    print(f"Yanıt: {answer_text(response)}")
    print(f"Input tokens: {response.usage.input_tokens}")
    print()


def main() -> None:
    first_messages = [{"role": "user", "content": INTRODUCTION}]
    first = ask(first_messages)
    show("1. İsim söylendi", first_messages, first)

    second_messages = [{"role": "user", "content": QUESTION}]
    second = ask(second_messages)
    show("2. Geçmiş olmadan soruldu", second_messages, second)

    # Modelin yanıtı değiştirilmeden geri gönderilir; thinking blokları da dahil.
    third_messages = [
        {"role": "user", "content": INTRODUCTION},
        {"role": "assistant", "content": first.content},
        {"role": "user", "content": QUESTION},
    ]
    third = ask(third_messages)
    show("3. Tam geçmişle soruldu", third_messages, third)


if __name__ == "__main__":
    main()
