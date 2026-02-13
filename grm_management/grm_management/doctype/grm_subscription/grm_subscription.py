# Copyright (c) 2026, Wael ELsafty and contributors
import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff, add_months, getdate, nowdate

class GRMSubscription(Document):
	def validate(self):
		self.validate_dates()
		self.set_payment_frequency()
		self.calculate_total_from_spaces()
		self.apply_taxes()
		self.calculate_grand_total()
		self.update_remaining_entries()

	def validate_dates(self):
		"""Validate and calculate duration"""
		if self.end_date < self.start_date:
			frappe.throw("End Date must be after Start Date")
		days = date_diff(self.end_date, self.start_date)
		self.duration_months = round(days / 30, 1)

	def set_payment_frequency(self):
		"""Auto-set payment frequency based on subscription type"""
		if self.subscription_type in ["Hourly", "Daily", "Entry-based"]:
			self.payment_frequency = "One-time"
		elif self.subscription_type == "Monthly":
			self.payment_frequency = "Monthly"
		elif self.subscription_type == "Annual":
			self.payment_frequency = "Annual"

	def calculate_total_from_spaces(self):
		"""Calculate total from spaces table - this is the main pricing"""
		total = 0
		for space_row in self.spaces:
			# Get the rate based on subscription type
			space = frappe.get_doc("GRM Space", space_row.space)

			if self.subscription_type == "Hourly":
				rate = flt(space.hourly_rate)
			elif self.subscription_type == "Daily":
				rate = flt(space.daily_rate)
			elif self.subscription_type == "Monthly":
				rate = flt(space.monthly_rate)
			elif self.subscription_type == "Annual":
				rate = flt(space.annual_rate)
			else:  # Entry-based
				rate = flt(space.monthly_rate)  # Default to monthly for entry-based

			# Allow override in the table
			if space_row.monthly_rate:
				rate = flt(space_row.monthly_rate)

			total += rate

		# Apply discount
		total = total - flt(self.discount_amount)
		self.total_amount = total

	def apply_taxes(self):
		"""Apply taxes from Sales Taxes and Charges Template"""
		if not self.sales_taxes_and_charges_template:
			self.tax_amount = 0
			return

		# Get tax template
		tax_template = frappe.get_doc("Sales Taxes and Charges Template",
									   self.sales_taxes_and_charges_template)

		tax_amount = 0
		for tax in tax_template.taxes:
			if tax.charge_type == "On Net Total":
				tax_amount += flt(self.total_amount) * flt(tax.rate) / 100
			elif tax.charge_type == "Actual":
				tax_amount += flt(tax.tax_amount)

		self.tax_amount = tax_amount

	def calculate_grand_total(self):
		"""Calculate grand total including tax"""
		self.grand_total = flt(self.total_amount) + flt(self.tax_amount)

	def update_remaining_entries(self):
		"""Update remaining entries for entry-based subscriptions"""
		if self.subscription_type == "Entry-based":
			self.remaining_entries = flt(self.total_entries_allowed) - flt(self.entries_used)


	@frappe.whitelist()
	def activate(self):
		"""Activate subscription and mark spaces as rented"""
		if self.status != "Draft":
			frappe.throw("Only Draft subscriptions can be activated")

		self.status = "Active"

		# Mark all spaces as rented
		for space_row in self.spaces:
			space = frappe.get_doc("GRM Space", space_row.space)
			space.status = "Rented"
			space.current_tenant = self.tenant  # Link to tenant instead of member
			space.current_subscription = self.name
			space.save(ignore_permissions=True)

		self.save()
		frappe.msgprint("Subscription activated successfully", indicator="green")

	@frappe.whitelist()
	def create_invoice(self):
		"""Create Sales Invoice for this subscription"""
		from grm_management.grm_management.doctype.grm_settings.grm_settings import get_settings

		# Get GRM Settings
		settings = get_settings()
		if not settings.subscription_item:
			frappe.throw("Please configure Subscription Item in GRM Settings")

		# Get customer from tenant
		tenant = frappe.get_doc("GRM Tenant", self.tenant)
		if not tenant.customer:
			frappe.throw("Tenant does not have a linked Customer. Please create customer first.")

		# Create invoice
		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = tenant.customer
		invoice.posting_date = nowdate()
		invoice.due_date = self.next_invoice_date or nowdate()

		# Add items from spaces using configured subscription item
		for space_row in self.spaces:
			space = frappe.get_doc("GRM Space", space_row.space)

			# Determine rate based on subscription type
			if self.subscription_type == "Hourly":
				rate = flt(space.hourly_rate)
			elif self.subscription_type == "Daily":
				rate = flt(space.daily_rate)
			elif self.subscription_type == "Monthly":
				rate = flt(space.monthly_rate)
			elif self.subscription_type == "Annual":
				rate = flt(space.annual_rate)
			else:
				rate = flt(space_row.monthly_rate) or self.total_amount

			# Use override rate if set
			if space_row.monthly_rate:
				rate = flt(space_row.monthly_rate)

			invoice.append("items", {
				"item_code": settings.subscription_item,
				"item_name": space.space_name,
				"description": f"Subscription: {self.subscription_type} - {space.space_name}",
				"qty": 1,
				"rate": rate,
				"amount": rate
			})

		# Add taxes
		if self.sales_taxes_and_charges_template:
			invoice.taxes_and_charges = self.sales_taxes_and_charges_template

			# Get tax template details
			tax_template = frappe.get_doc("Sales Taxes and Charges Template",
										   self.sales_taxes_and_charges_template)
			for tax in tax_template.taxes:
				invoice.append("taxes", tax.as_dict())

		invoice.insert(ignore_permissions=True)
		invoice.submit()

		# Update subscription
		self.last_invoice = invoice.name
		self.total_invoiced += flt(invoice.grand_total)
		self.outstanding_amount = flt(self.total_invoiced) - flt(self.total_paid)

		# Set next invoice date based on payment frequency
		if self.payment_frequency == "Monthly":
			self.next_invoice_date = add_months(nowdate(), 1)
		elif self.payment_frequency == "Quarterly":
			self.next_invoice_date = add_months(nowdate(), 3)
		elif self.payment_frequency == "Annual":
			self.next_invoice_date = add_months(nowdate(), 12)

		self.save()

		frappe.msgprint(f"Invoice {invoice.name} created successfully", indicator="green")
		return invoice.name

	@frappe.whitelist()
	def record_entry(self):
		"""Record an entry for entry-based subscriptions"""
		if self.subscription_type != "Entry-based":
			return

		self.entries_used += 1
		self.remaining_entries = self.total_entries_allowed - self.entries_used

		# Calculate overage charges
		if self.entries_used > self.total_entries_allowed:
			overage = self.entries_used - self.total_entries_allowed
			self.entry_overage_charges = overage * flt(self.extra_entry_rate)

		self.save()


