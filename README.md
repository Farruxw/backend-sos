# Smart SOS — Backend (Python / FastAPI)

Tezkor chaqiruv ilovasining **Python 3.10+ · FastAPI · SQLAlchemy** backendi.
Fuqaro SOS yuboradi → AI xizmat va xavfni aniqlaydi → eng yaqin bo'sh brigada biriktiriladi → yetib kelishigacha kuzatiladi.

✅ Sinalgan: 3 ta avtomatik test o'tdi, server ishga tushib ishladi.

---

## 1. Ishga tushirish (qadam-baqadam)

Kerak: **Python 3.10 yoki yangi** (`python --version` bilan tekshiring).

### 1-qadam. Papkaga kiring va virtual muhit yarating
```bash
cd smart-sos-backend-py
python -m venv .venv
```

### 2-qadam. Virtual muhitni yoqing
| Tizim | Buyruq |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

### 3-qadam. Kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 4-qadam. Serverni ishga tushiring
```bash
uvicorn app.main:app --reload
```
Server `http://localhost:8000` da ishlaydi. Birinchi ishga tushishda jadvallar va 8 ta namunaviy brigada avtomatik yaratiladi.

### 5-qadam. Tekshiring
- Brauzerda **http://localhost:8000/docs** — barcha API ni shu yerdan bosib sinash mumkin (Swagger).
- yoki `http://localhost:8000/health` → `{"status":"ok"}`

> Telefondan sinash uchun: `uvicorn app.main:app --host 0.0.0.0 --port 8000`, so'ng `http://KOMPYUTER_IP:8000`.

---

## 2. Sozlamalar (ixtiyoriy)

Hech narsa sozlamasangiz ham ishlaydi: baza **SQLite** (`smartsos.db` fayli), AI o'rniga **oddiy qoidalar**.

| O'zgaruvchi | Nima uchun | Standart |
|---|---|---|
| `DATABASE_URL` | Baza manzili | `sqlite:///./smartsos.db` |
| `ANTHROPIC_API_KEY` | Claude AI kaliti. Bo'lmasa qoidalar ishlaydi | bo'sh |
| `ANTHROPIC_MODEL` | Claude modeli | `claude-haiku-5-5` |

**O'rnatish:**
```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

### PostgreSQL ishlatish
1. `requirements.txt` da `psycopg[binary]` qatoridagi `#` ni olib tashlang, `pip install -r requirements.txt`.
2. Baza yarating: `createdb smartsos`
3. Manzilni bering:
```bash
export DATABASE_URL=postgresql+psycopg://smartsos:PAROL@localhost:5432/smartsos
```

---

## 3. Testlar
```bash
pytest
```
Tekshiradi: SOS → biriktirish → qayta biriktirish → yetib keldi → yakunlandi; bo'sh brigada qolmaganda `409`; noto'g'ri so'rovda `422`; chat.

---

## 4. Tuzilishi

```
smart-sos-backend-py/
├── requirements.txt        kutubxonalar ro'yxati
├── .env.example            sozlamalar namunasi
├── README.md               shu fayl
├── app/
│   ├── main.py             dastur kirish nuqtasi, CORS, jadvallarni yaratish
│   ├── config.py           muhit o'zgaruvchilari
│   ├── database.py         baza ulanishi va sessiya
│   ├── models.py           jadvallar: Call, Unit, ChatMessage, Status
│   ├── schemas.py          API kirish/chiqish shakllari (JSON)
│   ├── seed.py             namunaviy 8 ta brigada
│   ├── routers/
│   │   ├── calls.py        /api/calls ...
│   │   └── chat.py         /api/chat/{mutaxassis}
│   └── services/
│       ├── dispatch.py     brigada tanlash (biznes mantiq)
│       └── ai_triage.py    AI saralash + zaxira qoidalar
└── tests/test_api.py
```

