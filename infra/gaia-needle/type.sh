#!/system/bin/sh
# ╔════════════════════════════════════════════════════════╗
# ║  GAIA NEEDLE — USB HID Keyboard Emulator              ║
# ║  Types text on any machine via /dev/hidg0              ║
# ╚════════════════════════════════════════════════════════╝
#
# Usage (on device, as root):
#   sh type.sh "hello world"         # type text
#   sh type.sh --line "command"      # type text + Enter
#   sh type.sh --enter               # press Enter
#   sh type.sh --tab                 # press Tab
#   sh type.sh --ctrl-alt-t          # Ctrl+Alt+T (open terminal)
#   sh type.sh --ctrl-c              # Ctrl+C
#   sh type.sh --delay 100 "text"    # type with 100ms between keys

HIDG="/dev/hidg0"
DELAY=50000  # microseconds between keystrokes (50ms default)

# Send a single HID keyboard report
send_key() {
    local mod=$1
    local key=$2
    printf "\x$(printf '%02x' $mod)\x00\x$(printf '%02x' $key)\x00\x00\x00\x00\x00" > "$HIDG"
    usleep $DELAY
    printf "\x00\x00\x00\x00\x00\x00\x00\x00" > "$HIDG"
    usleep $DELAY
}

# USB HID scan codes for printable ASCII
type_char() {
    local c="$1"
    case "$c" in
        # Lowercase letters: a=4, b=5, ..., z=29
        [a-z]) send_key 0 $(($(printf '%d' "'$c") - 93)) ;;
        # Uppercase: same codes with Left Shift (mod=2)
        [A-Z]) send_key 2 $(($(printf '%d' "'$c") - 61)) ;;
        # Numbers
        '0') send_key 0 39 ;;
        [1-9]) send_key 0 $(($(printf '%d' "'$c") - 19)) ;;
        # Symbols (no modifier)
        ' ') send_key 0 44 ;;
        '-') send_key 0 45 ;;
        '=') send_key 0 46 ;;
        '[') send_key 0 47 ;;
        ']') send_key 0 48 ;;
        '\') send_key 0 49 ;;
        ';') send_key 0 51 ;;
        "'") send_key 0 52 ;;
        '`') send_key 0 53 ;;
        ',') send_key 0 54 ;;
        '.') send_key 0 55 ;;
        '/') send_key 0 56 ;;
        # Symbols (with Shift)
        '!') send_key 2 30 ;;
        '@') send_key 2 31 ;;
        '#') send_key 2 32 ;;
        '$') send_key 2 33 ;;
        '%') send_key 2 34 ;;
        '^') send_key 2 35 ;;
        '&') send_key 2 36 ;;
        '*') send_key 2 37 ;;
        '(') send_key 2 38 ;;
        ')') send_key 2 39 ;;
        '_') send_key 2 45 ;;
        '+') send_key 2 46 ;;
        '{') send_key 2 47 ;;
        '}') send_key 2 48 ;;
        '|') send_key 2 49 ;;
        ':') send_key 2 51 ;;
        '"') send_key 2 52 ;;
        '~') send_key 2 53 ;;
        '<') send_key 2 54 ;;
        '>') send_key 2 55 ;;
        '?') send_key 2 56 ;;
        # Skip unknown characters
        *) ;;
    esac
}

type_string() {
    local str="$1"
    local i=0
    while [ $i -lt ${#str} ]; do
        type_char "${str:$i:1}"
        i=$((i + 1))
    done
}

# ─── Main ───

case "$1" in
    --enter)
        send_key 0 40  # Enter
        ;;
    --tab)
        send_key 0 43  # Tab
        ;;
    --escape|--esc)
        send_key 0 41  # Escape
        ;;
    --backspace)
        send_key 0 42  # Backspace
        ;;
    --ctrl-c)
        send_key 1 6   # Left Ctrl + C
        ;;
    --ctrl-d)
        send_key 1 7   # Left Ctrl + D
        ;;
    --ctrl-alt-t)
        send_key 5 23  # Left Ctrl + Left Alt + T (open terminal)
        ;;
    --ctrl-alt-del)
        send_key 5 76  # Left Ctrl + Left Alt + Delete
        ;;
    --super|--win)
        send_key 8 0   # Left GUI/Super/Win key
        ;;
    --line)
        shift
        [ -n "$1" ] && type_string "$*"
        send_key 0 40  # Enter
        ;;
    --delay)
        DELAY=$(($2 * 1000))  # convert ms to us
        shift 2
        type_string "$*"
        ;;
    --help|-h)
        echo "Gaia Needle — USB HID Keyboard Emulator"
        echo ""
        echo "Usage: type.sh [options] [text]"
        echo ""
        echo "Options:"
        echo "  --line TEXT    Type text then press Enter"
        echo "  --enter        Press Enter"
        echo "  --tab          Press Tab"
        echo "  --esc          Press Escape"
        echo "  --backspace    Press Backspace"
        echo "  --ctrl-c       Send Ctrl+C"
        echo "  --ctrl-d       Send Ctrl+D"
        echo "  --ctrl-alt-t   Send Ctrl+Alt+T (open terminal)"
        echo "  --super        Press Super/Win key"
        echo "  --delay MS T   Type with MS milliseconds between keys"
        echo "  --help         Show this help"
        echo ""
        echo "Examples:"
        echo "  type.sh 'hello world'"
        echo "  type.sh --line 'ls -la'"
        echo "  type.sh --ctrl-alt-t"
        echo "  type.sh --delay 100 'slow typing'"
        ;;
    *)
        [ -n "$1" ] && type_string "$*"
        ;;
esac
