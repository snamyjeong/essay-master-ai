#!/bin/bash
# run_pytest.sh
# Set PYTHONPATH and run pytest

# Set PYTHONPATH to include the backend directory
export PYTHONPATH="/home/snamy78/essay-master-ai/backend:$PYTHONPATH"

# Run pytest with verbose output, rootdir, and redirect output to a log file
pytest --rootdir backend backend/app/tests -v > pytest_output.log 2>&1

# Print a message indicating completion
echo "Pytest execution completed. Check pytest_output.log for details."