Qatlamlar: **router** (so'rovni qabul qiladi) → **service** (mantiq) → **models/database** (PostgreSQL/SQLite).

---

## 5. Fayllar nima qiladi

### `app/models.py` — jadvallar
| Sinf | Jadval | Saqlaydi |
|---|---|---|
| `Call` | `calls` | Fuqaro ismi/telefoni, koordinata, matn, xizmatlar (`"103,101"`), xavf (`HIGH/MEDIUM/LOW`), AI xulosasi, holat, brigada (`unit_id`), vaqtlar |
| `Unit` | `units` | Brigada nomi, xizmat (101–104), joylashuv, `busy` (band/bo'sh), tarkib, mashina raqami |
| `ChatMessage` | `chat_messages` | Mutaxassis, yuboruvchi (`PATIENT/DOCTOR/AI`), matn, vaqt |
| `Status` | — | `NEW` → `ENROUTE` → `ARRIVED` → `DONE` (yoki `CANCELLED`) |

### `app/services/dispatch.py` — brigadani boshqarish
- `assign_nearest` — xizmat bo'yicha **eng yaqin bo'sh** brigadani tanlaydi (Haversine formulasi), band qiladi, holat `ENROUTE`. Bo'sh brigada yo'q bo'lsa `409`.
- `reassign` — brigada kechiksa: eskisini bo'shatadi, **keyingi eng yaqinini** yuboradi.
- `arrive` / `done` / `cancel` — holatni o'zgartiradi; `done` va `cancel` brigadani bo'shatadi.
- `eta_minutes` — yetib kelish vaqti = masofa ÷ 30 km/soat (kamida 1 daqiqa).

### `app/services/ai_triage.py` — AI
- `triage(text)` — matnni Claude ga yuboradi, `xizmat + xavf + xulosa` oladi. **Kalit yo'q yoki xato bo'lsa** — `rules()` ishlaydi (o'zbek va rus kalit so'zlar).
- `chat_reply(mutaxassis, text)` — chat uchun AI javobi. Tashxis va dori dozasi aytilmaydi.
- AI **faqat tavsiya beradi**, yakuniy qarorni operator qabul qiladi.

### `app/routers/` — API manzillari
`calls.py` va `chat.py` — quyidagi jadval.

### Qolganlari
- `schemas.py` — JSON ni tekshiradi (masalan `lat`, `lng`, `text` majburiy; bo'sh matn `422`). JSON maydonlari camelCase (`fullName`, `unitId`, `etaMinutes`).
- `seed.py` — baza bo'sh bo'lsa, brigadalarni qo'shadi (ismlar va raqamlar o'ylab topilgan).
- `database.py` — SQLite/PostgreSQL ulanishi, har so'rovga alohida sessiya.

---

## 6. REST API

| Metod | Manzil | Vazifa |
|---|---|---|
| POST | `/api/calls` | SOS yuborish, AI saralaydi, holat `NEW` |
| GET | `/api/calls/active` | Faol chaqiruvlar (operator uchun) |
| GET | `/api/calls/{id}` | Chaqiruv + brigada + `etaMinutes` |
| POST | `/api/calls/{id}/assign` | Eng yaqin bo'sh brigadani biriktirish |
| POST | `/api/calls/{id}/reassign` | Kechiksa, keyingisini yuborish |
| POST | `/api/calls/{id}/arrive` | Brigada yetib keldi |
| POST | `/api/calls/{id}/done` | Yakunlandi |
| POST | `/api/calls/{id}/cancel` | Fuqaro bekor qildi |
| GET / POST | `/api/chat/{mutaxassis}` | Chat tarixi / xabar yuborish |
| GET | `/health` | Server tirikligini tekshirish |

**Namuna (SOS yuborish):**
```bash
curl -X POST http://localhost:8000/api/calls \
  -H "Content-Type: application/json" \
  -d '{"fullName":"Vali Aliyev","phone":"+998901234567",
       "lat":41.2995,"lng":69.2401,"accuracy":12,
       "text":"Dadam hushidan ketdi, nafas olmayapti"}'
```
**Javob:** `services: "103"`, `severity: "HIGH"`, `status: "NEW"`.

---

## 7. React frontendni ishga tushirish

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend odatda `http://localhost:5173` da ochiladi va `VITE_API_BASE_URL=http://localhost:8000` orqali backendga ulanadi. Batafsil qo'llanma: [frontend/README.md](frontend/README.md).

## 8. SOS oqimi
1. Fuqaro SOS bosadi → `POST /api/calls`
2. `ai_triage.triage()` → xizmat, xavf, xulosa
3. Chaqiruv `NEW` bilan saqlanadi
4. Operator `POST /{id}/assign` → eng yaqin brigada → `ENROUTE`
5. Fuqaro `GET /{id}` bilan holat va vaqtni ko'radi
6. Brigada `POST /{id}/arrive` → `ARRIVED`, keyin `POST /{id}/done` → `DONE`, brigada bo'shaydi

---

## 9. Frontend API ulanishi
```js
const r = await fetch("http://localhost:8000/api/calls", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ fullName, phone, lat, lng, accuracy, text })
});
const call = await r.json();   // call.id, call.services, call.severity
```

---

## 10. Hali yo'q narsalar
- **Autentifikatsiya va rollar** — hozir API hamma uchun ochiq.
- **Real vaqtli GPS** (WebSocket), brigada harakati.
- **SMS shlyuzi, OneID**, pasport/JShShIR tekshiruvi.
- **Bir nechta xizmat**: `"103,101"` bo'lsa, hozir faqat **birinchisiga** brigada biriktiriladi.
- **Navbat**, HTTPS, audit jurnali, admin statistikasi, Alembic migratsiyalari.
