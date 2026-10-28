"""Asosiy oqimni tekshiradi: SOS -> assign -> arrive -> done. Ishga tushirish: pytest"""
import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["ANTHROPIC_API_KEY"] = ""          # testda faqat qoidalar

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

SOS = {"fullName": "Vali Aliyev", "phone": "+998901234567", "lat": 41.2995,
       "lng": 69.2401, "accuracy": 12, "text": "Dadam hushidan ketdi, nafas olmayapti"}


def test_full_flow():
    with TestClient(app) as c:
        call = c.post("/api/calls", json=SOS).json()
        assert call["services"] == "103" and call["severity"] == "HIGH" and call["status"] == "NEW"

        assert len(c.get("/api/calls/active").json()) == 1

        assert c.post(f"/api/calls/{call['id']}/assign").json()["status"] == "ENROUTE"
        d = c.get(f"/api/calls/{call['id']}").json()
        assert d["unit"]["busy"] is True and d["etaMinutes"] >= 1

        # kechiksa: keyingi brigada (ikkinchi tez yordam)
        first = d["unit"]["id"]
        c.post(f"/api/calls/{call['id']}/reassign")
        assert c.get(f"/api/calls/{call['id']}").json()["unit"]["id"] != first

        assert c.post(f"/api/calls/{call['id']}/arrive").json()["status"] == "ARRIVED"
        assert c.post(f"/api/calls/{call['id']}/done").json()["status"] == "DONE"


def test_no_free_unit_and_404():
    with TestClient(app) as c:
        assert c.get("/api/calls/99999").status_code == 404
        gas = {**SOS, "text": "Gaz hidi keldi"}
        ids = [c.post("/api/calls", json=gas).json()["id"] for _ in range(3)]
        assert c.post(f"/api/calls/{ids[0]}/assign").status_code == 200
        assert c.post(f"/api/calls/{ids[1]}/assign").status_code == 200
        assert c.post(f"/api/calls/{ids[2]}/assign").status_code == 409   # 104 brigadalar tugadi


def test_validation_and_chat():
    with TestClient(app) as c:
        assert c.post("/api/calls", json={"lat": 1, "lng": 2, "text": ""}).status_code == 422
        r = c.post("/api/chat/kardiolog", json={"text": "Yurak og'riyapti"}).json()
        assert r["sender"] == "AI"
        h = c.get("/api/chat/kardiolog").json()
        assert [m["sender"] for m in h] == ["PATIENT", "AI"]
