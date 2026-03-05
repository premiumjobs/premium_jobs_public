/** @odoo-module **/

import { registry } from "@web/core/registry";
import { patch } from '@web/core/utils/patch';

/**
 * PREMIUM JOBS - INTERFACE VISIBILITY CONTROL
 * ============================================
 * 
 * Этот файл управляет скрытием элементов интерфейса Odoo.
 * 
 * СКРЫТЫЕ ЭЛЕМЕНТЫ:
 * - "חשבון ה-Odoo שלי" (My Odoo.com account)
 * - "תיעוד" (Documentation)
 * - "תמיכה" (Support)
 * - "קיצורי דרך" (Shortcuts)
 * - Кнопки в dropdown меню формы контакта:
 *   * "שליחת הודעת SMS" (Send SMS)
 *   * "הודרה (vCard)" (Download vCard)
 *   * "Privacy Lookup"
 *   * "אפשר גישה לפורטל" (Grant Portal Access)
 * - Кнопка "התחל תוכנית" (Start Program) в форме контакта
 * - Меню "+ New" на сайте - скрыты все элементы кроме "דף" (Page):
 *   * Blog Post (блог)
 *   * Event (событие)
 *   * Forum (форум)
 *   * Job Position (вакансия)
 *   * Product (товар)
 *   * Course (курс)
 *   * Livechat Widget (чат)
 * 
 * КАК ПОКАЗАТЬ ЭЛЕМЕНТ ОБРАТНО:
 * - Закомментируй соответствующую строку `.remove("...")` или весь патч
 * - Обнови модуль: make update
 * - Очисти кэш браузера
 */

// Удаляем пункты из меню пользователя
registry.category("user_menuitems").remove("odoo_account");  // חשבון ה-Odoo שלי
registry.category("user_menuitems").remove("documentation"); // תיעוד
registry.category("user_menuitems").remove("support");       // תמיכה
registry.category("user_menuitems").remove("shortcuts");     // קיצורי דרך

// ============================================================================
// СКРЫТИЕ КНОПОК В DROPDOWN МЕНЮ ФОРМЫ КОНТАКТА
// ============================================================================
// Добавляем CSS для скрытия кнопок в dropdown меню res.partner
const style = document.createElement('style');
style.textContent = `
    /* Скрыть кнопку "שליחת הודעת SMS" (Send SMS) */
    span.dropdown-item[title*="SMS"],
    span.dropdown-item[title*="הודעת SMS"] {
        display: none !important;
    }
    
    /* Скрыть кнопку "הודרה (vCard)" (Download vCard) */
    span.dropdown-item[title*="vCard"],
    span.dropdown-item[title*="הודרה"] {
        display: none !important;
    }
    
    /* Скрыть кнопку "Privacy Lookup" */
    span.dropdown-item[title="Privacy Lookup"] {
        display: none !important;
    }
    
    /* Скрыть кнопку "אפשר גישה לפורטל" (Grant Portal Access) */
    span.dropdown-item[title*="גישה לפורטל"],
    span.dropdown-item[title*="Portal"] {
        display: none !important;
    }
    
    /* Также скрыть разделители (separator), если они остались пустыми */
    div[role="separator"].dropdown-divider:has(+ div:empty) {
        display: none !important;
    }
    
    /* Скрыть кнопку "התחל תוכנית" (Start Program) в форме контакта */
    button.btn.btn-secondary[name="231"],
    button[data-tooltip-info*="התחל תוכנית"],
    button[title*="התחל תוכנית"] {
        display: none !important;
    }
`;
document.head.appendChild(style);

// ============================================================================
// СКРЫТИЕ ЭЛЕМЕНТОВ МЕНЮ "+ NEW" НА САЙТЕ
// ============================================================================
// Патч для NewContentModal - оставляем только кнопку "דף" (Page)
// Скрываем: Blog, Event, Forum, Job Position, Product, Course, Livechat

// Используем динамический импорт чтобы не ломать frontend страницы
import('@website/systray_items/new_content').then(({ NewContentModal }) => {
    patch(NewContentModal.prototype, {
        setup() {
            super.setup();
            
            // Очищаем список элементов меню "+ New"
            // Оставляем только createNewPage() которая создаёт страницу (דף)
            this.state.newContentElements = [];
        }
    });
}).catch(() => {
    // NewContentModal недоступен на frontend страницах - это нормально
    console.log('NewContentModal not available - skipping patch');
});


