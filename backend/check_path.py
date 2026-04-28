
import sys
import os

print("sys.path before modification:")
for p in sys.path:
    print(p)

# Ensure the parent directory of 'backend' is in sys.path
# This makes 'backend' a top-level package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir) # Add the project root to sys.path

print("\nsys.path after modification (if any):")
for p in sys.path:
    print(p)

try:
    from backend.app.tasks import example_task
    print("\nSuccessfully imported backend.app.tasks.example_task")
except ModuleNotFoundError as e:
    print(f"\nModuleNotFoundError: {e}")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
