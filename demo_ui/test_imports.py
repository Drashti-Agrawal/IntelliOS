"""Test script to verify all imports work correctly"""
import os
import sys

print("=" * 60)
print("Testing Imports for ui.py")
print("=" * 60)

# Get paths
DEMO_UI_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DEMO_UI_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
FLOW_DIR = os.path.join(BACKEND_DIR, 'flow')

print(f"\n📁 Paths:")
print(f"   DEMO_UI_DIR: {DEMO_UI_DIR}")
print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
print(f"   BACKEND_DIR: {BACKEND_DIR}")
print(f"   FLOW_DIR: {FLOW_DIR}")

print(f"\n✓ Path existence:")
print(f"   DEMO_UI_DIR exists: {os.path.exists(DEMO_UI_DIR)}")
print(f"   BACKEND_DIR exists: {os.path.exists(BACKEND_DIR)}")
print(f"   FLOW_DIR exists: {os.path.exists(FLOW_DIR)}")

# Add paths to sys.path
for path in [BACKEND_DIR, FLOW_DIR, PROJECT_ROOT]:
    if path not in sys.path and os.path.exists(path):
        sys.path.insert(0, path)
        print(f"   Added to sys.path: {path}")

print(f"\n📦 Testing imports...")

# Test local_ddna_helper
try:
    from local_ddna_helper import (
        get_local_ddna_topics,
        get_local_ddna_topic,
        get_latest_local_ddna,
        get_local_ddna_stats,
        search_local_ddna
    )
    print("   ✅ local_ddna_helper imported successfully")
except ImportError as e:
    print(f"   ❌ local_ddna_helper import failed: {e}")

# Test flow module
try:
    from flow import handle_latest_logs
    print("   ✅ flow module imported successfully")
    print(f"      handle_latest_logs: {handle_latest_logs}")
except ImportError as e:
    print(f"   ❌ flow module import failed: {e}")

# Check flow.py file
flow_file = os.path.join(FLOW_DIR, 'flow.py')
print(f"\n📄 Flow file check:")
print(f"   Path: {flow_file}")
print(f"   Exists: {os.path.exists(flow_file)}")
if os.path.exists(flow_file):
    print(f"   Size: {os.path.getsize(flow_file)} bytes")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
