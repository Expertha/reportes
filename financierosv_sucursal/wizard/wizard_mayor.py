import json
import datetime
import io

from odoo import fields, models, api, _
import xlwt
from io import BytesIO
import base64


class wizard_sv_mayor_report(models.TransientModel):
	_name = 'wizard.sv.mayor.report'

	company_id = fields.Many2one('res.company', string="Company", help='Company', default=lambda self: self.env.user.company_id.id)
	date_month = fields.Selection(
		[('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
		 ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')], string='Mes de facturación', default='3', required=True)
	date_year = fields.Integer("Año de facturación", default=2022, requiered=True)
	acum = fields.Boolean(string="Acumulativo", default=False)
	fechai = fields.Date(string="Fecha Inicial", default='2022-3-1')
	fechaf = fields.Date(string="Fecha Final", default='2022-3-31')

	# stock_location_id=fields.Many2one('stock.location', string="Sucursal", help="Sucursal de la que se desea el Libro de IVA",default=lambda self: self.env.user.sucursal_id.id)

	def print_mayor_report(self):
		datas = {'ids': self._ids,
				 'form': self.read()[0],
				 'model': 'wizard.sv.mayor.report'}
		return self.env.ref('financierosv_sucursal.report_mayor_pdf').report_action(self, data=datas)

	def _get_report_name(self):
		return _("Libro Mayor Diario")

	def _get_accounts(self, options):
		"""
		Devuelve el listado de todas las cuentas.
		:param options:
		:return:
		"""
		company_id = self.env.company.id
		date_year = options.get('form').get('date_year')
		date_month = options.get('form').get('date_month')
		if options.get('form').get('acum'):
			acum = 1
		else:
			acum = 0
		fechai = options.get('form').get('fechai')
		fechaf = options.get('form').get('fechaf')

		return self.env['res.company'].get_mayor_details(company_id, date_year, date_month, acum, fechai, fechaf)

	def _get_account_details(self, options):
		company_id = self.env.company.id
		date_year = options.get('form').get('date_year')
		date_month = options.get('form').get('date_month')
		if options.get('form').get('acum'):
			acum = 1
		else:
			acum = 0
		fechai = options.get('form').get('fechai')
		fechaf = options.get('form').get('fechaf')
		cuenta = options.get('code')

		return self.env['res.company'].get_mayor_details1(company_id, date_year, date_month, acum, fechai, fechaf, cuenta)

	def _get_file_to_export(self, options):
		fl = BytesIO()
		wbk = xlwt.Workbook()

		# Page FACTURAS STORE
		page_1 = self.style_page_1(wbk, options)
		self.records_page_1(page_1, options)

		wbk.save(fl)
		fl.seek(0)
		file = base64.encodebytes(fl.read())
		fl.close()
		return file

	def style_page_1(self, wbk, options):
		font = xlwt.Font()
		bold_style = xlwt.XFStyle()
		font.name = 'Calibri'
		font.height = 30 * 11
		bold_style.font = font
		borders = xlwt.Borders()
		borders.left = 4
		borders.right = 4
		borders.top = 4
		borders.bottom = 4
		bold_style.borders = borders
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_CENTER
		alignment.vert = xlwt.Alignment.VERT_CENTER
		bold_style.alignment = alignment
		period_style = bold_style
		fontp = xlwt.Font()
		fontp.name = 'Calibri'
		fontp.height = 20 * 11
		period_style.font = fontp
		page_1 = wbk.add_sheet('Libro Mayor Diario', cell_overwrite_ok=True)
		page_1.set_horz_split_pos(1)
		page_1.panes_frozen = True
		page_1.remove_splits = True
		page_1.col(0).width = 256 * 20
		page_1.col(1).width = 256 * 40
		page_1.col(2).width = 256 * 20
		page_1.col(3).width = 256 * 20
		page_1.col(4).width = 256 * 20
		page_1.row(0).height_mismatch = True
		page_1.row(0).height = 40 * 20
		page_1.row(1).height_mismatch = True

		date_from = fields.Date.to_string(options.get('form').get('fechai'))
		date_to = fields.Date.to_string(options.get('form').get('fechaf'))

		period = self._get_report_name() + ' DEL ' + date_from + ' AL ' + date_to

		# sheet_name.write_merge(fila_inicial, fila_final, columna_inicial, columna_final,)
		# ws1.write_merge(0, 10, 0, 1, )

		page_1.write_merge(0, 0, 0, 4, self.env.company.name, bold_style)
		page_1.write_merge(1, 1, 0, 4, period, period_style)
		page_1.write_merge(2, 2, 0, 4, '(Valores expresados en dólares de los Estados Unidos de America)', bold_style)

		return page_1

	def records_page_1(self, page_1, options):
		font = xlwt.Font()
		bold_style = xlwt.XFStyle()
		font.name = 'Calibri'
		font.height = 20 * 11
		bold_style.font = font
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_LEFT
		alignment.wrap = 1
		bold_style.alignment = alignment

		bold_style_num = xlwt.XFStyle()
		bold_style_num.font = font
		alignment2 = xlwt.Alignment()
		alignment2.horz = xlwt.Alignment.HORZ_RIGHT
		bold_style_num.alignment = alignment2

		bold_style_percent = xlwt.XFStyle()
		bold_style_percent.font = font
		alignment3 = xlwt.Alignment()
		alignment3.horz = xlwt.Alignment.HORZ_RIGHT
		bold_style_percent.alignment = alignment3
		bold_style_percent.num_format_str = '#,##0.00 %'

		bold_style_date = xlwt.XFStyle()
		bold_style_date.font = font
		alignment4 = xlwt.Alignment()
		alignment4.horz = xlwt.Alignment.HORZ_CENTER
		bold_style_date.alignment = alignment4
		bold_style_date.num_format_str = 'DD/MM/YYYY'

		accounts = self._get_accounts(options)

		row = 4
		for account in accounts:
			name = account.get('code') + ' ' + account.get('name')
			page_1.write_merge(row, row, 0, 4, name, bold_style)
			row += 1
			page_1.write(row, 0, 'FECHA', bold_style)
			page_1.write(row, 1, 'DESCRIPCIÓN', bold_style)
			page_1.write(row, 2, 'DEBE', bold_style)
			page_1.write(row, 3, 'HABER', bold_style)
			page_1.write(row, 4, 'SALDO', bold_style)

			options['code'] = account.get('code')
			details = self._get_account_details(options)

			for item in details:
				page_1.write(row + 1, 0, item.get('date'), bold_style_date)
				page_1.write(row + 1, 1, 'Movimientos Diarios', bold_style)
				page_1.write(row + 1, 2, item.get('debit'), bold_style_num)
				page_1.write(row + 1, 3, item.get('credit'), bold_style_num)
				page_1.write(row + 1, 4, _('SALDO'), bold_style_num)
				row += 1

	# def records_page_3(self, page_3, partner_ids):
	# 	row = 1
	# 	for provider in provider_ids:
	# 		today = fields.Date.today()
	# 		date = format_date(self.env, fields.Date.to_string(today),
	# 						   date_format='dd/MM/YYYY')
	# 		addr = []
	# 		address = ''
	# 		if provider.street:
	# 			addr.append(provider.street)
	# 		if provider.street2:
	# 			addr.append(provider.street2)
	# 		if addr:
	# 			address = ', '.join(addr)
	# 		page_3.write(row, 1, provider.name, bold_style)
	# 		page_3.write(row, 2, '', bold_style_date)
	# 		page_3.write(row, 3, provider.vat or '', bold_style)
	# 		page_3.write(row, 4, address, bold_style)
	# 		page_3.write(row, 5, provider.city or '', bold_style)
	# 		page_3.write(row, 6, provider.state_id.name or '', bold_style)
	# 		page_3.write(row, 7, provider.country_id.name or '', bold_style)
	# 		page_3.write(row, 8, provider.zip or '', bold_style)
	# 		page_3.write(row, 9, 0.0, bold_style_percent)
	# 		page_3.write(row, 10, '', bold_style)
	# 		page_3.write(row, 11, '', bold_style_date)
	# 		row += 1

	def generate_xls(self):
		options = {'ids': self._ids,
				   'form': self.read()[0],
				   'model': 'wizard.sv.mayor.report'}

		file = self._get_file_to_export(options)

		wizard_id = self.env['wizard.report.download.xls'].create(
			{
				'file_name': _('Libro Mayor diario.xlsx'),
				'file': file
			}
		)
		return {
			'name': _('Libro Mayor diario Report'),
			'type': 'ir.actions.act_window',
			'view_id': self.env.ref(
				'financierosv_sucursal.wizard_report_download_xls').id,
			'res_id': wizard_id.id,
			'view_mode': 'form',
			'res_model': 'wizard.report.download.xls',
			'target': 'new',
		}


# def print_mayor_xlsx(self):
# 	options = {'ids': self._ids,
# 			   'form': self.read()[0],
# 			   'model': 'wizard.sv.mayor.report'}
# 	return {
# 		'type': 'ir_actions_account_report_download',
# 		'data': {'model': self.env.context.get('model'),
# 				 'options': json.dumps(options),
# 				 'output_format': 'xlsx',
#
# 				 'allowed_company_ids': self.env.context.get('allowed_company_ids'),
# 				 }
# 	}
#
# def _get_accounts(self, options):
# 	"""
# 	Devuelve el listado de todas las cuentas.
# 	:param options:
# 	:return:
# 	"""
# 	company_id = self.env.company.id
# 	date_year = options.get('form').get('date_year')
# 	date_month = options.get('form').get('date_month')
# 	acum = options.get('form').get('acum')
# 	fechai = fields.Date.from_string(options.get('date').get('fechai'))
# 	fechaf = fields.Date.from_string(options.get('date').get('fechaf'))
#
# 	return self.env['res.company'].get_mayor_details(company_id, date_year, date_month, acum, fechai, fechaf)
#
#
#
# def get_xlsx(self, options, response=None):
# 	output = io.BytesIO()
# 	workbook = xlsxwriter.Workbook(output, {
# 		'in_memory': True,
# 		'strings_to_formulas': False,
# 	})
#
# 	sheet = workbook.add_worksheet(self._get_report_name()[:31])
#
# 	date_default_style = workbook.add_format(
# 		{'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
# 	title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'valign': 'vcenter'})
# 	level_0_style = workbook.add_format(
# 		{'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
# 	level_1_style = workbook.add_format(
# 		{'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
# 	company_name_style = workbook.add_format(
# 		{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 20, 'font_color': '#000000'})
# 	period_style = workbook.add_format(
# 		{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 14, 'font_color': '#666666'})
# 	note_style = workbook.add_format(
# 		{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 12, 'font_color': '#666666'})
# 	signature_style = workbook.add_format(
# 		{'font_name': 'Arial', 'align': 'center', 'valign': 'bottom', 'font_size': 12, 'font_color': '#000000'})
#
# 	# Set the first column width to 50
# 	sheet.set_column(0, 0, 50)
# 	period = self._get_report_name() + ' DEL ' + options.get('date').get('date_from') + ' AL ' + options.get('date').get('date_to')
#
# 	sheet.set_row(0, 30)
# 	sheet.merge_range(0, 0, 0, 5, self.env.company.name, company_name_style)
# 	sheet.set_row(1, 20)
# 	sheet.merge_range(1, 0, 1, 5, period, period_style)
# 	sheet.merge_range(2, 0, 2, 5, '(Valores expresados en dólares de los Estados Unidos de America)', note_style)
#
# 	y_offset = 3
# 	accounts = self._get_accounts(options)
#
# 	for account in accounts:
# 		x_offset = 0
# 		# [{'code': '1101', 'name': 'EFECTIVO Y EQUIVALENTES', 'previo': 0.0, 'debe': 444412.01, 'haber': 437549.68},
# 		account_name = account.get('code') + ' ' + account.get('name')
# 		options['code'] = account.get('code')
#
# 		sheet.merge_range(y_offset, x_offset, y_offset, x_offset + 5, account_name, title_style)
# 		y_offset += 1
#
# 		details = self._get_account_details(options)
#
# 		headers = [
# 			{'name': 'Fecha', 'style': 'width: 25%'},
# 			{'name': 'Descripción', 'style': 'width: 10%'},
# 			{'name': 'Debe', 'class': 'number o_account_coa_column_contrast'},
# 			{'name': 'Haber', 'class': 'number o_account_coa_column_contrast'},
# 			{'name': 'Saldo', 'class': 'number o_account_coa_column_contrast'},
# 		]
#
# 		# Add headers.
# 		for header in headers:
# 			x_offset = 0
# 			for column in header:
# 				column_name_formated = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
# 				colspan = column.get('colspan', 1)
# 				if colspan == 1:
# 					sheet.write(y_offset, x_offset, column_name_formated, title_style)
# 				else:
# 					sheet.merge_range(y_offset, x_offset, y_offset, x_offset + colspan - 1, column_name_formated,
# 									  title_style)
# 				x_offset += colspan
# 			y_offset += 1
#
# 		for y in range(0, len(details)):
# 			cell_type, cell_value = self._get_cell_type_value(details[y])
# 			if cell_type == 'date':
# 				sheet.write_datetime(y + y_offset, 0, cell_value, date_default_style)
# 			else:
# 				sheet.write(y + y_offset, 0, cell_value, level_1_style)
#
# 			# write all the remaining cells
# 			for x in range(1, len(details[y]['columns']) + 1):
# 				cell_type, cell_value = self._get_cell_type_value(details[y]['columns'][x - 1])
# 				if cell_type == 'date':
# 					sheet.write_datetime(y + y_offset, x + details[y].get('colspan', 1) - 1, cell_value,
# 										 date_default_style)
# 				else:
# 					sheet.write(y + y_offset, x + details[y].get('colspan', 1) - 1, cell_value, level_1_style)
#
# 	sheet.set_row(len(details) + 10, 30)
#
# 	sheet.write(len(details) + 10, 0, 'F._________________________', signature_style)
# 	sheet.merge_range(len(details) + 10, 2, len(details) + 10, 3, 'F._________________________', signature_style)
# 	sheet.merge_range(len(details) + 10, 4, len(details) + 10, 5, 'F._________________________', signature_style)
# 	sheet.write(len(details) + 11, 0, 'Representante Legal', signature_style)
# 	sheet.merge_range(len(details) + 11, 2, len(details) + 11, 3, 'Contador', signature_style)
# 	sheet.merge_range(len(details) + 11, 4, len(details) + 11, 5, 'Auditor', signature_style)
#
# 	workbook.close()
# 	output.seek(0)
# 	generated_file = output.read()
# 	output.close()
#
# 	return generated_file
#
# def _get_cell_type_value(self, cell):
# 	if 'date' not in cell.get('class', '') or not cell.get('name'):
# 		# cell is not a date
# 		return ('text', cell.get('name', ''))
# 	if isinstance(cell['name'], (float, datetime.date, datetime.datetime)):
# 		# the date is xlsx compatible
# 		return ('date', cell['name'])
# 	try:
# 		# the date is parsable to a xlsx compatible date
# 		lg = self.env['res.lang']._lang_get(self.env.user.lang) or get_lang(self.env)
# 		return ('date', datetime.datetime.strptime(cell['name'], lg.date_format))
# 	except:
# 		# the date is not parsable thus is returned as text
# 		return ('text', cell['name'])


class WizardReportDownloadXLS(models.TransientModel):
	_name = 'wizard.report.download.xls'
	_description = 'Report Download XLS'

	file = fields.Binary(
		'File',
		help="File to export"
	)
	file_name = fields.Char(
		string="File name",
		size=64
	)
