# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class LocationExpense(Document):
	"""
	Location Expense DocType Controller

	Manages expenses for GRM Locations with automatic:
	- Purchase Invoice creation
	- Payment Entry creation for paid expenses
	"""

	def validate(self):
		"""Validate expense data"""
		self.validate_payment_date()
		self.set_expense_id()

	def validate_payment_date(self):
		"""Ensure payment date is set if status is Paid"""
		if self.payment_status == "Paid" and not self.payment_date:
			self.payment_date = nowdate()

	def set_expense_id(self):
		"""Auto-generate expense ID if not set"""
		if not self.expense_id:
			self.expense_id = self.name

	@frappe.whitelist()
	def create_purchase_invoice(self):
		"""
		Create Purchase Invoice from Location Expense

		Returns:
			dict: Created Purchase Invoice details
		"""
		if self.purchase_invoice:
			frappe.throw(f"Purchase Invoice {self.purchase_invoice} already created for this expense")

		if not self.vendor:
			frappe.throw("Please set Vendor before creating Purchase Invoice")

		# Create Purchase Invoice
		pi = frappe.new_doc("Purchase Invoice")
		pi.supplier = self.vendor
		pi.posting_date = self.expense_date
		pi.bill_no = self.invoice_number or self.expense_id
		pi.bill_date = self.expense_date
		pi.due_date = self.expense_date
		pi.set_posting_time = 1

		# Add expense as line item
		pi.append("items", {
			"item_code": self._get_expense_item(self.expense_type),
			"item_name": f"{self.expense_type} - {self.location}",
			"description": self.description or f"{self.expense_type} expense for {self.location}",
			"qty": 1,
			"rate": self.amount,
			"amount": self.amount,
			"expense_account": self._get_expense_account(self.expense_type),
			"cost_center": self._get_cost_center()
		})

		pi.insert(ignore_permissions=True)

		# Link Purchase Invoice
		self.purchase_invoice = pi.name
		self.save(ignore_permissions=True)

		frappe.msgprint(
			f"Purchase Invoice {pi.name} created successfully",
			title="Purchase Invoice Created",
			indicator="green"
		)

		return {
			"purchase_invoice": pi.name,
			"grand_total": pi.grand_total
		}

	@frappe.whitelist()
	def create_payment_entry(self):
		"""
		Create Payment Entry for this expense if Paid

		Returns:
			dict: Created Payment Entry details
		"""
		if not self.purchase_invoice:
			frappe.throw("Please create Purchase Invoice first")

		if self.payment_status != "Paid":
			frappe.throw("Payment Status must be 'Paid' to create Payment Entry")

		# Check if payment already exists
		existing_payment = frappe.db.exists("Payment Entry Reference", {
			"reference_doctype": "Purchase Invoice",
			"reference_name": self.purchase_invoice
		})

		if existing_payment:
			payment_entry = frappe.db.get_value(
				"Payment Entry Reference",
				existing_payment,
				"parent"
			)
			frappe.throw(f"Payment Entry {payment_entry} already exists for this invoice")

		pi = frappe.get_doc("Purchase Invoice", self.purchase_invoice)

		# Create Payment Entry
		pe = frappe.new_doc("Payment Entry")
		pe.payment_type = "Pay"
		pe.posting_date = self.payment_date or nowdate()
		pe.party_type = "Supplier"
		pe.party = self.vendor
		pe.paid_to = self._get_payable_account()
		pe.paid_from = self._get_payment_account()
		pe.paid_amount = self.amount
		pe.received_amount = self.amount
		pe.reference_no = self.invoice_number or self.expense_id
		pe.reference_date = self.payment_date or nowdate()

		# Add reference to Purchase Invoice
		pe.append("references", {
			"reference_doctype": "Purchase Invoice",
			"reference_name": self.purchase_invoice,
			"total_amount": pi.grand_total,
			"outstanding_amount": pi.outstanding_amount,
			"allocated_amount": self.amount
		})

		pe.insert(ignore_permissions=True)
		pe.submit()

		frappe.msgprint(
			f"Payment Entry {pe.name} created and submitted successfully",
			title="Payment Entry Created",
			indicator="green"
		)

		return {
			"payment_entry": pe.name,
			"paid_amount": pe.paid_amount
		}

	def _get_expense_item(self, expense_type):
		"""
		Get or create expense item for this expense type

		Args:
			expense_type: Type of expense (Rent, Electricity, etc.)

		Returns:
			str: Item code
		"""
		item_code = f"EXP-{expense_type.upper().replace(' ', '-')}"

		if not frappe.db.exists("Item", item_code):
			# Create item
			item = frappe.new_doc("Item")
			item.item_code = item_code
			item.item_name = f"{expense_type} Expense"
			item.item_group = "Services"
			item.stock_uom = "Unit"
			item.is_stock_item = 0
			item.is_purchase_item = 1
			item.insert(ignore_permissions=True)

		return item_code

	def _get_expense_account(self, expense_type):
		"""
		Get expense account based on expense type

		Args:
			expense_type: Type of expense

		Returns:
			str: Expense account name
		"""
		# Map expense types to accounts
		expense_accounts = {
			"Rent": "Rent - ",
			"Electricity": "Electricity Expenses - ",
			"Water": "Water Expenses - ",
			"Internet": "Telephone and Internet Expenses - ",
			"Cleaning": "Cleaning Expenses - ",
			"Maintenance": "Repairs and Maintenance - ",
			"Security": "Security Services - ",
			"Supplies": "Office Supplies - ",
			"Other": "Miscellaneous Expenses - "
		}

		account_prefix = expense_accounts.get(expense_type, "Miscellaneous Expenses - ")
		company = frappe.defaults.get_defaults().company

		# Get company abbreviation
		company_abbr = frappe.db.get_value("Company", company, "abbr")
		account_name = f"{account_prefix}{company_abbr}"

		# Check if account exists, otherwise use default
		if not frappe.db.exists("Account", account_name):
			# Use default expense account
			account_name = frappe.db.get_value(
				"Account",
				{"account_type": "Expense", "company": company, "is_group": 0},
				"name"
			)

		return account_name

	def _get_cost_center(self):
		"""
		Get cost center for this location

		Returns:
			str: Cost center name
		"""
		company = frappe.defaults.get_defaults().company

		# Try to get cost center based on location
		cost_center_name = f"{self.location} - "
		company_abbr = frappe.db.get_value("Company", company, "abbr")
		cost_center = f"{cost_center_name}{company_abbr}"

		if not frappe.db.exists("Cost Center", cost_center):
			# Use default cost center
			cost_center = frappe.db.get_value(
				"Cost Center",
				{"company": company, "is_group": 0},
				"name"
			)

		return cost_center

	def _get_payable_account(self):
		"""Get default payable account"""
		company = frappe.defaults.get_defaults().company
		return frappe.db.get_value("Company", company, "default_payable_account")

	def _get_payment_account(self):
		"""Get default cash/bank account for payment"""
		company = frappe.defaults.get_defaults().company

		# Get default cash account
		cash_account = frappe.db.get_value(
			"Account",
			{
				"account_type": "Cash",
				"company": company,
				"is_group": 0
			},
			"name"
		)

		if not cash_account:
			# Get default bank account
			cash_account = frappe.db.get_value(
				"Account",
				{
					"account_type": "Bank",
					"company": company,
					"is_group": 0
				},
				"name"
			)

		return cash_account

	@frappe.whitelist()
	def auto_create_invoice_and_payment(self):
		"""
		Automatically create Purchase Invoice and Payment Entry if paid

		Returns:
			dict: Created documents details
		"""
		result = {}

		# Create Purchase Invoice if not exists
		if not self.purchase_invoice:
			pi_result = self.create_purchase_invoice()
			result.update(pi_result)

		# Create Payment Entry if paid
		if self.payment_status == "Paid":
			try:
				pe_result = self.create_payment_entry()
				result.update(pe_result)
			except Exception as e:
				frappe.log_error(f"Error creating payment entry: {str(e)}", "Location Expense Payment Error")
				frappe.msgprint(
					f"Purchase Invoice created but Payment Entry failed: {str(e)}",
					title="Partial Success",
					indicator="orange"
				)

		return result
