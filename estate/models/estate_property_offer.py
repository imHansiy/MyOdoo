from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "房产报价"
    _order = "price desc"

    price = fields.Float("报价", required=True)
    status = fields.Selection(
        selection=[
            ('accepted', '已接受'),
            ('refused', '已拒绝'),
        ],
        string='状态',
        copy=False,
    )
    partner_id = fields.Many2one('res.partner', string='合作伙伴', required=True)
    property_id = fields.Many2one('estate.property', string='房产',required=True)
    validity = fields.Integer(string='有效期', default=7)
    date_deadline = fields.Date(string='截止日期', compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True)
    property_type_id = fields.Many2one(related='property_id.property_type_id', string='房产类型', store=True)

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', '报价必须大于0'),
    ]

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity) # 或者直接留空 record.date_deadline = False

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.today()).days
            else:
                record.validity = 7
    # 树视图定义
    def action_view_tree(self):
        return {
            'name': '房产报价列表',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer',
            'view_mode': 'tree',
            'target': 'current',
        }

    # 表单视图定义
    def action_view_form(self):
        return {
            'name': '房产报价详情',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer',
            'view_mode': 'form',
            'target': 'current',
        }

        # 确认报价
    def action_accept(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.action_sold() # 修改这一行
    
    # 拒绝报价
    def action_cancel(self):
        for record in self:
            record.status = 'refused'

    @api.model_create_multi
    def create(self, vals_list):
        # 在创建选件时，将属性 state 设置为 'Offer Received'。如果用户尝试创建金额低于现有选件的选件，也会引发错误。
        for vals in vals_list:
            property_id = vals.get('property_id')
            property = self.env['estate.property'].browse(property_id)
            property.state = 'offer_received'
            price = vals.get('price')
            if price < property.best_price:
                raise ValidationError("报价金额不能低于现有选件的金额！")

        return super().create(vals)