#!/usr/bin/env python3
"""
Comprehensive test runner for PyJavaPoet.

This script runs all test files created to match the original JavaPoet test suite.
It provides detailed reporting and can be used for continuous integration.
"""

import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import pyjavapoet
sys.path.insert(0, str(Path(__file__).parent.parent))


def discover_and_run_tests():
    """Discover and run all tests in the tests directory."""
    # Get the directory containing this script
    test_dir = Path(__file__).parent

    # Create a test loader
    loader = unittest.TestLoader()

    # Discover all tests in the current directory
    start_dir = str(test_dir)
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_individual_test_file(test_file):
    """Run a specific test file."""
    test_dir = Path(__file__).parent
    test_path = test_dir / test_file

    if not test_path.exists():
        print(f"Test file not found: {test_file}")
        return False

    # Import the test module
    module_name = test_file[:-3]  # Remove .py extension
    spec = unittest.util.spec_from_file_location(module_name, test_path)
    module = unittest.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    return result.wasSuccessful()


def list_test_files():
    """List all available test files."""
    test_dir = Path(__file__).parent
    test_files = sorted(test_dir.glob("test_*.py"))

    print("Available test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")

    return len(test_files)


def main():
    """Main entry point for the test runner."""
    if len(sys.argv) == 1:
        # Run all tests
        print("Running all PyJavaPoet tests...")
        print("=" * 50)
        success = discover_and_run_tests()

        if success:
            print("\n" + "=" * 50)
            print("🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed!")
            sys.exit(1)

    elif len(sys.argv) == 2:
        arg = sys.argv[1]

        if arg == "--list":
            # List available test files
            count = list_test_files()
            print(f"\nTotal: {count} test files")
            sys.exit(0)

        elif arg == "--help":
            # Show help
            print("PyJavaPoet Test Runner")
            print("Usage:")
            print("  python run_tests.py                 # Run all tests")
            print("  python run_tests.py --list          # List available test files")
            print("  python run_tests.py <test_file>     # Run specific test file")
            print("  python run_tests.py --help          # Show this help")
            print("\nExample:")
            print("  python run_tests.py test_type_spec.py")
            sys.exit(0)

        else:
            # Run specific test file
            test_file = arg
            if not test_file.endswith(".py"):
                test_file += ".py"

            print(f"Running test file: {test_file}")
            print("=" * 50)
            success = run_individual_test_file(test_file)

            if success:
                print(f"\n🎉 {test_file} passed!")
                sys.exit(0)
            else:
                print(f"\n❌ {test_file} failed!")
                sys.exit(1)

    else:
        print("Error: Too many arguments")
        print("Use 'python run_tests.py --help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
