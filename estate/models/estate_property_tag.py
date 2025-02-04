from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = '房产标签'
    _order = 'name'

    name = fields.Char(string='房产标签', required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', '房产标签必须唯一')
    ]