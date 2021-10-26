from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    total_initial_planned_hours = fields.Float(compute='_compute_project_information', string='Initial Planned Hours')
    total_invested_hours = fields.Float(compute='_compute_project_information', string='Invested Hours')
    total_initial_planned_hours_cost = fields.Float(compute='_compute_project_information', string='Initial Planned Hours Cost')
    total_invested_hours_cost = fields.Float(compute='_compute_project_information', string='Invested Hours Cost')
    total_equipment_cost = fields.Float(compute='_compute_project_information', string='Total Equipment Cost')
    total_material_cost = fields.Float(compute='_compute_project_information', string='Total Material Cost')
    total_consumed_material_cost = fields.Float(compute='_compute_project_information', string='Total Consumed Material Cost(actual)')
    project_progress = fields.Selection(string='Status', selection=[('new', 'New'), ('in_progress', 'In Progress'), ('done', 'Done'), ('hold', 'Hold')])
    currency_id = fields.Many2one('res.currency', compute='_compute_project_information', string='Currency')
    
    @api.depends('task_count')
    def _compute_project_information(self):
        for project in self:
            task_ids = self.env['project.task'].search([('project_id', 'in', project.ids), '|', '&', ('stage_id.is_closed', '=', False), ('stage_id.fold', '=', False), ('stage_id', '=', False)])
            total_initial_planned_hours = 0.0
            total_invested_hours = 0.0
            total_initial_planned_hours_cost = 0.0
            total_invested_hours_cost = 0.0
            total_equipment_cost = 0.0
            total_material_cost = 0.0
            total_consumed_material_cost = 0.0
            currency_id = False

            # Task calculated fields
            for task in task_ids:
                total_initial_planned_hours += task.planned_hours
                total_invested_hours += task.total_hours_spent
                # total_initial_planned_hours_cost
                if task.user_id:
                    employee_id = self.env['hr.employee'].search([('user_id', '=', task.user_id.id)])
                    if employee_id:
                        total_initial_planned_hours_cost += employee_id.timesheet_cost * task.planned_hours
                # total_consumed_material_cost/total_material_cost
                for material in task.prod_material_ids:
                    total_material_cost += material.cost_total
                    total_consumed_material_cost += material.cost_total
                # total_equipment_cost
                for equip in task.equipos_ids:
                    total_equipment_cost += equip.cost_equipo_total

            # Timesheet analytic line fields
            analytic_ids = self.env['account.analytic.line'].search([('task_id', 'in', task_ids.ids)])
            for analytic in analytic_ids:
                currency_id = analytic.employee_id.currency_id
                total_invested_hours_cost += analytic.unit_amount * analytic.employee_id.timesheet_cost
                total_initial_planned_hours_cost += 0.0


            project.total_initial_planned_hours = total_initial_planned_hours
            project.total_invested_hours = total_invested_hours
            project.total_initial_planned_hours_cost = total_initial_planned_hours_cost
            project.total_invested_hours_cost = total_invested_hours_cost
            project.total_equipment_cost = total_equipment_cost
            project.total_material_cost = total_material_cost
            project.total_consumed_material_cost = total_consumed_material_cost
            project.currency_id = currency_id
