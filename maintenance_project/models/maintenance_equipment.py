# Copyright 2019 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    project_id = fields.Many2one(comodel_name="project.project", ondelete="restrict")
    create_project_from_equipment = fields.Boolean(default=True)
    preventive_default_task_id = fields.Many2one(
        string="Default Task", comodel_name="project.task"
    )
    cost_equipo_id = fields.Float('Cost Equipo')
    cost_equipo_total = fields.Float('Cost Equipo Total', compute="_cost_equipo_total", store=True)
    hour_equip = fields.Float('Horas por Equipo')

    @api.depends('hour_equip')
    def _cost_equipo_total(self):
        for rec in self:
            if rec.hour_equip:
                rec.cost_equipo_total = rec.cost_equipo_id * rec.hour_equip
            else:
                rec.cost_equipo_total =  0

    @api.model
    def create(self, values):
        if values.get("create_project_from_equipment"):
            new_project = self.env["project.project"].create(
                self._prepare_project_from_equipment_values(values)
            )
            values["project_id"] = new_project.id
        return super().create(values)

    def _prepare_project_from_equipment_values(self, values):
        """
        Default project data creation hook
        """
        return {"name": values.get("name")}
