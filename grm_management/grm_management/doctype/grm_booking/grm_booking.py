# Copyright (c) 2026, Wael ELsafty and contributors
import frappe
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours, now

class GRMBooking(Document):
	def validate(self):
		self.set_rate_from_booking_type()
		self.calculate_duration()
		self.calculate_pricing()

	def set_rate_from_booking_type(self):
		"""Set rate type and rate based on booking type from space"""
		if not self.space:
			return

		# Set rate_type based on booking_type
		if self.booking_type == "Hourly":
			self.rate_type = "Hourly"
		elif self.booking_type in ["Daily", "Multi-day"]:
			self.rate_type = "Daily"

		# Fetch rate from space if not already set or if space changed
		space = frappe.get_doc("GRM Space", self.space)
		if self.rate_type == "Hourly":
			if not self.hourly_rate:
				self.hourly_rate = flt(space.hourly_rate)
		elif self.rate_type == "Daily":
			if not self.hourly_rate:
				self.hourly_rate = flt(space.daily_rate)

	def calculate_duration(self):
		if self.start_time and self.end_time:
			self.duration_hours = time_diff_in_hours(self.end_time, self.start_time)
			self.total_hours = self.duration_hours

	def calculate_pricing(self):
		"""Calculate pricing based on rate type"""
		if self.rate_type == "Hourly" and self.hourly_rate and self.total_hours:
			self.subtotal = flt(self.hourly_rate) * flt(self.total_hours)
		elif self.rate_type == "Daily" and self.hourly_rate:
			# For daily rate, hourly_rate field contains daily rate
			self.subtotal = flt(self.hourly_rate)
		self.total_amount = flt(self.subtotal) - flt(self.discount) + flt(self.tax) + flt(self.overtime_charges)
		
	@frappe.whitelist()
	def confirm_booking(self):
		"""Confirm a draft booking"""
		if self.status != "Draft":
			frappe.throw("Only Draft bookings can be confirmed")
		self.status = "Confirmed"
		self.save()
		frappe.msgprint("Booking confirmed successfully", indicator="green")

	@frappe.whitelist()
	def check_in(self):
		if self.status != "Confirmed":
			frappe.throw("Only Confirmed bookings can be checked in")
		self.actual_check_in = now()
		self.status = "Checked-in"
		self.save()
		frappe.msgprint("Checked in successfully", indicator="green")
		
	@frappe.whitelist()
	def check_out(self):
		self.actual_check_out = now()
		self.status = "Checked-out"
		if self.actual_check_in and self.actual_check_out:
			actual_hours = time_diff_in_hours(self.actual_check_out, self.actual_check_in)
			if actual_hours > self.total_hours:
				self.overtime_hours = actual_hours - self.total_hours
				self.overtime_charges = self.overtime_hours * flt(self.hourly_rate) * 1.5
		self.calculate_pricing()
		self.save()
		frappe.msgprint("Checked out successfully", indicator="green")
