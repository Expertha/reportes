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


class ExpandedBalanceSheet(models.Model):
	_inherit = "account.financial.html.report"

	position = fields.Integer(help="Indicates the position where it will be printed in the excel file")

	filter_analytic = False

	def print_pdf(self, options):
		if self.id == self.env.ref('b_custom_account_reports.expanded_balance_sheet_report').id:
			date_from = fields.Date.from_string(options.get('date').get('date_from'))
			date_to = fields.Date.from_string(options.get('date').get('date_to'))

			form = {
				'fechai': date_from,
				'fechaf': date_to,
				'date_year': 0000,
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
		if self.id == self.env.ref('b_custom_account_reports.expanded_balance_sheet_report').id:
			return _('Balance de Comprobación')
		else:
			return super(ExpandedBalanceSheet, self)._get_report_name()

	def print_xlsx(self, options):
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
			{'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': '#,##0.00'})
		date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})

		default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666', 'indent': 2})
		default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666'})
		title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
		level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 11, 'bottom': 6, 'font_color': '#666666'})
		number_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 11, 'bottom': 6, 'font_color': '#666666',
											  'num_format': '#,##0.00'})
		level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 11, 'bottom': 1, 'font_color': '#666666'})
		number_1_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 11, 'bottom': 1, 'font_color': '#666666',
											  'num_format': '#,##0.00'})
		level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 11, 'font_color': '#666666', 'indent': 1})
		level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 11, 'font_color': '#666666'})
		number_2_style = workbook.add_format(
			{'font_name': 'Arial', 'bold': False, 'font_size': 10, 'font_color': '#666666', 'num_format': '#,##0.00'})
		level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': False, 'font_size': 10, 'font_color': '#666666'})
		level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666', 'indent': 2})
		level_3_col1_total_style = workbook.add_format(
			{'font_name': 'Arial', 'bold': True, 'font_size': 11, 'font_color': '#666666', 'indent': 1})
		level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666'})
		number_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 11, 'font_color': '#666666', 'num_format': '#,##0.00'})
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
		sheet.set_row(0, 30)

		period = self._get_report_name() + ' DEL ' + options.get('date').get('date_from') + ' AL ' + options.get('date').get('date_to')

		if self._get_report_name() == 'Estado de Resultado Personalizado':
			sheet.merge_range(0, 0, 0, 1, self.env.company.name, company_name_style)
			sheet.set_row(1, 20)
			sheet.merge_range(1, 0, 1, 1, period, period_style)
			sheet.merge_range(2, 0, 2, 1, '(Valores expresados en dólares de los Estados Unidos de America)', note_style)
		else:
			sheet.merge_range(0, 0, 0, 4, self.env.company.name, company_name_style)
			sheet.set_row(1, 20)
			sheet.merge_range(1, 0, 1, 4, period, period_style)
			sheet.merge_range(2, 0, 2, 4, '(Valores expresados en dólares de los Estados Unidos de America)', note_style)

		y_offset = 3
		z_offset = 4
		headers, lines = self.with_context(no_format=True, print_mode=True, prefetch_fields=False)._get_table(options)

		col_one = list(filter(lambda item: item['position'] == 1, lines))
		col_two = list(filter(lambda item: item['position'] == 2, lines))

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

		for y in range(0, len(col_one)):
			level = col_one[y].get('level')
			if lines[y].get('caret_options'):
				style = level_3_style
				col1_style = level_3_col1_style
			elif level == 0:
				y_offset += 1
				style = level_0_style
				style_number = number_0_style
				col1_style = style
			elif level == 1:
				style = level_1_style
				style_number = number_1_style
				col1_style = style
			elif level == 2:
				style = level_2_style
				style_number = number_2_style
				col1_style = 'total' in col_one[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
			elif level == 3:
				style = level_3_style
				style_number = number_3_style
				col1_style = 'total' in col_one[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
			else:
				style = default_style
				style_number = default_style
				col1_style = default_col1_style

			# write the first column, with a specific style to manage the indentation
			cell_type, cell_value = self._get_cell_type_value(col_one[y])

			if cell_type == 'date':
				sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
			else:
				sheet.write(y + y_offset, 0, cell_value, col1_style)

			# write all the remaining cells
			for x in range(1, len(col_one[y]['columns']) + 1):
				cell_type, cell_value = self._get_cell_type_value(col_one[y]['columns'][x - 1])
				if cell_type == 'number':
					sheet.write_number(y + y_offset, x + col_one[y].get('colspan', 1) - 1, cell_value, style_number)
				else:
					sheet.write(y + y_offset, x + col_one[y].get('colspan', 1) - 1, cell_value, style)

		for y in range(0, len(col_two)):
			level = col_two[y].get('level')
			if col_two[y].get('caret_options'):
				style = level_3_style
				col1_style = level_3_col1_style
			elif level == 0:
				z_offset += 1
				style = level_0_style
				style_number = number_0_style
				col1_style = style
			elif level == 1:
				style = level_1_style
				style_number = number_1_style
				col1_style = style
			elif level == 2:
				style = level_2_style
				style_number = number_2_style
				col1_style = 'total' in col_two[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
			elif level == 3:
				style = level_3_style
				style_number = number_3_style
				col1_style = 'total' in col_two[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
			else:
				style = default_style
				style_number = default_style
				col1_style = default_col1_style

			# write the first column, with a specific style to manage the indentation
			cell_type, cell_value = self._get_cell_type_value(col_two[y])

			if cell_type == 'date':
				sheet.write_datetime(y + z_offset, 3, cell_value, date_default_col1_style)
			else:
				sheet.write(y + z_offset, 3, cell_value, col1_style)

			# write all the remaining cells
			for x in range(1, len(col_two[y]['columns']) + 1):
				cell_type, cell_value = self._get_cell_type_value(col_two[y]['columns'][x - 1])
				if cell_type == 'number':
					sheet.write_number(y + z_offset, x + 3 + col_two[y].get('colspan', 1) - 1, cell_value, style_number)
				else:
					sheet.write(y + z_offset, x + 3 + col_two[y].get('colspan', 1) - 1, cell_value, style)

		workbook.close()
		output.seek(0)
		generated_file = output.read()
		output.close()

		return generated_file

	def _get_cell_type_value(self, cell):
		if 'no_format_name' in cell:
			return ('number', cell.get('no_format_name', ''))
		if 'number' in cell.get('class', ''):
			return ('number', cell.get('name', ''))
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

	@api.model
	def _get_financial_line_report_line(self, options, financial_line, solver, groupby_keys):
		''' Create the report line for an account.financial.html.report.line record.
		:param options:             The report options.
		:param financial_line:      An account.financial.html.report.line record.
		:param solver_results:      An instance of the FormulaSolver class.
		:param groupby_keys:        The sorted encountered keys in the solver.
		:return:                    The dictionary corresponding to a line to be rendered.
		'''
		results = solver.get_results(financial_line)['formula']

		is_leaf = solver.is_leaf(financial_line)
		has_lines = solver.has_move_lines(financial_line)
		has_something_to_unfold = is_leaf and has_lines and bool(financial_line.groupby)

		# Compute if the line is unfoldable or not.
		is_unfoldable = has_something_to_unfold and financial_line.show_domain == 'foldable'

		# Compute the id of the report line we'll generate
		report_line_id = self._get_generic_line_id('account.financial.html.report.line', financial_line.id)

		# Compute if the line is unfolded or not.
		# /!\ Take care about the case when the line is unfolded but not unfoldable with show_domain == 'always'.
		if not has_something_to_unfold or financial_line.show_domain == 'never':
			is_unfolded = False
		elif financial_line.show_domain == 'always':
			is_unfolded = True
		elif financial_line.show_domain == 'foldable' and (report_line_id in options['unfolded_lines'] or options.get('unfold_all')):
			is_unfolded = True
		else:
			is_unfolded = False

		# Standard columns.
		columns = []
		for key in groupby_keys:
			amount = results.get(key, 0.0)
			columns.append({'name': self._format_cell_value(financial_line, amount), 'no_format': amount, 'class': 'number'})

		# Growth comparison column.
		if self._display_growth_comparison(options):
			columns.append(self._compute_growth_comparison_column(options,
																  columns[0]['no_format'],
																  columns[1]['no_format'],
																  green_on_positive=financial_line.green_on_positive
																  ))

		financial_report_line = {
			'id': report_line_id,
			'name': financial_line.name,
			'model_ref': ('account.financial.html.report.line', financial_line.id),
			'level': financial_line.level,
			'class': 'o_account_reports_totals_below_sections' if self.env.company.totals_below_sections else '',
			'columns': columns,
			'unfoldable': is_unfoldable,
			'unfolded': is_unfolded,
			'page_break': financial_line.print_on_new_page,
			'action_id': financial_line.action_id.id,
			'position': financial_line.position,
		}

		# Only run the checks in debug mode
		if self.user_has_groups('base.group_no_one'):
			# If a financial line has a control domain, a check is made to detect any potential discrepancy
			if financial_line.control_domain:
				if not financial_line._check_control_domain(options, results, self):
					# If a discrepancy is found, a check is made to see if the current line is
					# missing items or has items appearing more than once.
					has_missing = solver._has_missing_control_domain(options, financial_line)
					has_excess = solver._has_excess_control_domain(options, financial_line)
					financial_report_line['has_missing'] = has_missing
					financial_report_line['has_excess'] = has_excess
					# In either case, the line is colored in red.
					# The ids of the missing / excess report lines are stored in the options for the top yellow banner
					if has_missing:
						financial_report_line['class'] += ' alert alert-danger'
						options.setdefault('control_domain_missing_ids', [])
						options['control_domain_missing_ids'].append(financial_line.id)
					if has_excess:
						financial_report_line['class'] += ' alert alert-danger'
						options.setdefault('control_domain_excess_ids', [])
						options['control_domain_excess_ids'].append(financial_line.id)

		# Debug info columns.
		if self._display_debug_info(options):
			columns.append(self._compute_debug_info_column(options, solver, financial_line))

		# Custom caret_options for tax report.
		if self.tax_report and financial_line.domain and not financial_line.action_id:
			financial_report_line['caret_options'] = 'tax.report.line'

		return financial_report_line

	@api.model
	def _get_financial_total_section_report_line(self, options, financial_report_line):
		''' Create the total report line.
		:param options:                 The report options.
		:param financial_report_line:   The line dictionary created by the '_get_financial_line_report_line' method.
		:return:                        The dictionary corresponding to a line to be rendered.
		'''
		return {
			'id': self._get_generic_line_id('account.financial.html.report.line', None, parent_line_id=financial_report_line['id'], markup='total'),
			'name': _('Total') + ' ' + financial_report_line['name'],
			'level': financial_report_line['level'] + 1,
			'parent_id': financial_report_line['id'],
			'class': 'total',
			'columns': financial_report_line['columns'],
			'position': financial_report_line['position']
		}


class ExpandedBalanceSheetLine(models.Model):
	_inherit = "account.financial.html.report.line"

	position = fields.Integer(help="Indicates the position where it will be printed in the excel file")
