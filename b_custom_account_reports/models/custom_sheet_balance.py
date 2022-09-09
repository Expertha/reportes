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

import json
import datetime
import io

from odoo import fields, models, api, _
from odoo.tools.misc import xlsxwriter
from odoo.tools import config, date_utils, get_lang


class CustomSheetBalance(models.Model):
	_inherit = "account.financial.html.report"

	filter_analytic = False
	filter_accumulative = False

	@api.model
	def _get_templates(self):
		templates = super(CustomSheetBalance, self)._get_templates()
		templates['search_template'] = 'b_custom_account_reports.custom_search_sheet'

		return templates

	def print_pdf(self, options):
		if self.id == self.env.ref('b_custom_account_reports.report_balance_sheet').id:

			report_name = 'financierosv_sucursal.report_balance_pdf'
			# report = self.env['ir.actions.report']._get_report_from_name(report_name)
			date_from = fields.Date.from_string(options.get('date').get('date_from'))
			date_to = fields.Date.from_string(options.get('date').get('date_to'))

			form = {
				'fechai': date_from,
				'fechaf': date_to,
				'date_year': 2022,
				'date_month': 1,
				'acum': options.get('accumulative', False),
				'company_id': [self.env.company.id]
			}
			data = {
				'ids': [self.env.company.id],
				'form': form,
				'model': 'res_company'
			}
			return self.env.ref('financierosv_sucursal.report_general_pdf').report_action(self, data=data)
		else:
			return super(CustomSheetBalance, self).print_pdf(options=options)

	def print_xlsx(self, options):
		if self.id == self.env.ref('b_custom_account_reports.report_balance_sheet').id:
			return {
				'type': 'ir_actions_account_report_download',
				'data': {'model': self.env.context.get('model'),
						 'options': json.dumps(options),
						 'output_format': 'xlsx',
						 'financial_id': self.env.context.get('id'),
						 'allowed_company_ids': self.env.context.get('allowed_company_ids'),
						 }
			}

	def get_xlsx(self, options, response=None):
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {
			'in_memory': True,
			'strings_to_formulas': False,
		})
		sheet = workbook.add_worksheet(self._get_report_name()[:31])

		date_default_col1_style = workbook.add_format(
			{'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
		date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
		default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666', 'indent': 2})
		default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666'})
		title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
		level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 11, 'bottom': 6, 'font_color': '#666666'})
		level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 11, 'bottom': 1, 'font_color': '#666666'})
		level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 11, 'font_color': '#666666', 'indent': 1})
		level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 11, 'font_color': '#666666'})
		level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 10, 'font_color': '#666666'})
		level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666', 'indent': 2})
		level_3_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 11, 'font_color': '#666666', 'indent': 1})
		level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666'})
		company_name_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 20, 'font_color': '#000000'})
		period_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 14, 'font_color': '#666666'})
		note_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 12, 'font_color': '#666666'})
		signature_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'center', 'valign': 'bottom', 'font_size': 12, 'font_color': '#000000'})

		# Set the first column width to 50
		sheet.set_column(0, 0, 50)

		period = self._get_report_name() + ' DEL ' + options.get('date').get('date_from') + ' AL ' + options.get('date').get('date_to')

		sheet.set_row(0, 30)
		sheet.merge_range(0, 0, 0, 4, self.env.company.name, company_name_style)
		sheet.set_row(1, 20)
		sheet.merge_range(1, 0, 1, 4, period, period_style)
		sheet.merge_range(2, 0, 2, 4, '(Valores expresados en dólares de los Estados Unidos de America)', note_style)

		y_offset = 3
		headers, lines = self.with_context(no_format=True, print_mode=True, prefetch_fields=False)._get_table(options)

		# Add headers.
		for header in headers:
			x_offset = 0
			for column in header:
				column_name_formated = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
				colspan = column.get('colspan', 1)
				# if colspan == 1:
				# 	sheet.write(y_offset, x_offset, column_name_formated, title_style)
				# else:
				# 	sheet.merge_range(y_offset, x_offset, y_offset, x_offset + colspan - 1, column_name_formated, title_style)
				x_offset += colspan
			y_offset += 1

		if options.get("hierarchy"):
			lines = self._create_hierarchy(lines, options)
		if options.get('selected_column'):
			lines = self._sort_lines(lines, options)

		# Add lines.
		yy = 0
		for y in range(0, len(lines)):
			level = lines[y].get('level')
			if lines[y].get('caret_options'):
				style = level_3_style
				col1_style = level_3_col1_style
			elif level == 0:
				y_offset += 1
				style = level_0_style
				col1_style = style
			elif level == 1:
				style = level_1_style
				col1_style = style
			elif level == 2:
				style = level_2_style
				col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
			elif level == 3:
				style = level_3_style
				col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
			else:
				style = default_style
				col1_style = default_col1_style

			# write the first column, with a specific style to manage the indentation
			cell_type, cell_value = self._get_cell_type_value(lines[y])

			if y in range(0, 16):
				if cell_type == 'date':
					sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
				else:
					sheet.write(y + y_offset, 0, cell_value, col1_style)

				# write all the remaining cells
				for x in range(1, len(lines[y]['columns']) + 1):
					cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
					if cell_type == 'date':
						sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
					else:
						sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)
			else:
				yy_offset = 5
				if cell_type == 'date':
					sheet.write_datetime(yy + yy_offset, 3, cell_value, date_default_col1_style)
				else:
					sheet.write(yy + yy_offset, 3, cell_value, col1_style)

				# write all the remaining cells
				for xx in range(1, len(lines[yy]['columns']) + 1):
					cell_type, cell_value = self._get_cell_type_value(lines[yy]['columns'][xx - 1])
					if cell_type == 'date':
						sheet.write_datetime(yy + yy_offset, 4, cell_value, date_default_style)
					else:
						sheet.write_number(yy + yy_offset, 4, cell_value, style)
				yy = yy + 1

		sheet.set_row(len(lines), 30)
		sheet.merge_range(30, 0, 30, 4, 'F  __________________________                                 '
										'F  __________________________                                 '
										'F  __________________________', signature_style)

		sheet.merge_range(31, 0, 31, 4,
						  '                                  Representante Legal                                                                                                   Contador                                                                                                                        Auditor',
						  '')

		workbook.close()
		output.seek(0)
		generated_file = output.read()
		output.close()

		return generated_file

	def _get_cell_type_value(self, cell):
		if 'date' not in cell.get('class', '') or not cell.get('name'):
			# cell is not a date
			return ('text', cell.get('name', ''))
		if isinstance(cell['name'], (float, datetime.date, datetime.datetime)):
			# the date is xlsx compatible
			return ('date', cell['name'])
		try:
			# the date is parsable to a xlsx compatible date
			lg = self.env['res.lang']._lang_get(self.env.user.lang) or get_lang(self.env)
			return ('date', datetime.datetime.strptime(cell['name'], lg.date_format))
		except:
			# the date is not parsable thus is returned as text
			return ('text', cell['name'])
