"""
Test runner script with various options
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_tests(args):
    """Run tests with specified options"""
    
    # Base pytest command
    cmd = ["pytest"]
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=app",
            "--cov=services",
            "--cov=scraper",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    # Filter by marker
    if args.marker:
        cmd.extend(["-m", args.marker])
    
    # Filter by test name
    if args.test:
        cmd.extend(["-k", args.test])
    
    # Run specific file
    if args.file:
        cmd.append(args.file)
    
    # Fail fast
    if args.failfast:
        cmd.append("-x")
    
    # Show output
    if args.show_output:
        cmd.append("-s")
    
    # Parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent / "backend")
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for IBM Docs LLM")
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-m", "--marker",
        help="Run tests with specific marker (unit, integration, slow)"
    )
    
    parser.add_argument(
        "-k", "--test",
        help="Run tests matching pattern"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Run specific test file"
    )
    
    parser.add_argument(
        "-x", "--failfast",
        action="store_true",
        help="Stop on first failure"
    )
    
    parser.add_argument(
        "-s", "--show-output",
        action="store_true",
        help="Show print statements"
    )
    
    parser.add_argument(
        "-n", "--parallel",
        type=int,
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    args = parser.parse_args()
    
    sys.exit(run_tests(args))


if __name__ == "__main__":
    main()

# Made with Bob
