# Premium Jobs - Локальная установка

## 🎉 Проект успешно мигрирован из Docker!

### 📍 Доступ к системе:

**🌐 Сайт (публичная часть):**
- http://localhost:8069

**🔐 CRM (административная панель):**
- http://localhost:8069/web
- http://localhost:8069/web/login

### 👤 Данные для входа:
- **Email:** admin
- **Пароль:** (ваш текущий пароль из базы данных)

---

## 🚀 Управление системой

### Запуск Odoo:
```bash
cd /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT
./start_odoo.sh
```

### Остановка Odoo:
```bash
# Нажмите Ctrl+C в терминале где запущен Odoo
# Или найдите процесс и остановите:
pkill -f "odoo-bin"
```

### Перезапуск с обновлением модуля:
```bash
cd /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT
./start_odoo.sh -u premium_jobs
```

---

## 📁 Структура проекта

```
PROJECT/
├── odoo_source/          # Исходный код Odoo 17
├── addons/               # Кастомные модули
│   ├── premium_jobs/     # Основной модуль CRM
│   └── web_overrides/    # Переопределение веб-интерфейса
├── filestore/            # Файлы и изображения
│   └── premium_jobs/     # Filestore базы данных
├── database/             # Бэкапы базы данных
│   └── premium_jobs_export.sql
├── config/               # Конфигурация
│   └── odoo.conf         # Настройки Odoo
├── logs/                 # Логи
│   └── odoo.log          # Основной лог файл
├── odoo_venv/            # Python виртуальное окружение
└── start_odoo.sh         # Скрипт запуска
```

---

## 🛠 Техническая информация

### База данных:
- **PostgreSQL:** localhost:5432
- **Database:** premium_jobs_local
- **User:** premium_jobs_user
- **Password:** premium123

### Python окружение:
- **Версия Python:** 3.13
- **Виртуальное окружение:** `/PROJECT/odoo_venv/`
- **Все зависимости установлены**

### Логи:
- **Odoo logs:** `/PROJECT/logs/odoo.log`
- **Уровень логирования:** info

---

## 📝 Полезные команды

### Создать новую базу данных:
```bash
psql postgres -c "CREATE DATABASE new_db OWNER premium_jobs_user;"
```

### Бэкап базы данных:
```bash
pg_dump -U premium_jobs_user premium_jobs_local > backup_$(date +%Y%m%d).sql
```

### Восстановление базы:
```bash
psql -U premium_jobs_user premium_jobs_local < backup.sql
```

### Просмотр логов в реальном времени:
```bash
tail -f /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT/logs/odoo.log
```

### Установка дополнительных Python пакетов:
```bash
source /Users/dimalivshitz/Documents/DEVPROJ/Premium\ Jobs/PROJECT/odoo_venv/bin/activate
pip install package_name
```

---

## ⚙️ Конфигурация (odoo.conf)

Основные настройки находятся в `/PROJECT/config/odoo.conf`:
- **Порт:** 8069
- **Addons paths:** Odoo стандартные + кастомные модули
- **Data directory:** `/PROJECT/filestore/`
- **Workers:** 0 (для разработки)

---

## 🔧 Разработка

### Редактирование кода:
Все кастомные модули находятся в:
```
/PROJECT/addons/premium_jobs/
/PROJECT/addons/web_overrides/
```

### После изменения кода:
1. Перезапустите Odoo с флагом `-u module_name`
2. Или обновите через веб-интерфейс: Apps → Update Apps List

---

## ✅ Что было перенесено:

✓ База данных (30MB)
✓ Все кастомные модули (premium_jobs, web_overrides)
✓ Filestore (все загруженные файлы)
✓ Конфигурация Odoo
✓ Python зависимости

---

## 🚨 Важно:

1. **Docker больше не нужен** - всё работает локально
2. **PostgreSQL должен быть запущен** - проверьте: `brew services list`
3. **Виртуальное окружение активируется автоматически** через start_odoo.sh
4. **Порт 8069 должен быть свободен** - закройте другие Odoo инстансы

---

## 📞 Поддержка:

Если возникли проблемы:
1. Проверьте логи: `tail -50 /PROJECT/logs/odoo.log`
2. Убедитесь что PostgreSQL запущен: `brew services list`
3. Проверьте порт: `lsof -i :8069`

---

**Система полностью готова к работе! 🎊**

