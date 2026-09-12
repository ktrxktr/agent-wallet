#!/usr/bin/env python3
"""test_wallet.py — offline proof the toolkit works. No network, no keys.

  python3 test_wallet.py
"""
import base64
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_wallet import base58btc, did_of, sweep, sign_payload, load_seed
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def fresh_key():
    import secrets
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secrets.token_hex(32)))


class TestWallet(unittest.TestCase):
    def test_did_shape(self):
        did = did_of(fresh_key())
        self.assertTrue(did.startswith("did:key:z6Mk"))
        self.assertTrue(54 <= len(did) <= 60, len(did))

    def test_did_stable(self):
        k = fresh_key()
        self.assertEqual(did_of(k), did_of(k))

    def test_sign_verifies(self):
        k = fresh_key()
        p = sign_payload(k, "lobby", "hello world")
        self.assertEqual(p["did"], did_of(k))
        self.assertEqual(p["room"], "lobby")
        sig = base64.urlsafe_b64decode(p["sig"] + "==")
        k.public_key().verify(sig, f"{p['room']}|{p['nonce']}|{p['text']}".encode())

    def test_sweep(self):
        self.assertEqual(sweep("hi\x00there"), "hi there")
        with self.assertRaises(SystemExit):
            sweep("   \x00  ")
        with self.assertRaises(SystemExit):
            sweep("x" * 5000)

    def test_new_and_load(self):
        d = tempfile.mkdtemp()
        seed_hex = "ab" * 32
        with open(os.path.join(d, "identity.key"), "w") as f:
            f.write(seed_hex + "\n")
        k = load_seed(d)
        self.assertEqual(did_of(k), did_of(Ed25519PrivateKey.from_private_bytes(bytes.fromhex(seed_hex))))

    def test_new_refuses_overwrite(self):
        import subprocess
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "identity.key"), "w") as f:
            f.write("ab" * 32)
        r = subprocess.run([sys.executable, "agent_wallet.py", "new", d],
                           capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
