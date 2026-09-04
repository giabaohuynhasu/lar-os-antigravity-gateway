#!/usr/bin/env bash
# ==============================================================================
# ⚡ Antigravity Termux / Termius / Linux One-Line Installer
# ==============================================================================

set -e

echo -e "\033[96m\033[1m⚡ Installing Antigravity Vibe Engine for Termux / Termius...\033[0m"

# 1. Determine environment
TARGET_BIN=""
if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    # Android Termux
    TARGET_BIN="$PREFIX/bin"
    echo -e "\033[92m[✓] Detected Android Termux environment: $TARGET_BIN\033[0m"
    if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
        echo "[+] Installing python in Termux..."
        pkg update -y && pkg install -y python
    fi
elif [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
    TARGET_BIN="/usr/local/bin"
else
    mkdir -p "$HOME/.local/bin"
    TARGET_BIN="$HOME/.local/bin"
    # Ensure in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        [ -f "$HOME/.zshrc" ] && echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    fi
fi

# 2. Download termux_vibe.py
mkdir -p "$HOME/.antigravity"
echo "[+] Fetching core engine..."
curl -sSL "https://raw.githubusercontent.com/giabaohuynhasu/lar-os-antigravity-gateway/main/termux_vibe.py" -o "$HOME/.antigravity/termux_vibe.py"
chmod +x "$HOME/.antigravity/termux_vibe.py"

# 3. Create wrapper scripts: a, vibe, agy
WRAPPER_SCRIPT="#!/usr/bin/env bash
if command -v python3 >/dev/null 2>&1; then
    exec python3 \"$HOME/.antigravity/termux_vibe.py\" \"\$@\"
else
    exec python \"$HOME/.antigravity/termux_vibe.py\" \"\$@\"
fi
"

for alias_name in a vibe agy; do
    echo "$WRAPPER_SCRIPT" > "$TARGET_BIN/$alias_name"
    chmod +x "$TARGET_BIN/$alias_name"
    echo -e "\033[92m[✓] Created shortcut: $TARGET_BIN/$alias_name\033[0m"
done

echo ""
echo -e "\033[96m\033[1m========================================================\033[0m"
echo -e "\033[92m\033[1m🎉 CÀI ĐẶT THÀNH CÔNG VIBE ENGINE TRÊN TERMUX / TERMINAL!\033[0m"
echo -e "\033[96m========================================================\033[0m"
echo -e "Bây giờ bạn có thể gõ ngay không cần cú pháp hay ngoặc kép:"
echo -e "  \033[93ma st\033[0m                                 (Kiểm tra trạng thái)"
echo -e "  \033[93ma viet code python kiem tra so nguyen to\033[0m (Không cần ngoặc kép!)"
echo -e "  \033[93ma claude sua loi function nay giup tui\033[0m   (Gọi Claude)"
echo -e "  \033[93mvibe tom tat asu roi gui mail cho tui\033[0m    (Tự động gửi mail)"
echo ""
