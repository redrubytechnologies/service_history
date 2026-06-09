from odoo import models, fields, api,_
from odoo.exceptions import UserError


class EmployeeHistory(models.Model):
    _name = 'employee.history'
    _description = 'Employee History'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    change_date = fields.Date(string='Change Date', default=lambda self: fields.Date.today())
    changed_field = fields.Selection([
        ('designation', 'Designation'),
        ('department', 'Department'),
        ('salary', 'Salary'),
        ('wage', 'Wage'),
        ('type', 'Type')
    ], string='Changed Field')
    old_value = fields.Char(string='Old Value')
    new_value = fields.Char(string='New Value')
    as_on_date= fields.Date(string="As On")

class HRHistoryEmployee(models.Model):
    _inherit = 'hr.employee'

    history_ids = fields.One2many('employee.history', 'employee_id', string='Employee History' , order='change_date desc')

    radio_button_field = fields.Selection(
        [('In-House Employee', 'In-House Employee'), ('Client Deputed', 'Client Deputed')],
        string='Type', track_visibility='always'
    )

    def write(self, vals):
        tracked_fields = {'department_id', 'job_id', 'radio_button_field'}
        tracked_vals = {field: vals[field] for field in tracked_fields if field in vals}
        other_vals = {key: vals[key] for key in vals if key not in tracked_fields}

        if tracked_vals:
            for employee in self:
                history_vals = {
                    'employee_id': employee.id,
                    'changed_field': '',
                    'old_value': '',
                    'new_value': '',
                }
                if 'department_id' in tracked_vals:
                    old_department = employee.department_id.name if employee.department_id else ''
                    new_department = tracked_vals['department_id'] and self.env['hr.department'].browse(
                        tracked_vals['department_id']).name or ''
                    if old_department != new_department:
                        history_vals.update({
                            'changed_field': 'department',
                            'old_value': old_department,
                            'new_value': new_department,
                        })
                if 'job_id' in tracked_vals:
                    old_designation = employee.job_id.name if employee.job_id else ''
                    new_designation = tracked_vals['job_id'] and self.env['hr.job'].browse(
                        tracked_vals['job_id']).name or ''
                    if old_designation != new_designation:
                        history_vals.update({
                            'changed_field': 'designation',
                            'old_value': old_designation,
                            'new_value': new_designation,
                        })
                if 'radio_button_field' in tracked_vals:
                    old_radio_button = employee.radio_button_field or ''
                    new_radio_button = tracked_vals['radio_button_field'] or ''
                    if old_radio_button != new_radio_button:
                        history_vals.update({
                            'changed_field': 'type',
                            'old_value': old_radio_button,
                            'new_value': new_radio_button,
                        })
                if history_vals['changed_field']:
                    self.env['employee.history'].sudo().create(history_vals)

        return super(HRHistoryEmployee, self).write({**other_vals, **tracked_vals})

class HRContract(models.Model):
    _inherit = 'hr.contract'

    history_ids = fields.One2many('employee.history', 'employee_id', string='Employee History')

    @api.onchange('wage')
    def _onchange_contract_id(self):
        if self.wage:
            self.history_ids.create({
                'employee_id': self.employee_id.id,
                'changed_field': 'wage',
                'old_value': self._origin.wage if self._origin.wage else '0.0',
                'new_value': self.wage
            })



