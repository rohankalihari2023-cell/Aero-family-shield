"""
run_tests.py
Automated test suite runner for AeroFamily.
Executes all unit, integration, and accessibility tests across the project.
"""

import sys
import os
import unittest
import time

def run_all_tests():
    # Ensure project root is in sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print("=" * 65)
    print("  🛡️  AEROFAMILY - AUTOMATED TEST SUITE")
    print("=" * 65)
    print(f"Project Directory: {project_root}")
    print(f"Python Version:    {sys.version.split()[0]}")
    print("-" * 65)

    loader = unittest.TestLoader()
    tests_dir = os.path.join(project_root, "tests")
    suite = loader.discover(start_dir=tests_dir, pattern="test_*.py")

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    duration = time.time() - start_time

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)

    print("\n" + "=" * 65)
    print(f"  Ran {total} tests in {duration:.3f}s")
    if failures == 0 and errors == 0:
        print("  ✓ ALL TESTS PASSED SUCCESSFULLY")
        print("=" * 65)
        return 0
    else:
        print(f"  ❌ FAILED (failures={failures}, errors={errors})")
        print("=" * 65)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())

if __name__ == "__main__":
    sys.exit(run_all_tests())
