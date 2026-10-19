"""Claude istemcisi ve model ayarları.

Ayarlar proje kökündeki .env dosyasından (python-dotenv ile) yüklenir. Ortamda
zaten tanımlı değişkenler .env'deki değerlerin önüne geçer. Zorunlu bir değişken
eksik veya boşsa modül import edilirken ConfigError fırlatılır.
"""

import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

REQUIRED_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_TEMP_MODEL",
)


class ConfigError(RuntimeError):
    """Zorunlu bir ortam değişkeni eksik olduğunda fırlatılır."""


def _load_settings() -> dict[str, str]:
    load_dotenv(ENV_FILE)

    # Boş değer de eksik sayılır; .env.example kopyalanıp doldurulmadıysa böyle olur.
    settings = {name: os.getenv(name, "").strip() for name in REQUIRED_VARS}
    missing = [name for name, value in settings.items() if not value]
    if missing:
        raise ConfigError(
            "Zorunlu ortam değişkenleri eksik veya boş: "
            + ", ".join(missing)
            + f". Bu değişkenleri {ENV_FILE} dosyasında ya da ortamda tanımlayın "
            "(şablon için .env.example dosyasına bakın)."
        )
    return settings


_settings = _load_settings()

MODEL: str = _settings["ANTHROPIC_MODEL"]
TEMP_MODEL: str = _settings["ANTHROPIC_TEMP_MODEL"]

client = Anthropic(api_key=_settings["ANTHROPIC_API_KEY"])
