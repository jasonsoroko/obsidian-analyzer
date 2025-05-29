#!/usr/bin/env python3
"""
Health check script for Obsidian Analyzer system.
Runs tests and generates health report.
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_command(cmd, description):
    """Run a command and return result."""
    print(f"🔍 {description}...")
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        duration = time.time() - start_time
        print(f"✅ {description} - OK ({duration:.2f}s)")
        return True, duration, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"   Error: {e.stderr}")
        return False, 0, e.stderr


def check_dependencies():
    """Check if all required dependencies are available."""
    deps = ["pytest", "psutil"]
    missing = []
    
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: uv add " + " ".join(missing))
        return False
    
    return True


def run_health_check():
    """Run comprehensive health check."""
    print("🏥 Obsidian Analyzer Health Check")
    print("=" * 40)
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "UNKNOWN",
        "checks": {}
    }
    
    # Check dependencies
    if not check_dependencies():
        health_report["overall_status"] = "FAILED"
        health_report["checks"]["dependencies"] = {"status": "FAILED", "message": "Missing dependencies"}
        return health_report
    
    checks = [
        ("pytest tests/unit -v", "Unit Tests"),
        ("pytest tests/integration -v", "Integration Tests"),
        ("pytest tests/integration/test_performance.py -v", "Performance Tests"),
        ("python -c 'from obsidian_analyzer import CodingFolderAnalyzer; print(\"Import OK\")'", "Module Import"),
        ("python scripts/analyze_vault.py test_vault --output /tmp/test_report.md", "CLI Functionality"),
    ]
    
    passed = 0
    total = len(checks)
    
    for cmd, description in checks:
        success, duration, output = run_command(cmd, description)
        
        health_report["checks"][description.lower().replace(" ", "_")] = {
            "status": "PASSED" if success else "FAILED",
            "duration": duration,
            "command": cmd
        }
        
        if success:
            passed += 1
    
    # Overall status
    if passed == total:
        health_report["overall_status"] = "HEALTHY"
        print(f"\n🎉 System Health: HEALTHY ({passed}/{total} checks passed)")
    elif passed >= total * 0.7:
        health_report["overall_status"] = "WARNING"
        print(f"\n⚠️  System Health: WARNING ({passed}/{total} checks passed)")
    else:
        health_report["overall_status"] = "CRITICAL"
        print(f"\n🚨 System Health: CRITICAL ({passed}/{total} checks passed)")
    
    # Save health report
    report_path = Path("tests/reports/health_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(health_report, f, indent=2)
    
    print(f"📄 Health report saved to: {report_path}")
    
    return health_report


def main():
    """Main health check function."""
    try:
        report = run_health_check()
        
        # Exit with appropriate code
        if report["overall_status"] == "HEALTHY":
            sys.exit(0)
        elif report["overall_status"] == "WARNING":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⏹️  Health check cancelled")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
