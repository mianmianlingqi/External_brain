from __future__ import annotations

import argparse
import os
import time
from pathlib import Path


def _serve_target(target: str) -> None:
    from brain import serve_target

    port = int(os.environ.get("PORT", "8080"))
    view_url, agent_url, stop = serve_target(target, host="0.0.0.0", port=port)
    print(view_url)
    print(agent_url)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        stop()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m brain")
    sub = parser.add_subparsers(dest="command", required=True)
    serve_p = sub.add_parser("serve")
    serve_p.add_argument("target")
    expand_p = sub.add_parser("expand")
    expand_p.add_argument("target")
    expand_p.add_argument("direction")
    expand_p.add_argument("--kind", default="server")
    expand_p.add_argument("--public-url", default="")
    args = parser.parse_args(argv)
    if args.command == "serve":
        _serve_target(args.target)
        return
    from brain import expand

    public_url = args.public_url or os.environ.get("PUBLIC_URL", "").strip() or None
    brain, agent_secret, view_secret = expand(
        args.target, args.direction, kind=args.kind, public_url=public_url
    )
    root = Path(args.target) / ".brain"
    print(root.joinpath("agent.address").read_text(encoding="utf-8"))
    print(root.joinpath("view.link").read_text(encoding="utf-8"))
    _ = brain, agent_secret, view_secret


if __name__ == "__main__":
    main()
