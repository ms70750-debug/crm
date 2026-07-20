import argparse
import os
import sys

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.database_target_guard import (  # noqa: E402
    APPROVED_MESSAGE,
    DIVERGENT_MESSAGE,
    EXPECTED_FINGERPRINT_ENV,
    DatabaseTargetGuardError,
    calculate_database_target_fingerprint,
    validate_database_target,
)


def _url_from_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida o destino PostgreSQL oficial sem expor conexao.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--url-env", default="DIRECT_URL")
    validate_parser.add_argument("--fingerprint-env", default=EXPECTED_FINGERPRINT_ENV)
    validate_parser.add_argument("--environment", default=os.environ.get("APP_ENV", "production"))

    fingerprint_parser = subparsers.add_parser("fingerprint")
    fingerprint_parser.add_argument("--url-env", default="DIRECT_URL")
    fingerprint_parser.add_argument("--environment", default=os.environ.get("APP_ENV", "production"))

    args = parser.parse_args(argv)
    try:
        database_url = _url_from_env(args.url_env)
        if args.command == "fingerprint":
            print(calculate_database_target_fingerprint(database_url, environment=args.environment))
            return 0

        validate_database_target(
            database_url,
            os.environ.get(args.fingerprint_env, ""),
            environment=args.environment,
        )
        print(APPROVED_MESSAGE)
        return 0
    except DatabaseTargetGuardError:
        print(DIVERGENT_MESSAGE, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
