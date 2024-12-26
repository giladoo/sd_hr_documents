# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SdHrdocumentsEmployee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many('sd_hr_documents.attachments',
                                   'employee_id',
                                   string="documents")


    document_count = fields.Integer(compute='_compute_document_count',
                                    string='documents',
                                    help='Count of documents.')

    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)


    def action_document_view(self):
        self.ensure_one()
        # return {}
        return {
            'name': _('documents'),
            'domain': [('employee_id', '=', self.id)],
            'res_model': 'sd_hr_documents.attachments',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': "{'employee_id': %s}" % self.id
        }
