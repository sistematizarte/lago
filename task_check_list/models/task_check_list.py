# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.depends('task_checklist')
    def checklist_progress(self):
        # total_len = self.env['task.checklist'].search_count([])}
        self.checklist_progress = 0
        total_len =  self.task_checklist
        for rec in total_len:
            if rec.status:
                self.checklist_progress = rec.peso + self.checklist_progress


    task_checklist = fields.Many2many('task.checklist', string='Check List')
    checklist_progress = fields.Float(compute=checklist_progress, string='Progress', store=True,
                                      default=0.0)
    max_rate = fields.Integer(string='Maximum rate', default=100)


class TaskChecklist(models.Model):
    _name = 'task.checklist'
    _description = 'Checklist for the task'

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')
    status = fields.Boolean(string='Status')
    peso = fields.Float(string='Peso checklist')

