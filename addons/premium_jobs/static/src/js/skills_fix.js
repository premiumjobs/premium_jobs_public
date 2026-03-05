/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SkillsListRenderer } from "@hr_skills/fields/skills_one2many/skills_one2many";

// Патч для исправления ошибки с skills report
patch(SkillsListRenderer.prototype, {
    /**
     * Переопределяем метод openSkillsReport чтобы избежать ошибки
     */
    openSkillsReport(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        
        const { resId, resModel } = this.props.list;
        
        // Проверяем что resId существует
        if (!resId) {
            console.warn("Skills report: No resId available");
            return;
        }
        
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: this.env._t("Skills Report"),
            res_model: "hr.employee.skill.report",
            views: [[false, "graph"]],
            domain: [["employee_id", "=", resId]],
            context: {
                search_default_group_by_skill_type: 1,
            },
        });
    },
});


