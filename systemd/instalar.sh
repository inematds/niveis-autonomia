#!/bin/sh
# Instala o timer diário do usuário (sem sudo). Para tirar: systemctl --user disable --now niveis-autonomia.timer
set -e
d="$HOME/.config/systemd/user"; mkdir -p "$d"
cp "$(dirname "$0")/niveis-autonomia.service" "$(dirname "$0")/niveis-autonomia.timer" "$d/"
systemctl --user daemon-reload
systemctl --user enable --now niveis-autonomia.timer
systemctl --user list-timers niveis-autonomia.timer --no-pager
