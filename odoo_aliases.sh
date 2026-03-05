#!/bin/bash
# Premium Jobs - Shell Aliases
# Добавьте эти алиасы в ваш ~/.zshrc или ~/.bashrc

# === Odoo Management ===
alias odoo-start='cd ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT && ./start_odoo.sh'
alias odoo-stop='pkill -f "odoo-bin" && echo "✅ Odoo остановлен"'
alias odoo-restart='pkill -f "odoo-bin" && sleep 2 && cd ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT && ./start_odoo.sh'
alias odoo-update='pkill -f "odoo-bin" && sleep 2 && cd ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT && ./start_odoo.sh -u premium_jobs'
alias odoo-logs='tail -f ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT/logs/odoo.log'
alias odoo-clear='psql -U premium_jobs_user -d premium_jobs_local -c "DELETE FROM ir_asset;" && echo "✅ Кэш очищен"'
alias odoo-status='pgrep -f "odoo-bin" > /dev/null && echo "✅ Odoo запущен (PID: $(pgrep -f odoo-bin))" || echo "❌ Odoo остановлен"'

# === Quick Navigation ===
alias odoo-cd='cd ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT'
alias odoo-addons='cd ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT/addons/premium_jobs'
alias odoo-config='cursor ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT/config/odoo.conf'

# === Database ===
alias odoo-db='psql -U premium_jobs_user -d premium_jobs_local'
alias odoo-backup='cd ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT && pg_dump -U premium_jobs_user premium_jobs_local > database/backup_$(date +%Y%m%d_%H%M%S).sql && echo "✅ Бэкап создан"'

# === Web Access ===
alias odoo-web='open http://localhost:8069/web'
alias odoo-site='open http://localhost:8069/he'

echo "✅ Odoo aliases loaded!"
echo "💡 Используйте команды: odoo-start, odoo-stop, odoo-restart, odoo-update, odoo-logs"

