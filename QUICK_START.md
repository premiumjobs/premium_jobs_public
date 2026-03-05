# 🚀 Quick Start Guide - Premium Jobs

## ⚡ Быстрые команды (Make)

Перейдите в папку PROJECT и используйте:

```bash
cd PROJECT

make start        # Запустить Odoo
make stop         # Остановить Odoo
make restart      # Перезапустить
make update       # Обновить модуль premium_jobs
make update-full  # Полное обновление + очистка кэша
make logs         # Показать логи
make clear-cache  # Очистить кэш ассетов
make backup       # Создать бэкап БД
make status       # Показать статус
make help         # Показать все команды
```

---

## 🔧 Установка алиасов в Shell

Добавьте в ваш `~/.zshrc`:

```bash
# Загрузить Odoo алиасы
source ~/Documents/DEVPROJ/Premium\ Jobs/PROJECT/odoo_aliases.sh
```

Затем выполните:
```bash
source ~/.zshrc
```

### Доступные алиасы:

```bash
odoo-start       # Запустить Odoo
odoo-stop        # Остановить Odoo
odoo-restart     # Перезапустить
odoo-update      # Обновить модуль premium_jobs
odoo-logs        # Показать логи в реальном времени
odoo-clear       # Очистить кэш ассетов
odoo-status      # Показать статус
odoo-cd          # Перейти в папку PROJECT
odoo-addons      # Перейти в папку модулей
odoo-config      # Открыть конфиг в Cursor
odoo-db          # Открыть консоль PostgreSQL
odoo-backup      # Создать бэкап БД
odoo-web         # Открыть CRM в браузере
odoo-site        # Открыть сайт в браузере
```

---

## 🌐 Доступ к системе

- **Сайт:** http://localhost:8069/he
- **CRM:** http://localhost:8069/web
- **Логин:** admin
- **Пароль:** (ваш текущий пароль)

---

## 📝 Типичные сценарии

### После изменения CSS/JS:
```bash
make update-full
```

### После изменения Python кода:
```bash
make restart
```

### После изменения XML шаблонов:
```bash
make update
```

### Отладка проблем:
```bash
make logs
# или
odoo-logs
```

### Очистка кэша при проблемах со стилями:
```bash
make clear-cache
make restart
```

---

## 🗄️ База данных

**Создать бэкап:**
```bash
make backup
# или
odoo-backup
```

**Подключиться к БД:**
```bash
odoo-db
# или
psql -U premium_jobs_user -d premium_jobs_local
```

**Восстановить из бэкапа:**
```bash
psql -U premium_jobs_user -d premium_jobs_local -f database/backup_YYYYMMDD_HHMMSS.sql
```

---

## 🔍 Решение проблем

### Белый экран после логина:
```bash
make clear-cache
make update-full
```

### Стили не применяются:
```bash
make clear-cache
make restart
```

### Odoo не запускается:
```bash
# Проверить статус PostgreSQL
brew services list

# Убедиться что порт 8069 свободен
lsof -i :8069

# Остановить старые процессы
make stop
```

### Просмотр ошибок:
```bash
make logs
# или
tail -100 PROJECT/logs/odoo.log
```

---

## 📂 Структура проекта

```
PROJECT/
├── start_odoo.sh          # Скрипт запуска
├── Makefile               # Make команды
├── odoo_aliases.sh        # Shell алиасы
├── odoo_source/           # Исходники Odoo 17
├── odoo_venv/             # Python окружение
├── addons/
│   ├── premium_jobs/      # Основной модуль
│   └── web_overrides/     # Веб переопределения
├── data_dir/              # Filestore
├── config/
│   └── odoo.conf          # Конфигурация
├── database/              # Бэкапы БД
└── logs/
    └── odoo.log           # Логи

```

---

## 💡 Полезные советы

1. **Всегда делайте бэкап перед большими изменениями:**
   ```bash
   make backup
   ```

2. **Используйте `make update-full` после изменения CSS/JS**

3. **Проверяйте логи при проблемах:**
   ```bash
   make logs
   ```

4. **Очищайте кэш при странном поведении:**
   ```bash
   make clear-cache
   ```

5. **Проверяйте статус перед началом работы:**
   ```bash
   make status
   ```

---

## 🎯 Чек-лист перед работой

- [ ] PostgreSQL запущен (`brew services list`)
- [ ] Порт 8069 свободен (`lsof -i :8069`)
- [ ] Odoo остановлен (`make stop`)
- [ ] Создан бэкап (`make backup`)

---

**Все готово! Работайте с Odoo легко и быстро!** 🎉

