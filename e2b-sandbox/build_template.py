#!/usr/bin/env python3
"""Build a reusable Aliyun FC E2B Claude Code sandbox template."""

from __future__ import annotations

import argparse
import time

from e2b import Template, default_build_logger

from config import (
    cpu_count,
    e2b_opts,
    from_image,
    memory_mb,
    save_template_state,
    template_name_base,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build Claude Code template from Aliyun FC E2B registry image"
    )
    p.add_argument(
        "--name",
        default=None,
        help="Template name (default: E2B_TEMPLATE_NAME or claude-code)",
    )
    p.add_argument(
        "--unique",
        action="store_true",
        help="Append unix timestamp to template name",
    )
    p.add_argument(
        "--from-image",
        default=None,
        help="Override E2B_FROM_IMAGE",
    )
    p.add_argument("--cpu", type=int, default=None, help="CPU count (default 2)")
    p.add_argument(
        "--memory-mb", type=int, default=None, help="Memory MB (default 8192)"
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    image = args.from_image or from_image()
    name = args.name or template_name_base()
    if args.unique:
        name = f"{name}-{int(time.time())}"

    opts = e2b_opts()
    print(f"Building template: {name}")
    print(f"From image:        {image}")
    print(f"API URL:           {opts['api_url']}")
    print(f"Domain:            {opts['domain']}")
    print(f"CPU / Memory:      {args.cpu or cpu_count()} / {args.memory_mb or memory_mb()} MB")

    build = Template.build(
        Template().from_image(image),
        name=name,
        cpu_count=args.cpu or cpu_count(),
        memory_mb=args.memory_mb or memory_mb(),
        on_build_logs=default_build_logger(),
        **opts,
    )

    save_template_state(build.name, from_image_value=image)
    print(f"template: {build.name}")
    print("Saved to .template-state.json — reuse this name for Sandbox.create()")


if __name__ == "__main__":
    main()
