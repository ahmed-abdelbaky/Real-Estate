from odoo import models, fields, api
# from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare


class estateProperty(models.Model):
    _name = 'estate.property'
    _description = 'estate property'
    _order = "id desc"
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date('Available From',
                                    default=lambda self: fields.Datetime.now() + relativedelta(months=+3), copy=False)
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default='2')
    living_area = fields.Integer('Living Area')
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ], string="Garden Orientation"
    )
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold_and_cancel', 'Sold and Cancel')
        ],
        default='new', required=True, copy=False, string='Status'
    )
    type_id = fields.Many2one('estate.property.type', string='Property Type')
    sales_person = fields.Char('Sales Person', default=lambda self: self.env.user.name, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Buyer')
    tag_ids = fields.Many2many('estate.property.tag', string='Tag')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    total_area = fields.Integer("Total Area", compute="_compute_total_area")
    best_price = fields.Integer("Best Price", compute="_compute_best_price")
    user_id = fields.Many2one("res.users")

    @api.depends("living_area", 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for rec in self:
            if rec.offer_ids:
                value = rec.offer_ids.mapped('price')
                # print("offer_ids ", rec.offer_ids)
                # print("offer_ids ", rec.mapped('partner_id'), rec.partner_id)
                # print("value ", value)
                rec.best_price = max(value)
            else:
                rec.best_price = 0
        # print("partner_id ", self.mapped('partner_id'))

    @api.onchange('garden')
    def on_change(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_orientation = ''
            self.garden_area = ''

    def button_sold(self):
        for record in self:

            if record.state == ' sold_and_cancel':
                raise UserError('a sold property cannot be canceled.')
            else:
                record.state = 'sold_and_cancel'

    def button_cancel(self):
        for record in self:
            record.state = 'new'
            # raise UserError('A canceled property cannot be set as sold.')

    _sql_constraints = [
        ('check_positive_expected_price', 'CHECK(expected_price > 0 )', 'Expected Price must be Positive'),
        ('check_positive_selling_price', 'CHECK(selling_price > 0 )', 'Selling Price must be positive')

    ]

    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price:
                amount = 90 * record.expected_price / 100
                if float_compare(record.selling_price, amount, 2) < 0:
                    raise UserError('selling price cannot be lower than 90% of the expected price.')

    def unlink(self):
        for record in self:
            if record.state not in ['new', 'sold_and_cancel']:
                raise UserError('You Cant delete this property')

        super().unlink()
