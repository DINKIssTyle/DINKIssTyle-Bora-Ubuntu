#!/bin/bash
# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
#
# Bora 설치 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="bora"
DESKTOP_FILE="$SCRIPT_DIR/bora.desktop"
ICON_FILE="$SCRIPT_DIR/assets/icon.png"

echo "==================================="
echo "  Bora - Screen Capture Tool"
echo "  설치 스크립트"
echo "==================================="
echo

# 의존성 확인
echo "[1/4] 의존성 확인 중..."
# 의존성 확인
echo "[1/4] 의존성 확인 중..."
MISSING_APT_DEPS=""
MISSING_PIP_DEPS=""

# APT 패키지 확인
if ! command -v python3 &> /dev/null; then MISSING_APT_DEPS="$MISSING_APT_DEPS python3"; fi
if ! command -v pip3 &> /dev/null; then MISSING_APT_DEPS="$MISSING_APT_DEPS python3-pip"; fi
if ! python3 -c "import PyQt6" 2>/dev/null; then MISSING_APT_DEPS="$MISSING_APT_DEPS python3-pyqt6"; fi
if ! python3 -c "import PIL" 2>/dev/null; then MISSING_APT_DEPS="$MISSING_APT_DEPS python3-pil"; fi
if ! python3 -c "import numpy" 2>/dev/null; then MISSING_APT_DEPS="$MISSING_APT_DEPS python3-numpy"; fi
if ! dpkg -s libxcb-cursor0 &> /dev/null; then MISSING_APT_DEPS="$MISSING_APT_DEPS libxcb-cursor0"; fi
if ! command -v gnome-screenshot &> /dev/null; then MISSING_APT_DEPS="$MISSING_APT_DEPS gnome-screenshot"; fi

# PIP 패키지 확인 (APT에 없는 패키지)
if ! python3 -c "import mss" 2>/dev/null; then MISSING_PIP_DEPS="$MISSING_PIP_DEPS mss"; fi
if ! python3 -c "import keyboard" 2>/dev/null; then MISSING_PIP_DEPS="$MISSING_PIP_DEPS keyboard"; fi

if [ -n "$MISSING_APT_DEPS" ] || [ -n "$MISSING_PIP_DEPS" ]; then
    echo "누락된 패키지:"
    if [ -n "$MISSING_APT_DEPS" ]; then echo "  [System]: $MISSING_APT_DEPS"; fi
    if [ -n "$MISSING_PIP_DEPS" ]; then echo "  [Python]: $MISSING_PIP_DEPS"; fi
    echo
    read -p "누락된 패키지를 설치하시겠습니까? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -n "$MISSING_APT_DEPS" ]; then
            echo "시스템 패키지 설치 중..."
            sudo apt update
            sudo apt install -y $MISSING_APT_DEPS
        fi
        
        if [ -n "$MISSING_PIP_DEPS" ]; then
            echo "Python 패키지 설치 중..."
            # --break-system-packages는 최신 우분투(23.04+)에서 pip install을 허용하기 위해 필요할 수 있음
            # 사용자 로컬 설치(--user)를 사용하므로 시스템 파이썬을 크게 훼손하지 않음
            pip3 install --user $MISSING_PIP_DEPS --break-system-packages || pip3 install --user $MISSING_PIP_DEPS
        fi
    else
        echo "설치가 취소되었습니다."
        exit 1
    fi
else
    echo "모든 의존성이 충족되었습니다."
fi

# 실행 권한 부여 및 입력 그룹 설정
echo
echo "[2/4] 권한 설정 중..."
chmod +x "$SCRIPT_DIR/main.py"

# input 그룹 확인 (키보드 후킹용)
if ! groups $USER | grep &>/dev/null 'input'; then
    echo "사용자 $USER 를 'input' 그룹에 추가합니다 (핫키 지원을 위해 필요)..."
    sudo usermod -aG input $USER
    echo "주의: 그룹 변경 사항을 적용하려면 로그아웃 후 다시 로그인해야 할 수 있습니다."
fi

# .desktop 파일 경로 업데이트
echo
echo "[3/4] 데스크톱 엔트리 생성 중..."

# .desktop 파일 내용 생성 (현재 경로 반영)
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Bora
Name[ko]=보라
Comment=Screen Capture Utility
Comment[ko]=화면 캡처 유틸리티
Exec=python3 $SCRIPT_DIR/main.py
Icon=$ICON_FILE
Terminal=false
Type=Application
Categories=Utility;Graphics;
Keywords=screenshot;capture;image;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

# 애플리케이션 메뉴 등록
mkdir -p ~/.local/share/applications
cp "$DESKTOP_FILE" ~/.local/share/applications/

# 자동 시작 등록
echo
echo "[4/4] 자동 시작 등록 중..."
read -p "로그인 시 자동 시작하시겠습니까? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    mkdir -p ~/.config/autostart
    cp "$DESKTOP_FILE" ~/.config/autostart/
    echo "자동 시작이 등록되었습니다."
else
    echo "자동 시작이 등록되지 않았습니다."
fi

echo
echo "==================================="
echo "  설치가 완료되었습니다!"
echo "==================================="
echo
echo "실행 방법:"
echo "  1. 터미널: python3 $SCRIPT_DIR/main.py"
echo "  2. 애플리케이션 메뉴에서 'Bora' 검색"
echo
if ! groups | grep -q 'input'; then
    echo "중요: 핫키 기능을 사용하려면 반드시 로그아웃 후 다시 로그인해주세요."
fi
echo
