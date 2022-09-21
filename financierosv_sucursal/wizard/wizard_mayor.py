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

		bold_style_period = xlwt.XFStyle()
		font1 = xlwt.Font()
		font1.name = 'Calibri'
		font1.height = 25 * 11
		bold_style_period.font = font1
		alignment.horz = xlwt.Alignment.HORZ_CENTER
		alignment.vert = xlwt.Alignment.VERT_CENTER
		bold_style_period.alignment = alignment

		bold_style_nota = xlwt.XFStyle()
		font2 = xlwt.Font()
		font2.name = 'Calibri'
		font2.height = 20 * 11
		bold_style_nota.font = font2
		alignment.horz = xlwt.Alignment.HORZ_CENTER
		alignment.vert = xlwt.Alignment.VERT_CENTER
		bold_style_nota.alignment = alignment

		page_1 = wbk.add_sheet('Libro Mayor Diario', cell_overwrite_ok=True)
		page_1.set_horz_split_pos(1)
		page_1.panes_frozen = True
		page_1.remove_splits = True
		page_1.col(0).width = 256 * 20
		page_1.col(1).width = 256 * 40
		page_1.col(2).width = 256 * 20
		page_1.col(3).width = 256 * 20
		page_1.col(4).width = 256 * 20
		# page_1.row(0).height_mismatch = True
		page_1.row(0).height = 40 * 20
		# page_1.row(1).height_mismatch = True

		date_from = fields.Date.to_string(options.get('form').get('fechai'))
		date_to = fields.Date.to_string(options.get('form').get('fechaf'))

		period = self._get_report_name() + ' DEL ' + date_from + ' AL ' + date_to

		# sheet_name.write_merge(fila_inicial, fila_final, columna_inicial, columna_final,)
		# ws1.write_merge(0, 10, 0, 1, )

		page_1.write_merge(0, 0, 0, 4, self.env.company.name, bold_style)
		page_1.write_merge(1, 1, 0, 4, period, bold_style_period)
		page_1.write_merge(2, 2, 0, 4, '(Valores expresados en dólares de los Estados Unidos de America)', bold_style_nota)

		return page_1

	def records_page_1(self, page_1, options):
		font = xlwt.Font()
		bold_style = xlwt.XFStyle()
		font.name = 'Calibri'
		font.height = 20 * 11
		bold_style.font = font
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_LEFT
		alignment.vert = xlwt.Alignment.VERT_CENTER
		alignment.wrap = 1
		bold_style.alignment = alignment

		bold_style_num = xlwt.XFStyle()
		bold_style_num.font = font
		alignment2 = xlwt.Alignment()
		alignment2.horz = xlwt.Alignment.HORZ_RIGHT
		alignment2.vert = xlwt.Alignment.VERT_CENTER
		bold_style_num.alignment = alignment2
		bold_style_num.num_format_str = '#,##0.00'

		bold_style_total = xlwt.XFStyle()
		font2 = xlwt.Font()
		font2.name = 'Calibri'
		font2.height = 20 * 11
		font2.bold = True
		bold_style_total.font = font2
		bold_style_total.alignment = alignment2
		bold_style_total.num_format_str = '#,##0.00'

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
		alignment4.vert = xlwt.Alignment.VERT_CENTER
		bold_style_date.alignment = alignment4
		bold_style_date.num_format_str = 'DD/MM/YYYY'

		bold_style_center = xlwt.XFStyle()
		bold_style_center.font = font
		alignment5 = xlwt.Alignment()
		alignment5.horz = xlwt.Alignment.HORZ_CENTER
		alignment5.vert = xlwt.Alignment.VERT_CENTER
		bold_style_center.alignment = alignment5

		bold_style_subtotal = xlwt.XFStyle()
		bold_style_subtotal.font = font2
		alignment6 = xlwt.Alignment()
		alignment6.horz = xlwt.Alignment.HORZ_RIGHT
		alignment6.vert = xlwt.Alignment.VERT_CENTER
		bold_style_subtotal.alignment = alignment6

		bold_style_account = xlwt.XFStyle()
		bold_style_account.font = font
		bold_style_account.alignment = alignment
		borders = xlwt.Borders()
		borders.left = 4
		borders.right = 4
		borders.top = 4
		borders.bottom = 4
		bold_style_account.borders.bottom_colour = 0x3A
		bold_style_account.borders = borders

		header = xlwt.easyxf('font: bold off, color black; \
						   borders: top_color black, bottom_color black, right_color black, left_color black,\
                           left thin, right thin, top thin, bottom thin;\
                     		pattern: pattern solid, fore_color white; align: horiz centre')

		accounts = self._get_accounts(options)

		row = 4
		for account in accounts:
			name = account.get('code') + ' ' + account.get('name')

			account_type = self.env['account.account'].search([('code', 'like', '%s%%' % account.get('code'))], limit=1)

			if account_type.internal_group in ('equity', 'income', 'liability'):
				saldo_init = account.get('previo') * -1
			else:
				saldo_init = account.get('previo')

			page_1.row(row).height = 20 * 20
			page_1.write_merge(row, row, 0, 4, name, bold_style_account)
			row += 1
			page_1.write(row, 0, _('DATE'), header)
			page_1.write(row, 1, _('DESCRIPTION'), header)
			page_1.write(row, 2, _('DEBIT'), header)
			page_1.write(row, 3, _('CREDIT'), header)
			page_1.write(row, 4, _('BALANCE'), header)
			row += 1
			page_1.write(row, 0, '', bold_style)
			page_1.write(row, 1, _('Previous balance'), bold_style)
			page_1.write(row, 2, '0.00', bold_style_num)
			page_1.write(row, 3, '0.00', bold_style_num)
			page_1.write(row, 4, saldo_init, bold_style_num)
			row += 1

			options['code'] = account.get('code')
			details = self._get_account_details(options)

			i = row + 1
			flag = False
			for item in details:
				flag = True

				if account_type.internal_group in ('asset', 'expense'):
					saldo_init = saldo_init + item.get('debit') - item.get('credit')
				else:
					saldo_init = saldo_init + item.get('credit') - item.get('debit')

				formula_debe = "SUBTOTAL(9,C%d:C%d)" % (i, row + 1)
				formula_haber = "SUBTOTAL(9,D%d:D%d)" % (i, row + 1)
				page_1.write(row, 0, item.get('date'), bold_style_date)
				page_1.write(row, 1, _('MOVEMENT JOURNALS'), bold_style)
				page_1.write(row, 2, item.get('debit'), bold_style_num)
				page_1.write(row, 3, item.get('credit'), bold_style_num)
				page_1.write(row, 4, saldo_init, bold_style_num)
				row += 1

			if flag:
				subtotal_debe = formula_debe
				subtotal_haber = formula_haber
			else:
				subtotal_haber = subtotal_debe = '0.00'

			page_1.write(row, 0, '', bold_style_date)
			page_1.write(row, 1, 'Subtotal', bold_style_subtotal)
			page_1.write(row, 2, xlwt.Formula(subtotal_debe), bold_style_total)
			page_1.write(row, 3, xlwt.Formula(subtotal_haber), bold_style_total)
			page_1.write(row, 4, '', bold_style_num)
			row += 1

		total_debe = "SUBTOTAL(9,C%d:C%d)" % (7, row)
		total_haber = "SUBTOTAL(9,D%d:D%d)" % (7, row)
		row += 5
		page_1.write(row, 0, '', bold_style_date)
		page_1.write(row, 1, 'TOTALES', bold_style_subtotal)
		page_1.write(row, 2, xlwt.Formula(total_debe), bold_style_total)
		page_1.write(row, 3, xlwt.Formula(total_haber), bold_style_total)
		page_1.write(row, 4, '', bold_style_num)

	def generate_xls(self):
		options = {'ids': self._ids,
				   'form': self.read()[0],
				   'model': 'wizard.sv.mayor.report'}

		file = self._get_file_to_export(options)

		wizard_id = self.env['wizard.report.download.xls'].create(
			{
				'file_name': _('Libro Mayor diario.xls'),
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
