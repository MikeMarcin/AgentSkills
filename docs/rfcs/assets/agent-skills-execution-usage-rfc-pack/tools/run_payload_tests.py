#!/usr/bin/env python3
"""Run only disposable offline payload fixtures. No providers or live MASK calls."""
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'payload/skills/implement-rfc/scripts'))
suite=unittest.defaultTestLoader.discover(str(root/'payload/skills/implement-rfc/tests'),pattern='test_usage*_seed.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
