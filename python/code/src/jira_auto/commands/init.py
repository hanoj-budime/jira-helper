import argparse
import os
import sys

from ..models import write_create_template


def cmd_init(args: argparse.Namespace) -> int:
    if os.path.exists(args.output):
        print(f"Refusing to overwrite existing file: {args.output}", file=sys.stderr)
        return 2
    write_create_template(args.output)
    print(f"Template created: {args.output}")
    return 0
