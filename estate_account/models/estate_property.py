from odoo import models,Command

class EstateProperty(models.Model):
    _inherit = 'estate.property'


    def action_sold(self):
        vals = {
            "partner_id": self.buyer_id.id,
            "move_type": "out_invoice",
            "line_ids": [
                Command.create({
                    "name": "营业税",
                    "quantity": 1,
                    "price_unit": self.selling_price * 0.06,
                }),
                Command.create({
                    "name": "杂项",
                    "quantity": 1,
                    "price_unit": 100,
                }),
            ],
        }
        self.env['account.move'].create(vals)
        return super().action_sold()
