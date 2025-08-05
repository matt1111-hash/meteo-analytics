#!/bin/bash
# Global Weather Analyzer - Linux Environment Setup
# Automatically configures PySide6 library paths and development environment

set -e  # Exit on any error

echo "🌍 Global Weather Analyzer - Environment Setup"
echo "=============================================="

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Error: No virtual environment detected."
    echo "   Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"

# Configure PySide6 library path for Linux
PYSIDE6_LIB_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/PySide6/Qt/lib"

if [[ -d "$PYSIDE6_LIB_PATH" ]]; then
    export LD_LIBRARY_PATH="$PYSIDE6_LIB_PATH:$LD_LIBRARY_PATH"
    echo "✅ PySide6 library path configured: $PYSIDE6_LIB_PATH"
else
    echo "⚠️  Warning: PySide6 not found. Installing dependencies..."
    pip install -r requirements-base.txt
    
    # Recheck after installation
    if [[ -d "$PYSIDE6_LIB_PATH" ]]; then
        export LD_LIBRARY_PATH="$PYSIDE6_LIB_PATH:$LD_LIBRARY_PATH"
        echo "✅ PySide6 library path configured after installation"
    else
        echo "❌ Error: PySide6 installation failed or path incorrect"
        exit 1
    fi
fi

# Test PySide6 functionality
echo "🧪 Testing PySide6 installation..."
python -c "
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import __version__
print(f'✅ PySide6 working! Version: {__version__}')
app = QApplication([])
print('✅ QApplication created successfully')
" || {
    echo "❌ Error: PySide6 test failed"
    exit 1
}

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/cache data/climate_cache exports logs utils

echo "🎉 Environment setup complete!"
echo ""
echo "To run the application:"
echo "  python meteo_gui_starter.py"
echo ""
echo "For development:"
echo "  pip install -r requirements-dev.txt"
echo "  python -m pytest tests/"
echo ""
echo "Note: Add this to your ~/.bashrc for permanent PySide6 support:"
echo "export LD_LIBRARY_PATH=\"\$VIRTUAL_ENV/lib/python3.12/site-packages/PySide6/Qt/lib:\$LD_LIBRARY_PATH\""
