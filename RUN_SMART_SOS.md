# Smart SOS — Backend va Frontendni ishga tushirish

Ushbu yo‘riqnoma Smart SOS backendini va React frontendini bitta loyihadan ishlatish uchun.

## Talablar

- macOS
- Python 3.10 yoki undan yangi
- Node.js 20 yoki undan yangi

Node.js/NPM mavjudligini tekshiring:

```bash
node --version
npm --version
python3 --version
```

Node.js yo‘q bo‘lsa, Homebrew orqali o‘rnating:

```bash
brew install node
```

## 1-qadam. Loyihaga kiring

```bash
cd /Users/macbookair/Downloads/smart-sos-backend-py
```

## 2-qadam. Backendni tayyorlang

Yangi terminalni oching va backend kutubxonalarini o‘rnating:

```bash
cd /Users/macbookair/Downloads/smart-sos-backend-py
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Backendni ishga tushiring:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend `http://localhost:8000` manzilida ishga tushadi.

Tekshirish:

```bash
curl http://localhost:8000/health
```

Javob:

```json
{"status":"ok"}
```

## 3-qadam. Frontendni tayyorlang

Ikkinchi terminalni oching:

```bash
cd /Users/macbookair/Downloads/smart-sos-backend-py/frontend
npm install
cp .env.example .env
```

`.env` faylining mazmuni:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Frontendni ishga tushiring:

```bash
npm run dev
```

Vite terminalda ko‘rsatgan manzilni brauzerda oching, odatda: `http://localhost:5173`.

## Bitta buyruq bilan backendni ishga tushirish (backend terminali)

Backend virtual muhit va kutubxonalar bir marta o‘rnatilgach, keyingi safar faqat quyidagini bajaring:

```bash
cd /Users/macbookair/Downloads/smart-sos-backend-py
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Bitta buyruq bilan frontendni ishga tushirish (frontend terminali)

```bash
cd /Users/macbookair/Downloads/smart-sos-backend-py/frontend
npm run dev
```

## Foydalanish tartibi

1. Birinchi terminalda backendni ishga tutiring.
2. Backend `http://localhost:8000` manzilini ochib, `{"status":"ok"}` javobini ko‘rsating.
3. Ikkinchi terminalda frontendni ishga tushiring.
4. Brauzerda `http://localhost:5173` manzilini oching.
5. Backend yoki frontendni to‘xtatish uchun tegishli terminalda `Ctrl+C` tugmalarini bosing.

## To‘xtatish va qayta ishga tushirish

Backend yoki frontend terminalining bitta eng muhim qoidasi: har bir terminalda faqat bitta server protsessi qoladi. Backendni to‘xtatgach, frontend terminalini yopmang; frontend keyin backend qayta ulanganidan avtomatik ishga tushadi.

## Muammolar

### `npm: command not found`

Node.js/NPM o‘rnatilmagan. Terminalda quyidagini bajaring:

```bash
brew install node
exec zsh
```

### `uvicorn: command not found`

Backend virtual muhiti faollashtirilmagan:

```bash
cd /Users/macbookair/Downloads/smart-sos-backend-py
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Frontend backendga ulanmasa

1. Backend terminalida backend ishlab turganini tekshiring.
2. [smart-sos-backend-py/frontend/.env](frontend/.env) faylida quyidagi qiymat borligini tekshiring:

```env
VITE_API_BASE_URL=http://localhost:8000
```

3. Frontendni `Ctrl+C` bilan to‘xtating va qayta ishga tushiring.

### Port band bo‘lsa

```bash
lsof -i :8000
lsof -i :5173
```

Kerakli terminaldagi serverni `Ctrl+C` bilan to‘xtating.
