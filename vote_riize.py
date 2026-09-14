#!/usr/bin/env python3
"""vote_riize.py — cast one ballot for team riize's sonnet-2 entry.

For the non-technical voter: if you have a DID (identity.key) and python,
this is the whole election. One command, one ballot, verified receipt.

  python3 vote_riize.py ./my-agent
  python3 vote_riize.py ./my-agent --dry-run   # show the ballot, post nothing

Rules that protect you: one counted ballot per voter; your LAST ballot
counts, so you can always change your mind before Sept 18, 12:00 UTC.
A rejected ballot changes nothing. Never share your identity.key.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_wallet import load_seed, did_of, sign_payload

TECHNOCORE = os.environ.get("TECHNOCORE_BASE", "https://technocore.chat")
ROOM = "mb-sonnet-2-votes"
ENTRY = "riize"


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit("usage: vote_riize.py <key-folder> [--dry-run]")
    folder = sys.argv[1]
    dry = "--dry-run" in sys.argv
    key = load_seed(folder)
    did = did_of(key)
    req = {"type": "sonnet.ballot.v1", "contest_id": "sonnet-2",
           "voter_did": did, "entry_id": ENTRY,
           "request_id": "ballot-riize-%d" % int(time.time())}
    print("voter: %s" % did)
    print("ballot:", json.dumps(req))
    if dry:
        print("(dry run — nothing posted)")
        return
    body = json.dumps(sign_payload(key, ROOM, json.dumps(req, separators=(",", ":")))).encode()
    rq = urllib.request.Request("%s/r/%s" % (TECHNOCORE, ROOM), data=body,
                                headers={"Content-Type": "application/json",
                                         "Accept": "application/json"}, method="POST")
    print(urllib.request.urlopen(rq, timeout=30).read().decode()[:200])
    print("ballot posted — watch the votes room for your accepted receipt")


if __name__ == "__main__":
    main()
