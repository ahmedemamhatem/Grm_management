# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff, add_months, getdate, today

class GRMPropertyContract(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_duration()
		self.calculate_annual_rent()
		self.update_payment_statistics()

	def validate_dates(self):
		"""Validate contract dates"""
		if self.start_date and self.end_date:
			if getdate(self.end_date) <= getdate(self.start_date):
				frappe.throw(frappe._("End Date must be after Start Date"))

		# Update status based on dates
		if self.start_date and self.end_date:
			today_date = getdate(today())
			start = getdate(self.start_date)
			end = getdate(self.end_date)

			if self.status not in ["Terminated", "Renewed"]:
				if today_date < start:
					self.status = "Draft"
				elif start <= today_date <= end:
					self.status = "Active"
				elif today_date > end:
					self.status = "Expired"

	def calculate_duration(self):
		"""Calculate contract duration in years and months"""
		if self.start_date and self.end_date:
			days = date_diff(self.end_date, self.start_date)
			self.duration_years = days / 365.25
			self.duration_months = int(days / 30.44)

	def calculate_annual_rent(self):
		"""Calculate annual rent from monthly rent"""
		if self.monthly_rent:
			self.annual_rent = flt(self.monthly_rent) * 12

	def update_payment_statistics(self):
		"""Update payment statistics from payment records"""
		# Total paid
		total_paid = frappe.db.sql("""
			SELECT SUM(amount) as total
			FROM `tabGRM Payment`
			WHERE contract = %s AND payment_status = 'Paid'
		""", self.name)

		self.total_paid = flt(total_paid[0][0]) if total_paid and total_paid[0][0] else 0

		# Total pending
		total_pending = frappe.db.sql("""
			SELECT SUM(amount) as total
			FROM `tabGRM Payment`
			WHERE contract = %s AND payment_status = 'Pending'
		""", self.name)

		self.total_pending = flt(total_pending[0][0]) if total_pending and total_pending[0][0] else 0

		# Last payment date
		last_payment = frappe.db.sql("""
			SELECT payment_date
			FROM `tabGRM Payment`
			WHERE contract = %s AND payment_status = 'Paid'
			ORDER BY payment_date DESC
			LIMIT 1
		""", self.name)

		if last_payment and last_payment[0][0]:
			self.last_payment_date = last_payment[0][0]

		# Calculate next payment date
		if self.payment_frequency == "Monthly":
			self.next_payment_date = add_months(self.last_payment_date or self.start_date, 1)
		elif self.payment_frequency == "Quarterly":
			self.next_payment_date = add_months(self.last_payment_date or self.start_date, 3)
		elif self.payment_frequency == "Semi-Annually":
			self.next_payment_date = add_months(self.last_payment_date or self.start_date, 6)
		elif self.payment_frequency == "Annually":
			self.next_payment_date = add_months(self.last_payment_date or self.start_date, 12)

	def on_update(self):
		"""Update linked property and landlord"""
		if self.property:
			property_doc = frappe.get_doc("GRM Property", self.property)
			property_doc.contract = self.name
			property_doc.save(ignore_permissions=True)
