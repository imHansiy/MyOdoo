from odoo import models, fields,api

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = '房地产物业类型'
    _order = "sequence"

    name = fields.Char(string='物业类型', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='房产')
    sequence = fields.Integer(string='排序', default=1)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='报价')
    offer_count = fields.Integer(string='报价数量', compute='_compute_offer_count')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "房产类型名称必须唯一！")
    ]

    # 计算报价数量
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)