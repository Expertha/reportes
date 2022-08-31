# -*- encoding: utf-8 -*-
#
# Module written to Odoo, Open Source Management Solution
#
# Copyright (c) 2022 Birtum - http://www.birtum.com
# All Rights Reserved.
#
# Developer(s): Carlos Maykel López González
#               (clg@birtum.com)
#
########################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

from odoo import fields, models, api, _


class ExpandedBalanceSheet(models.Model):
	_inherit = "account.financial.html.report"

	filter_analytic = False

	def print_pdf(self, options):
		if self.id == self.env.ref('b_custom_account_reports.ending_trial_balance_report').id:

			report_name = 'financierosv_sucursal.report_balance_pdf'
			# report = self.env['ir.actions.report']._get_report_from_name(report_name)
			date_from = fields.Date.from_string(options.get('date').get('date_from'))
			date_to = fields.Date.from_string(options.get('date').get('date_to'))

			form = {
				'fechai': date_from,
				'fechaf': date_to,
				'date_year': 1900,
				'date_month': 1,
				'acum': options.get('accumulative', True),
				'company_id': [self.env.company.id]
			}
			data = {
				'ids': [self.env.company.id],
				'form': form,
				'model': 'res_company'
			}
			return self.env.ref('financierosv_sucursal.report_general_pdf').report_action(self, data=data)
		else:
			return super(ExpandedBalanceSheet, self).print_pdf(options=options)

	def _get_report_name(self):
		return _('Balance Trial New Report')
