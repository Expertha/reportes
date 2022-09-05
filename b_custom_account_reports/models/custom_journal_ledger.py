from odoo import fields, models, api, _


class CustomJournalLedger(models.Model):
	_name = 'custom.journal.ledger'
	_inherit = "account.general.ledger"
	_description = "Custom General Ledger Report"

	def _get_columns_name(self, options):
		columns_names = [
			{'name': ''},
			{'name': _('Date'), 'class': 'date'},
			{'name': _('Description')},
			{'name': _('Debit'), 'class': 'number'},
			{'name': _('Credit'), 'class': 'number'},
			{'name': _('Balance'), 'class': 'number'}
		]
		# if self.user_has_groups('base.group_multi_currency'):
		# 	columns_names.insert(4, {'name': _('Currency'), 'class': 'number'})
		return columns_names
