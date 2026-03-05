# Interface Visibility Control System
# Система управления видимостью элементов интерфейса

**Автор:** Premium Jobs Development Team  
**Дата создания:** 30 октября 2025  
**Последнее обновление:** 30 октября 2025

---

## Оглавление

1. [Обзор](#обзор)
2. [Архитектура системы](#архитектура-системы)
3. [Как использовать](#как-использовать)
4. [Примеры скрытия элементов](#примеры-скрытия-элементов)
5. [Как вернуть скрытый элемент](#как-вернуть-скрытый-элемент)
6. [Технические детали](#технические-детали)
7. [Best Practices](#best-practices)

---

## Обзор

Система Interface Visibility Control позволяет **централизованно управлять видимостью элементов интерфейса Odoo CRM** из одного места.

### Зачем это нужно?

- **Упрощение интерфейса** - скрыть ненужные пункты меню, кнопки, вкладки
- **Брендирование** - убрать упоминания Odoo, логотипы, ссылки
- **Безопасность** - скрыть технические разделы от всех пользователей
- **Централизованное управление** - все настройки в одном файле

### Что можно скрыть?

✅ Пункты меню в шапке CRM  
✅ Элементы выпадающего меню профиля  
✅ Вкладки и поля в формах  
✅ Кнопки и действия  
✅ Блоки на странице  
✅ Виджеты и панели

---

## Архитектура системы

Система состоит из **двух файлов**:

```
addons/premium_jobs/
├── data/
│   └── interface_visibility.xml      # Конфигурация (XML)
└── static/src/js/
    └── hide_interface_elements.js    # Логика скрытия (JavaScript)
```

### Файл 1: `interface_visibility.xml`

**Назначение:** Документация и конфигурация элементов, скрываемых через XML.

**Расположение:** `addons/premium_jobs/data/interface_visibility.xml`

**Что здесь:**
- Комментарии о том, что скрыто
- XML-записи для скрытия меню, действий, представлений
- Примеры использования

### Файл 2: `hide_interface_elements.js`

**Назначение:** JavaScript код для скрытия элементов интерфейса, которые нельзя скрыть через XML.

**Расположение:** `addons/premium_jobs/static/src/js/hide_interface_elements.js`

**Что здесь:**
- Удаление пунктов из меню пользователя
- Удаление виджетов из dashboard
- Манипуляции с DOM после загрузки страницы

---

## Как использовать

### Шаг 1: Определить что нужно скрыть

1. Открой CRM и найди элемент, который нужно скрыть
2. Определи тип элемента:
   - **Пункт меню** → ищи `ir.ui.menu`
   - **Элемент профиля** → ищи в `user_menuitems` registry
   - **Вкладка/поле** → ищи в XML представлении модели
   - **Кнопка** → ищи в XML представлении или действии

### Шаг 2: Выбрать метод скрытия

#### Метод A: JavaScript (для динамических элементов)

**Используй для:**
- Элементов меню профиля (Documentation, Support, My Odoo Account)
- Dashboard виджетов
- Элементов, добавляемых динамически через JS

**Как:**

1. Открой `addons/premium_jobs/static/src/js/hide_interface_elements.js`
2. Добавь строку:
```javascript
registry.category("user_menuitems").remove("element_id");
```

#### Метод B: XML (для статических элементов)

**Используй для:**
- Пунктов меню в шапке CRM
- Полей и вкладок в формах
- Действий (Actions)

**Как:**

1. Открой `addons/premium_jobs/data/interface_visibility.xml`
2. Добавь XML запись (см. примеры ниже)

### Шаг 3: Применить изменения

```bash
cd PRODUCTION
make update    # или: make restart
```

### Шаг 4: Проверить

1. Открой CRM
2. Очисти кэш браузера (Cmd+Shift+R / Ctrl+Shift+R)
3. Проверь что элемент скрыт

---

## Примеры скрытия элементов

### Пример 1: Скрыть элемент меню профиля (JS)

**Задача:** Скрыть "חשבון ה-Odoo שלי" (My Odoo.com account)

**Файл:** `hide_interface_elements.js`

```javascript
// Удаляем пункт "חשבון ה-Odoo שלי" из меню пользователя
registry.category("user_menuitems").remove("odoo_account");
```

**Другие доступные элементы:**
```javascript
// Скрыть документацию
registry.category("user_menuitems").remove("documentation");

// Скрыть поддержку
registry.category("user_menuitems").remove("support");

// Скрыть горячие клавиши
registry.category("user_menuitems").remove("shortcuts");
```

---

### Пример 2: Скрыть пункт меню в шапке (XML)

**Задача:** Скрыть меню "Settings" (Настройки)

**Файл:** `interface_visibility.xml`

```xml
<data noupdate="0">
    <!-- Скрыть меню "Settings" -->
    <record id="base.menu_administration" model="ir.ui.menu">
        <field name="active" eval="False"/>
    </record>
</data>
```

---

### Пример 3: Скрыть вкладку в форме (XML)

**Задача:** Скрыть вкладку "Internal Notes" в форме контакта

**Файл:** `interface_visibility.xml`

```xml
<record id="view_partner_form_hide_internal_notes" model="ir.ui.view">
    <field name="name">res.partner.form.hide.notes</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//page[@name='internal_notes']" position="attributes">
            <attribute name="invisible">1</attribute>
        </xpath>
    </field>
</record>
```

---

### Пример 4: Скрыть поле в форме (XML)

**Задача:** Скрыть поле "Email" в форме контакта

```xml
<record id="view_partner_form_hide_email" model="ir.ui.view">
    <field name="name">res.partner.form.hide.email</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='email']" position="attributes">
            <attribute name="invisible">1</attribute>
        </xpath>
    </field>
</record>
```

---

### Пример 5: Скрыть кнопку (XML)

**Задача:** Скрыть кнопку "Archive" в форме задачи

```xml
<record id="view_task_form_hide_archive" model="ir.ui.view">
    <field name="name">project.task.form.hide.archive</field>
    <field name="model">project.task</field>
    <field name="inherit_id" ref="project.view_task_form2"/>
    <field name="arch" type="xml">
        <xpath expr="//button[@name='toggle_active']" position="attributes">
            <attribute name="invisible">1</attribute>
        </xpath>
    </field>
</record>
```

---

## Как вернуть скрытый элемент

### Вернуть элемент, скрытый через JavaScript

1. Открой `hide_interface_elements.js`
2. Найди строку `registry.category(...).remove("element_id");`
3. Закомментируй её:
```javascript
// registry.category("user_menuitems").remove("odoo_account");
```
4. Обнови модуль: `make update`
5. Очисти кэш браузера (Cmd+Shift+R)

### Вернуть элемент, скрытый через XML

#### Вариант 1: Закомментировать запись

```xml
<!--
<record id="hide_my_menu" model="ir.ui.menu">
    <field name="active" eval="False"/>
</record>
-->
```

#### Вариант 2: Включить обратно

```xml
<record id="hide_my_menu" model="ir.ui.menu">
    <field name="active" eval="True"/>  <!-- Было: False -->
</record>
```

#### Вариант 3: Удалить запись из XML

Просто удали весь блок `<record>...</record>`.

**После любого изменения:**
```bash
make update
```

---

## Технические детали

### Порядок загрузки

1. **XML файлы** загружаются при установке/обновлении модуля
2. **JavaScript файлы** загружаются при загрузке страницы CRM

### Registry Categories в Odoo

Odoo использует registry для динамических элементов:

```javascript
// Меню пользователя
registry.category("user_menuitems")

// Системные сервисы
registry.category("services")

// Действия
registry.category("actions")

// Виджеты
registry.category("fields")
```

### Как найти ID элемента

#### Для меню:

```sql
SELECT id, name, external_id 
FROM ir_ui_menu m
LEFT JOIN ir_model_data imd ON imd.res_id = m.id AND imd.model = 'ir.ui.menu'
WHERE name->>'en_US' LIKE '%Settings%';
```

#### Для элементов профиля:

Открой DevTools → Console:
```javascript
odoo.__DEBUG__.services["@web/core/registry"].category("user_menuitems").getAll()
```

#### Для полей в форме:

Открой форму → Включи Debug Mode → View Metadata → смотри XML

---

## Best Practices

### ✅ DO (Делай так)

1. **Документируй изменения** - добавляй комментарии в XML и JS
2. **Используй осмысленные ID** - `hide_odoo_account`, а не `temp_123`
3. **Группируй похожие элементы** - все скрытые меню в одном месте
4. **Тестируй на всех ролях** - проверь для админа, менеджера, портального юзера
5. **Делай backup** - перед большими изменениями

### ❌ DON'T (Не делай так)

1. **Не удаляй элементы из odoo_source напрямую** - используй override
2. **Не скрывай критические элементы** - "Log out", "Save", "Cancel"
3. **Не забывай `noupdate="0"`** - иначе изменения не применятся
4. **Не дублируй логику** - если элемент уже скрыт в JS, не скрывай в XML
5. **Не скрывай без необходимости** - каждый скрытый элемент = overhead

### Чек-лист перед коммитом

- [ ] Добавлен комментарий в XML/JS
- [ ] Обновлена эта документация (если добавлен новый тип скрытия)
- [ ] Протестировано для админа и обычного пользователя
- [ ] Проверено что элемент действительно скрыт
- [ ] Проверено что скрытие не ломает функциональность

---

## FAQ

### Q: Как скрыть элемент только для определенной группы пользователей?

A: Используй атрибут `groups` в XML:

```xml
<record id="base.menu_administration" model="ir.ui.menu">
    <field name="groups_id" eval="[(6, 0, [ref('base.group_system')])]"/>
</record>
```

### Q: Почему элемент не скрывается?

**Чек-лист:**
1. Обновил модуль? `make update`
2. Очистил кэш браузера? (Cmd+Shift+R)
3. Правильный ID элемента?
4. Правильный синтаксис в XML/JS?
5. Нет ошибок в логах Odoo?

### Q: Можно ли скрыть элемент временно (на время)?

A: Да! Просто закомментируй запись в XML или строку в JS, а потом раскомментируй обратно.

### Q: Как узнать что скрыто в данный момент?

A: Открой файлы:
- `data/interface_visibility.xml` - список скрытых элементов в XML
- `static/src/js/hide_interface_elements.js` - список скрытых элементов в JS

---

## История изменений

| Дата | Автор | Изменение |
|------|-------|-----------|
| 30.10.2025 | Premium Jobs Dev | Создана система Interface Visibility Control |
| 30.10.2025 | Premium Jobs Dev | Скрыт пункт "חשבון ה-Odoo שלי" (My Odoo.com account) |
| 09.11.2025 | Premium Jobs Dev | Скрыты все элементы меню "+ New" кроме "דף" (Page) через патч NewContentModal |

---

## Контакты

**При возникновении вопросов:**
- Читай другую документацию в `Project Documentation/`
- Смотри код в `addons/premium_jobs/`
- Проверяй логи: `logs/odoo.log`

**Полезные файлы:**
- `Odoo_Development_Best_Practices.md` - Best practices для разработки
- `Odoo_Templates_Best_Practices.md` - Работа с XML шаблонами
- `Database Schema.md` - Структура базы данных

---

**Конец документации** 🎉

