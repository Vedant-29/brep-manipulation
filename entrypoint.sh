#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate brep_manipulation

# Debug X11 setup
echo "=== X11 Debug Information ==="
echo "DISPLAY: $DISPLAY"
echo "XAUTHORITY: $XAUTHORITY"
echo "X11 socket exists: $(ls -la /tmp/.X11-unix/ 2>/dev/null || echo 'NOT FOUND')"

# Test X11 connection
if command -v xdpyinfo >/dev/null 2>&1; then
    if xdpyinfo -display $DISPLAY >/dev/null 2>&1; then
        echo "✓ X11 display $DISPLAY is accessible"
    else
        echo "✗ X11 display $DISPLAY is NOT accessible, continuing anyway..."
    fi
fi

echo "=== Starting BREP Manipulation Service ==="
python app.py