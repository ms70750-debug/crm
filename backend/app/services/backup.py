import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import BackupAuditLog


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_sqlite_backup(source: Path, target_dir: Path, db: Session | None = None) -> Path:
    if not source.exists():
        raise RuntimeError("Banco ficticio de origem nao encontrado")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{source.stem}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.backup.sqlite"
    shutil.copy2(source, target)
    checksum = file_checksum(target)
    if db:
        db.add(BackupAuditLog(operation="backup", target=target.name, status="ok", checksum=checksum, metadata_json=json.dumps({"demo": True})))
        db.commit()
    return target


def restore_sqlite_backup(backup_path: Path, restore_path: Path, db: Session | None = None) -> Path:
    if not backup_path.exists():
        raise RuntimeError("Backup ficticio nao encontrado")
    restore_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_path, restore_path)
    checksum = file_checksum(restore_path)
    if db:
        db.add(BackupAuditLog(operation="restore", target=restore_path.name, status="ok", checksum=checksum, metadata_json=json.dumps({"demo": True})))
        db.commit()
    return restore_path