@frappe.whitelist()
def create_payment_for_subscription(subscription_name, invoice_name, amount, mode_of_payment, reference_no=None, reference_date=None):
	"""Create Payment Entry for a subscription invoice"""
	from frappe.utils import nowdate

	subscription = frappe.get_doc('GRM Subscription', subscription_name)
	invoice = frappe.get_doc('Sales Invoice', invoice_name)

	# Get company
	company = invoice.company

	# Get default accounts for mode of payment
	payment_account = frappe.db.get_value('Mode of Payment Account',
		{'parent': mode_of_payment, 'company': company}, 'default_account')

	if not payment_account:
		payment_account = frappe.db.get_value('Account',
			{'account_type': 'Cash', 'company': company, 'is_group': 0}, 'name')

	if not payment_account:
		frappe.throw('No payment account found for this mode of payment')

	# Create payment entry
	payment = frappe.new_doc('Payment Entry')
	payment.payment_type = 'Receive'
	payment.party_type = 'Customer'
	payment.party = invoice.customer
	payment.company = company
	payment.posting_date = nowdate()
	payment.paid_from = frappe.db.get_value('Account',
		{'account_type': 'Receivable', 'company': company, 'is_group': 0}, 'name')
	payment.paid_to = payment_account
	payment.paid_amount = flt(amount)
	payment.received_amount = flt(amount)
	payment.mode_of_payment = mode_of_payment
	payment.reference_no = reference_no or invoice_name
	payment.reference_date = reference_date or nowdate()

	# Link to invoice
	payment.append('references', {
		'reference_doctype': 'Sales Invoice',
		'reference_name': invoice_name,
		'allocated_amount': flt(amount)
	})

	payment.insert(ignore_permissions=True)
	payment.submit()

	# Update subscription totals
	subscription.total_paid = flt(subscription.total_paid) + flt(amount)
	subscription.outstanding_amount = flt(subscription.total_invoiced) - flt(subscription.total_paid)
	subscription.save(ignore_permissions=True)

	frappe.db.commit()

	return payment.name
