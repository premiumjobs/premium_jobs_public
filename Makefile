# Premium Jobs - Odoo Management Commands
# Использование: make [команда]

.PHONY: start stop restart update update-full logs clear-cache backup status help

# Запустить Odoo
start:
	@echo "🚀 Запуск Odoo..."
	@./start_odoo.sh

# Остановить Odoo
stop:
	@echo "⏸️  Остановка Odoo..."
	@pkill -f "odoo-bin" || echo "Odoo уже остановлен"

# Перезапустить Odoo
restart: stop
	@echo "🔄 Перезапуск Odoo..."
	@sleep 2
	@./start_odoo.sh

# Обновить модуль premium_jobs
update: stop
	@echo "📦 Обновление модуля premium_jobs..."
	@sleep 2
	@./start_odoo.sh -u premium_jobs

# Обновить все модули (web, website, premium_jobs)
update-full: stop clear-cache
	@echo "📦 Полное обновление всех модулей..."
	@sleep 2
	@./start_odoo.sh -u web,website,premium_jobs

# Показать логи в реальном времени
logs:
	@echo "📋 Логи Odoo (Ctrl+C для выхода):"
	@tail -f logs/odoo.log

# Очистить кэш ассетов
clear-cache:
	@echo "🧹 Очистка кэша ассетов..."
	@psql -U premium_jobs_user -d premium_jobs_local -c "DELETE FROM ir_asset;" > /dev/null 2>&1
	@echo "✅ Кэш очищен"

# Создать бэкап БД
backup:
	@echo "💾 Создание бэкапа..."
	@mkdir -p database
	@pg_dump -U premium_jobs_user premium_jobs_local > database/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Бэкап создан: database/backup_$$(date +%Y%m%d_%H%M%S).sql"

# Показать статус
status:
	@echo "📊 Статус Odoo:"
	@pgrep -f "odoo-bin" > /dev/null && echo "✅ Odoo запущен (PID: $$(pgrep -f 'odoo-bin'))" || echo "❌ Odoo остановлен"
	@echo ""
	@echo "🗄️  PostgreSQL:"
	@brew services list | grep postgres || echo "❌ PostgreSQL не найден"
	@echo ""
	@echo "🌐 Ссылки:"
	@echo "   - Сайт: http://localhost:8069/he"
	@echo "   - CRM: http://localhost:8069/web"

# Показать помощь
help:
	@echo "🎯 Доступные команды:"
	@echo ""
	@echo "  make start        - Запустить Odoo"
	@echo "  make stop         - Остановить Odoo"
	@echo "  make restart      - Перезапустить Odoo"
	@echo "  make update       - Обновить модуль premium_jobs"
	@echo "  make update-full  - Полное обновление + очистка кэша"
	@echo "  make logs         - Показать логи в реальном времени"
	@echo "  make clear-cache  - Очистить кэш ассетов"
	@echo "  make backup       - Создать бэкап базы данных"
	@echo "  make status       - Показать статус системы"
	@echo "  make help         - Показать эту справку"
	@echo ""
	@echo "💡 Примеры:"
	@echo "  make restart      - Быстрый перезапуск"
	@echo "  make update-full  - После изменения CSS/JS"
	@echo "  make logs         - Отладка проблем"

# По умолчанию показываем help
.DEFAULT_GOAL := help

