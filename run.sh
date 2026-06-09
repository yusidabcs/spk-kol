#!/bin/bash
# ============================================================
# SPK Pemilihan KOL Instagram — F&B Bali
# Script untuk menjalankan sistem di macOS/Linux
# ============================================================

set -e  # Exit on error

# Warna untuk output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=============================================="
echo -e "  SPK Pemilihan KOL Instagram — F&B Bali"
echo -e "==============================================${NC}"
echo ""

# Cek Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python tidak ditemukan!${NC}"
    echo "   Install Python 3.10+ dari https://python.org"
    exit 1
fi

# Pilih python yang tersedia
PYTHON=$(command -v python3 || command -v python)
PYTHON_VERSION=$($PYTHON --version 2>&1)
echo -e "${GREEN}✓${NC} Python ditemukan: $PYTHON_VERSION"

# Cek versi minimum (Python 3.10+)
$PYTHON -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Python kamu di bawah 3.10, mungkin error.${NC}"
    echo "   Disarankan upgrade ke Python 3.10 atau lebih baru."
    read -p "   Lanjutkan tetap? (y/n): " ans
    [ "$ans" != "y" ] && exit 1
fi

# Buat virtual environment kalau belum ada
if [ ! -d "venv" ]; then
    echo ""
    echo -e "${BLUE}→ Membuat virtual environment...${NC}"
    $PYTHON -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment dibuat di folder venv/"
fi

# Aktifkan venv
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment aktif"

# Cek apakah dependencies sudah terinstall
if ! python -c "import fastapi, uvicorn, sqlalchemy, pandas" 2>/dev/null; then
    echo ""
    echo -e "${BLUE}→ Installing dependencies (sekali saja, ~2 menit)...${NC}"
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    echo -e "${GREEN}✓${NC} Semua dependencies terinstall"
else
    echo -e "${GREEN}✓${NC} Dependencies sudah terinstall"
fi

# Jalankan server
echo ""
echo -e "${GREEN}=============================================="
echo -e "  Sistem siap! Buka browser di:"
echo -e "  ${BLUE}http://localhost:8000${GREEN}"
echo -e "  "
echo -e "  Tekan Ctrl+C untuk berhenti"
echo -e "==============================================${NC}"
echo ""

python main.py
