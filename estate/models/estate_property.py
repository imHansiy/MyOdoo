from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EstateProperty(models.Model):
    _name =  "estate.property"
    _description = "房产信息"
    _order = "id desc"

    name = fields.Char("房产名称", required=True)
    description = fields.Text("描述")
    postcode = fields.Char("邮政编码")
    date_availability = fields.Date("可入住日期",copy=False,default= lambda self: fields.Date.today() +  timedelta(days=90))
    expected_price = fields.Float("预期价格", required=True)
    selling_price = fields.Float("售价", readonly=True, copy=False)
    bedrooms = fields.Integer("卧室数", default=2)
    living_area = fields.Integer("居住面积 (平方米)")
    facades = fields.Integer("朝向")
    garage = fields.Boolean("车库")
    garden = fields.Boolean("花园")
    garden_area = fields.Integer("花园面积 (平方米)")
    garden_orientation = fields.Selection(
        string="花园朝向",
        selection=[
            ("north", "北"),
            ("south", "南"),
            ("east", "东"),
            ("west", "西"),
        ],
        help="花园朝向是指花园面向的方向",
    )
    active = fields.Boolean("有效", default=True)
    state = fields.Selection(
        selection=[
            ('new', '新订单'),
            ('offer_received', '收到报价'),
            ('offer_accepted', '接受报价'),
            ('sold', '售出'),
            ('canceled', '取消'),
        ],
        string='状态',
        required=True,
        copy=False,
        default='new',
    )
    property_type_id = fields.Many2one('estate.property.type', string='房子类型', required=True)
    buyer_id = fields.Many2one('res.partner', string='买家', required=True,copy=False)
    seller_id = fields.Many2one('res.users', string='卖家', required=True, default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='标签')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='报价')
    total_area = fields.Float(compute='_compute_total_area', string='总面积 (平方米)')
    best_price = fields.Float(compute='_compute_best_price', string='最佳价格')

    _sql_constraints = [
        # 房产预期价格必须严格为正数
        ('check_expected_price', 'CHECK(expected_price > 0)', '房产预期价格必须严格为正数'),
        # 房产售价必须为正数
        ('check_selling_price', 'CHECK(selling_price >= 0)', '房产售价必须为正数')
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < (0.9 * record.expected_price) and record.selling_price > 0:
                raise ValidationError("售价不能低于预期价格的 90%！如果您想接受此报价，请提高报价。")

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = '北'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price')) if record.offer_ids else 0.0

    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', '预期价格必须大于 0'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', '售价必须大于或等于 0'),
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < (0.9 * record.expected_price) and record.selling_price > 0:
                raise ValidationError("售价不能低于预期价格的 90%！如果您想接受此报价，请降低预期价格。")

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''
    
    def action_sold(self):
        """将房产标记为已售"""
        for record in self:
            if record.state == 'canceled':
                raise ValidationError(_("已取消的房产无法出售。"))
            record.state = 'sold'
        return True

    def action_cancel(self):
        print("在这里")
        """将房产标记为取消"""
        for record in self:
            if record.state == 'sold':
                raise ValidationError(_("已售出的房产无法取消。"))
            record.state = 'canceled'
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_check(self):
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise ValidationError(_("只有新订单和已取消的房产才能删除。"))
            
