from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "verification" / "evidence"
DB_PATH = EVIDENCE / "database" / "verify_persistence.db"
OUT = EVIDENCE / "database" / "verify_persistence.json"

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
os.environ["UPLOAD_DIR"] = str((EVIDENCE / "uploads").resolve())
os.environ["PROCESSED_DIR"] = str((EVIDENCE / "processed").resolve())
os.environ["EXPORT_DIR"] = str((EVIDENCE / "exports").resolve())
os.environ["APP_AUTO_CREATE_DB"] = "true"

sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.database import Base, engine  # noqa: E402
from backend.app.main import app  # noqa: E402


def main() -> int:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    customer = client.post("/api/customers", json={"customer_code": "PT-PERSIST", "full_name": "Persist Patient"}).json()
    document = client.post("/api/documents/manual", json={"customer_id": customer["id"], "source_name": "Persist note", "text": "Persisted text."}).json()

    engine.dispose()
    connection = sqlite3.connect(DB_PATH)
    try:
        counts = {
            "customers": connection.execute("select count(*) from customers").fetchone()[0],
            "documents": connection.execute("select count(*) from documents").fetchone()[0],
            "audit_logs": connection.execute("select count(*) from audit_logs").fetchone()[0],
        }
    finally:
        connection.close()

    result = {
        "customer_id": customer["id"],
        "document_id": document["document_id"],
        "counts_after_reopen": counts,
        "pass": counts["customers"] == 1 and counts["documents"] == 1 and counts["audit_logs"] >= 2,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
