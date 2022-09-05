from odoo import fields, models, api, _


class CustomJournalLedger(models.Model):
	_name = 'custom.journal.ledger'
	_inherit = "account.general.ledger"
	_description = "Custom General Ledger Report"

	def _get_columns_name(self, options):
		columns_names = [
			{'name': ''},
			{'name': _('Date'), 'class': 'date'},
			{'name': _('Communication')},
			{'name': _('Partner')},
			{'name': _('Debit'), 'class': 'number'},
			{'name': _('Credit'), 'class': 'number'},
			{'name': _('Balance'), 'class': 'number'}
		]
		if self.user_has_groups('base.group_multi_currency'):
			columns_names.insert(4, {'name': _('Currency'), 'class': 'number'})
		return columns_names

	def _get_lines(self, options, line_id=None):
		offset = int(options.get('lines_offset', 0))
		remaining = int(options.get('lines_remaining', 0))
		balance_progress = float(options.get('lines_progress', 0))

		if offset > 0:
			# Case a line is expanded using the load more.
			return self._load_more_lines(options, line_id, offset, remaining, balance_progress)
		else:
			# Case the whole report is loaded or a line is expanded for the first time.
			return self._get_general_ledger_lines(options, line_id=line_id)

	def _get_general_ledger_lines(self, options, line_id=None):
		''' Get lines for the whole report or for a specific line.
		:param options: The report options.
		:return:        A list of lines, each one represented by a dictionary.
		'''
		lines = []
		aml_lines = []
		options_list = self._get_options_periods_list(options)
		unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])
		date_from = fields.Date.from_string(options['date']['date_from'])
		company_currency = self.env.company.currency_id

		expanded_account = line_id and self.env['account.account'].browse(int(line_id[8:]))
		accounts_results, taxes_results = self._do_query(options_list, expanded_account=expanded_account)

		total_debit = total_credit = total_balance = 0.0
		for account, periods_results in accounts_results:
			# No comparison allowed in the General Ledger. Then, take only the first period.
			results = periods_results[0]

			is_unfolded = 'account_%s' % account.id in options['unfolded_lines']

			# account.account record line.
			account_sum = results.get('sum', {})
			account_un_earn = results.get('unaffected_earnings', {})

			# Check if there is sub-lines for the current period.
			max_date = account_sum.get('max_date')
			has_lines = max_date and max_date >= date_from or False

			amount_currency = account_sum.get('amount_currency', 0.0) + account_un_earn.get('amount_currency', 0.0)
			debit = account_sum.get('debit', 0.0) + account_un_earn.get('debit', 0.0)
			credit = account_sum.get('credit', 0.0) + account_un_earn.get('credit', 0.0)
			balance = account_sum.get('balance', 0.0) + account_un_earn.get('balance', 0.0)

			lines.append(self._get_account_title_line(options, account, amount_currency, debit, credit, balance, has_lines))

			total_debit += debit
			total_credit += credit
			total_balance += balance

			if has_lines and (unfold_all or is_unfolded):
				# Initial balance line.
				account_init_bal = results.get('initial_balance', {})

				cumulated_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)

				lines.append(self._get_initial_balance_line(
					options, account,
					account_init_bal.get('amount_currency', 0.0) + account_un_earn.get('amount_currency', 0.0),
					account_init_bal.get('debit', 0.0) + account_un_earn.get('debit', 0.0),
					account_init_bal.get('credit', 0.0) + account_un_earn.get('credit', 0.0),
					cumulated_balance,
				))

				# account.move.line record lines.
				amls = results.get('lines', [])

				load_more_remaining = len(amls)
				load_more_counter = self._context.get('print_mode') and load_more_remaining or self.MAX_LINES

				for aml in amls:
					# Don't show more line than load_more_counter.
					if load_more_counter == 0:
						break

					cumulated_balance += aml['balance']
					lines.append(self._get_aml_line(options, account, aml, company_currency.round(cumulated_balance)))

					load_more_remaining -= 1
					load_more_counter -= 1
					aml_lines.append(aml['id'])

				if load_more_remaining > 0:
					# Load more line.
					lines.append(self._get_load_more_line(
						options, account,
						self.MAX_LINES,
						load_more_remaining,
						cumulated_balance,
					))

				if self.env.company.totals_below_sections:
					# Account total line.
					lines.append(self._get_account_total_line(
						options, account,
						account_sum.get('amount_currency', 0.0),
						account_sum.get('debit', 0.0),
						account_sum.get('credit', 0.0),
						account_sum.get('balance', 0.0),
					))

		if not line_id:
			# Report total line.
			lines.append(self._get_total_line(
				options,
				total_debit,
				total_credit,
				company_currency.round(total_balance),
			))

			# Tax Declaration lines.
			journal_options = self._get_options_journals(options)
			if len(journal_options) == 1 and journal_options[0]['type'] in ('sale', 'purchase'):
				lines += self._get_tax_declaration_lines(
					options, journal_options[0]['type'], taxes_results
				)
		if self.env.context.get('aml_only'):
			return aml_lines
		return lines

	def _do_queryq(self, options, line_id, group_by_date=True, limit=False):
		select = "SELECT * "
		select += "FROM (select aa.code, aa.name, "
		select += "case when 3=1 then ( select COALESCE(sum(aml.debit),0) - COALESCE(sum(aml.credit),0) from account_move_line aml " \
				  "inner join account_move am on aml.move_id = am.id inner join account_account aac on aml.account_id = aac.id" \
				  "where am.company_id = 1 and aac.code like aa.code || '%' and " \
				  "COALESCE(am.date,am.invoice_date)<CAST('2022-06-01' as date) and am.state in ('posted')) else 0 end AS previo, "
