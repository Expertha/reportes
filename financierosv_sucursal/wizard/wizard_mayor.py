import json
import datetime
import io

from odoo import fields, models, api, _
from odoo.tools.misc import xlsxwriter
from odoo.tools import config, date_utils, get_lang
from collections import defaultdict


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

	def print_mayor_xlsx(self):
		options = {
			'ids': self._ids,
			'form': self.read()[0],
			'output_format': 'xlsx',
			'model': 'wizard.sv.mayor.report',
		}
		return self.get_xlsx(options)

	def get_xlsx(self, options, response=None):
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {
			'in_memory': True,
			'strings_to_formulas': False,
		})
		sheet = workbook.add_worksheet(self._get_report_name()[:31])

		company_name_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 20, 'font_color': '#000000'})
		period_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 14, 'font_color': '#666666'})
		note_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'font_size': 12, 'font_color': '#666666'})
		date_style = workbook.add_format(
			{'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
		title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
		number_style = workbook.add_format(
			{'font_name': 'Arial', 'align': 'right', 'valign': 'bottom', 'font_size': 12, 'font_color': '#000000'})

		sheet.set_column(0, 0, 50)

		period = self._get_report_name() + ' DEL ' + options.get('form').get('fechai').strftime("%Y%m%d") + ' AL ' + \
				 options.get('form').get('fechaf').strftime("%Y%m%d")

		sheet.set_row(0, 30)
		sheet.merge_range(0, 0, 0, 5, self.env.company.name, company_name_style)
		sheet.set_row(1, 20)
		sheet.merge_range(1, 0, 1, 5, period, period_style)
		sheet.merge_range(2, 0, 2, 5, '(Valores expresados en dólares de los Estados Unidos de America)', note_style)

		workbook.close()
		output.seek(0)
		generated_file = output.read()
		output.close()

		return generated_file

	def _get_report_name(self):
		return ("Libro Mayor")
