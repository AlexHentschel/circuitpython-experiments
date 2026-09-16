#!/usr/bin/env python3
"""KU#1 harness feasibility probe.

Runs a *cold* local Cursor SDK agent whose ONLY persona is a specified rule-tree
copy, to test (a) that it loads that copy, (b) that the real workspace persona
does NOT leak in, and (c) that we can observe which files it consulted (so the
agent is usable as a discoverability instrument).

Isolation mechanism: the SDK local runtime resolves project settings relative to
`cwd`. We stage the given rule tree as `<tmp>/.cursor/rules` in a fresh temp dir
OUTSIDE any Cursor workspace root, point the agent at it, and control loading via
`setting_sources`.

Usage:
  CURSOR_API_KEY=... python3 run_probe.py \
      --rules personas/sentinel-rules \
      --setting project \
      --model auto \
      --prompt "..."
"""
import argparse
import os
import shutil
import sys
import tempfile

from cursor_sdk import Agent, AgentOptions, LocalAgentOptions


def _load_env_file() -> None:
    """Load KEY=VALUE lines from a sibling .env (gitignored) into os.environ.

    Lets the operator drop CURSOR_API_KEY into harness-test/.env without pasting
    it anywhere tracked. Does not override an already-set env var.
    """
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("'\"")
            os.environ.setdefault(key, val)


def main() -> int:
    _load_env_file()
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True,
                    help="Source rule-tree dir (its CONTENTS become <tmp>/.cursor/rules)")
    ap.add_argument("--setting", default="project",
                    choices=["project", "all", "user", "team", "mdm", "plugins", "none"],
                    help="setting_sources value ('none' => [], inline-only)")
    ap.add_argument("--model", default="auto")
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--prompt-file", default=None)
    ap.add_argument("--keep", action="store_true", help="keep the temp workspace")
    args = ap.parse_args()

    if not os.environ.get("CURSOR_API_KEY"):
        print("FATAL: CURSOR_API_KEY not set in env", file=sys.stderr)
        return 3

    if args.prompt_file:
        with open(args.prompt_file) as fh:
            prompt = fh.read()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("FATAL: provide --prompt or --prompt-file", file=sys.stderr)
        return 3

    src = os.path.abspath(args.rules)
    if not os.path.isdir(src):
        print(f"FATAL: rules dir not found: {src}", file=sys.stderr)
        return 3

    tmp = tempfile.mkdtemp(prefix="cursor-harness-")
    rules_dst = os.path.join(tmp, ".cursor", "rules")
    os.makedirs(os.path.dirname(rules_dst), exist_ok=True)
    shutil.copytree(src, rules_dst)
    print(f"[harness] temp workspace: {tmp}")
    print(f"[harness] staged rules:   {rules_dst}")
    print(f"[harness] setting_sources: {[] if args.setting=='none' else [args.setting]}")
    print(f"[harness] model:          {args.model}")
    print("=" * 70)

    setting_sources = [] if args.setting == "none" else [args.setting]
    opts = AgentOptions(
        model=args.model,
        api_key=os.environ["CURSOR_API_KEY"],
        local=LocalAgentOptions(cwd=tmp, setting_sources=setting_sources),
    )

    tool_calls = []
    final_text_parts = []
    try:
        with Agent.create(opts) as agent:
            print(f"[harness] agent_id: {getattr(agent, 'agent_id', '?')}")
            run = agent.send(prompt)
            print(f"[harness] run.id: {getattr(run, 'id', '?')}")
            for msg in run.messages():
                mtype = getattr(msg, "type", None)
                if mtype == "assistant":
                    for block in getattr(msg.message, "content", []) or []:
                        if getattr(block, "type", None) == "text":
                            final_text_parts.append(block.text)
                elif mtype == "tool_use" or "tool" in str(mtype or "").lower():
                    tool_calls.append(repr(msg)[:500])
            result = run.wait()
            print("=" * 70)
            print(f"[harness] STATUS: {result.status}")
            print("=" * 70)
            print("[harness] TOOL CALLS OBSERVED:")
            for tc in tool_calls:
                print("  -", tc)
            print("=" * 70)
            print("[harness] FINAL ASSISTANT TEXT:")
            print("".join(final_text_parts) or getattr(result, "result", ""))
    finally:
        if args.keep:
            print(f"[harness] kept temp workspace: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
