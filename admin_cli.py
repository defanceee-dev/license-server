import argparse
import json

from db import init_db
from license_service import create_license, extend_license, list_licenses, revoke_license


def main() -> None:
    parser = argparse.ArgumentParser(description="License admin CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create_p = sub.add_parser("create")
    create_p.add_argument("--days", type=int, required=True)
    create_p.add_argument("--plan", type=str, required=True)
    create_p.add_argument("--notes", type=str, default=None)

    extend_p = sub.add_parser("extend")
    extend_p.add_argument("--key", type=str, required=True)
    extend_p.add_argument("--days", type=int, required=True)

    revoke_p = sub.add_parser("revoke")
    revoke_p.add_argument("--key", type=str, required=True)

    sub.add_parser("list")

    args = parser.parse_args()
    init_db()

    if args.cmd == "create":
        print(json.dumps(create_license(args.days, args.plan, args.notes), indent=2))
    elif args.cmd == "extend":
        print(json.dumps(extend_license(args.key, args.days), indent=2))
    elif args.cmd == "revoke":
        print(json.dumps({"ok": revoke_license(args.key)}, indent=2))
    elif args.cmd == "list":
        print(json.dumps(list_licenses(), indent=2))


if __name__ == "__main__":
    main()
