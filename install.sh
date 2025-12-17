#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Installing DINKIssTyle-Bora...${NC}"

# 1. Dependency Check
echo "Checking system dependencies..."
sudo apt update
sudo apt install -y libxcb-cursor0 gnome-screenshot

# 2. Permission Check (CRITICAL)
echo "Configuring permissions..."
if ! groups $USER | grep &>/dev/null 'input'; then
    echo "Adding user $USER to 'input' group for hotkey support..."
    sudo usermod -aG input $USER
    echo "NOTE: You may need to logout and login again for group changes to take effect."
fi

# 3. Install Binary
echo "Installing binary..."
mkdir -p ~/.local/bin
if [ -f "dist/DINKIssTyle-Bora" ]; then
    cp dist/DINKIssTyle-Bora ~/.local/bin/
else
    echo "Error: Binary not found in dist/. Please run ./build.sh first."
    exit 1
fi

# 4. Install Desktop Entry
echo "Installing desktop shortcut..."
mkdir -p ~/.local/share/applications/
# Replace placeholder with actual home directory
sed "s|USER_PLACEHOLDER|$USER|g" assets/DINKIssTyle-Bora.desktop > ~/.local/share/applications/DINKIssTyle-Bora.desktop

# 5. Refresh
update-desktop-database ~/.local/share/applications/

echo -e "${GREEN}Installation Complete!${NC}"
echo "You can now launch 'DINKIssTyle Bora' from your application menu."
if ! groups | grep -q 'input'; then
    echo "IMPORTANT: Please LOGOUT and LOGIN again to enable hotkey support."
fi
