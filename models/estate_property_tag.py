from odoo import models, fields, api


class estatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _order = "name"

    name = fields.Char("Name", required=True)
    color = fields.Integer('Color')
    _sql_constraints = [
        ('check_unique_tag_name', 'unique(name)', 'Name of Tag already found')
    ]