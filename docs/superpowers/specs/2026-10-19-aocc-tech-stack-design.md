# AOCC Copilot — Teknoloji ve Ortam Kararları

- **Tarih:** 2026-10-19
- **Durum:** Onaylandı (kapsam: yalnızca teknoloji, `.env.example`, `.gitignore`)

## Amaç

İGA Havalimanı Operasyon Kontrol Merkezi (AOCC) için bir asistan. Asistan, canlı
operasyon verisini (uçuş, gate/stand, kaynak, olay) tool'lar aracılığıyla sorgulayıp
özetler. İlk aşamada gerçek sistemler (AODB, RMS vb.) yerine mock veri kullanılır.

Bu doküman kod yazımından önce alınan teknoloji ve ortam kararlarını kaydeder.

## Kesinleşen kararlar

| Katman | Seçim | Gerekçe |
|---|---|---|
| Dil | Python 3.12 | Anthropic SDK 1.x en az Python 3.10 ister; 3.12 olgun ve geniş destekli. |
| Paket/ortam yönetimi | uv + `pyproject.toml` | Hızlı, `uv.lock` ile tekrarlanabilir kurulum, venv yönetimi dahil. |
| Web framework | FastAPI + Uvicorn | Async, otomatik `/docs`, SSE ile streaming yanıt. |
| LLM erişimi | Anthropic API'ye doğrudan, resmî `anthropic` Python SDK | Kimlik bilgisi `ANTHROPIC_API_KEY` ortam değişkeninden. |
| Varsayılan model | `claude-opus-5-5` | `.env` üzerinden değiştirilebilir. |
| Veritabanı | PostgreSQL 17, Docker Compose ile | Mock operasyon verisi burada tutulur; üretime yakın. |
| DB erişimi | SQLAlchemy 2.x (async) + asyncpg, Alembic | Gerçek kaynağa geçişte yalnızca bağlantı değişir. |
| Config | pydantic-settings | `.env` tip kontrollü okunur; hatalı/eksik değer açılışta yakalanır. |
| Test / kalite | pytest (+ pytest-asyncio), ruff | |
| Arayüz | Şimdilik yalnızca backend API; React frontend sonra | `.gitignore` frontend'e hazır tutulur. |

Planlanan klasör düzeni: `backend/` (FastAPI), `frontend/` (React, ileride),
kökte `docker-compose.yml` ve `.env.example`.

## Ortam değişkenleri (`.env.example`)

Kökte tek bir `.env` dosyası kullanılır. Şimdilik yalnızca Anthropic/Claude bölümü
tanımlıdır:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `ANTHROPIC_API_KEY` | (boş) | Zorunlu. Gerçek değer yalnızca commit edilmeyen `.env` dosyasında. |
| `ANTHROPIC_MODEL` | `claude-opus-5-5` | Ana model. |
| `ANTHROPIC_TEMP_MODEL` | (boş) | Ana modeli değiştirmeden geçici olarak denenecek ikinci model. Boş = deneme kapalı. |
| `ANTHROPIC_MAX_TOKENS` | `16000` | Streaming olmayan çağrılarda SDK zaman aşımına takılmayan güvenli üst sınır. |
| `ANTHROPIC_EFFORT` | `medium` | `low` / `medium` / `high` / `xhigh` / `max`. Opus 5.5'te thinking kapatılamaz; maliyet/derinlik effort ile ayarlanır. Varsayılanla aynı olsa da görünür olsun diye açıkça yazılır. |

Notlar:
- `temperature` parametresi `claude-opus-5-5`'te kaldırıldığı için (400 döner) config'e eklenmez.
- Production'da `ANTHROPIC_API_KEY` `.env` yerine bir secret store'dan (Vault, Key Vault vb.) gelmelidir.

## `.gitignore` kapsamı

Gizli değerler (`.env`, `.env.*`, `.env.example` hariç), Python/uv çıktıları
(`uv.lock` commit edilir), test/araç cache'leri, Node/React çıktıları (ileride),
IDE dosyaları (Visual Studio, VS Code, JetBrains), işletim sistemi dosyaları, loglar,
Claude Code kişisel ayarları (`.claude/settings.local.json`) ve plan çalışma alanı
(`.superpowers/`). Ortak `.claude/settings.json` commit edilir.

## Açık kararlar

- **Agent döngüsü mimarisi:** manuel tool-use döngüsü veya SDK Tool Runner (beta).
  Değerlendirmede manuel döngü, kontrol ve denetlenebilirlik nedeniyle önerildi;
  karar ertelendi. Managed Agents, mock veri yerel Postgres'te olduğu için uygun bulunmadı.

## Ertelenen kararlar

- Uygulama değişkenleri (`APP_ENV`, `APP_HOST`, `APP_PORT`, `LOG_LEVEL`).
- PostgreSQL bağlantı değişkenleri (`POSTGRES_*`) ve bağlantı URL'sinin nasıl kurulacağı.
- CORS ayarları (React frontend ile birlikte).
- Kimlik doğrulama/yetkilendirme.
- SDK timeout/retry ayarları (SDK varsayılanları şimdilik yeterli).
