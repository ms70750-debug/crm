from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "backend"))

if not os.environ.get("DATABASE_URL") and os.environ.get("SUPABASE_DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["SUPABASE_DIRECT_URL"]

from app.database.session import SessionLocal  # noqa: E402
from app.services.admin_bootstrap import (  # noqa: E402
    ACTIVATION_BASE_URL,
    ADMIN_BOOTSTRAP_TTL_MINUTES,
    AdminBootstrapBlocked,
    AdminBootstrapError,
    create_admin_bootstrap_link,
    normalize_email,
)


def _safe_output_path(raw_path: str) -> Path:
    path = Path(raw_path).resolve()
    temp_root = Path(os.environ.get("TEMP") or os.environ.get("TMP") or "").resolve()
    in_temp = temp_root and temp_root in path.parents
    in_repo = REPO_ROOT in path.parents or path.parent == REPO_ROOT
    if path.suffix != ".txt" or not (in_temp or in_repo):
        raise RuntimeError("Nome de artifact invalido.")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria link privado de ativacao do primeiro administrador.")
    parser.add_argument("--admin-email", default=os.environ.get("ADMIN_EMAIL", ""))
    parser.add_argument("--output", default=os.environ.get("ADMIN_BOOTSTRAP_OUTPUT_FILE", "admin-activation-link.txt"))
    parser.add_argument("--activation-base-url", default=os.environ.get("ADMIN_ACTIVATION_BASE_URL", ACTIVATION_BASE_URL))
    args = parser.parse_args()

    output_path = _safe_output_path(args.output)
    email = normalize_email(args.admin_email)
    github_run_id = os.environ.get("GITHUB_RUN_ID")

    with SessionLocal() as db:
        try:
            result = create_admin_bootstrap_link(db, email, activation_base_url=args.activation_base_url, github_run_id=github_run_id)
        except AdminBootstrapBlocked:
            print("link_created=false")
            print("duplicate_admin=true")
            print("token_displayed=false")
            return 2
        except AdminBootstrapError:
            print("link_created=false")
            print("duplicate_admin=false")
            print("token_displayed=false")
            return 1

    output_path.write_text(result.link + "\n", encoding="utf-8")
    try:
        output_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    print("link_created=true")
    print(f"expires_minutes={ADMIN_BOOTSTRAP_TTL_MINUTES}")
    print("artifact_created=true")
    print("token_displayed=false")
    print(f"duplicate_admin={'true' if result.duplicate_admin else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
