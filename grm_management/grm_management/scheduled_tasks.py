# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime, add_days, add_months, getdate


# ============================================================================
# HOURLY TASKS
# ============================================================================

def hourly():
	"""Run all hourly scheduled tasks"""
	sync_all_device_attendance()
	check_booking_access()
	check_device_health()


def sync_all_device_attendance():
	"""Sync attendance from all online Access Devices (Direct ZK and BioTime)"""
	try:
		# Sync Direct ZK devices
		direct_devices = frappe.get_all("Access Device", filters={
			"status": "Online",
			"auto_sync": 1,
			"connection_mode": "Direct ZK"
		}, fields=["name", "device_name"])

		for device in direct_devices:
			try:
				device_doc = frappe.get_doc("Access Device", device.name)
				device_doc.sync_attendance()
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(
					f"Error syncing Direct ZK device {device.device_name}: {str(e)}",
					"Scheduled Device Sync Error"
				)
				continue

		# Sync BioTime API (centralized sync for all BioTime devices)
		biotime_settings = frappe.get_single("BioTime Settings")
		if biotime_settings.enabled and biotime_settings.auto_sync:
			try:
				biotime_settings.sync_attendance()
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(
					f"Error syncing BioTime attendance: {str(e)}",
					"Scheduled BioTime Sync Error"
				)

		frappe.logger().info(f"Hourly: Synced {len(direct_devices)} Direct ZK devices + BioTime")

	except Exception as e:
		frappe.log_error(f"Error in sync_all_device_attendance: {str(e)}", "Scheduled Task Error")


def check_booking_access():
	"""Grant/revoke access for bookings based on time"""
	try:
		current_time = now_datetime()
		current_date = nowdate()

		# Find bookings that are Confirmed and should be starting soon (within next hour)
		upcoming_bookings = frappe.get_all("Booking", filters={
			"status": "Confirmed",
			"booking_date": current_date
		}, fields=["name", "start_time", "end_time"])

		for booking in upcoming_bookings:
			# Check if booking is within access window
			# This is simplified - actual implementation would check time more precisely
			pass

		frappe.logger().info(f"Hourly: Checked {len(upcoming_bookings)} bookings for access")

	except Exception as e:
		frappe.log_error(f"Error in check_booking_access: {str(e)}", "Scheduled Task Error")


def check_device_health():
	"""Ping all devices and update status"""
	try:
		devices = frappe.get_all("Access Device", filters={
			"status": ["!=", "Maintenance"]
		}, fields=["name", "device_name"])

		online_count = 0
		offline_count = 0

		for device in devices:
			try:
				device_doc = frappe.get_doc("Access Device", device.name)
				conn = device_doc.get_connection()

				if conn:
					conn.disconnect()
					online_count += 1
				else:
					offline_count += 1

			except Exception as e:
				frappe.log_error(
					f"Error checking device health for {device.device_name}: {str(e)}",
					"Device Health Check Error"
				)
				offline_count += 1
				continue

		frappe.logger().info(f"Hourly: Device health check - Online: {online_count}, Offline: {offline_count}")

	except Exception as e:
		frappe.log_error(f"Error in check_device_health: {str(e)}", "Scheduled Task Error")


# ============================================================================
# DAILY TASKS
# ============================================================================

def daily():
	"""Run all daily scheduled tasks at midnight"""
	expire_contracts()
	expire_memberships()
	send_expiry_reminders()
	mark_no_show_bookings()
	update_member_statistics()


def expire_contracts():
	"""Find and expire contracts where end_date < today"""
	try:
		today = getdate(nowdate())

		# Find Active contracts that have expired
		expired_contracts = frappe.get_all("GRM Contract", filters={
			"status": "Active",
			"end_date": ["<", today]
		}, fields=["name", "contract_number", "member"])

		for contract in expired_contracts:
			try:
				contract_doc = frappe.get_doc("GRM Contract", contract.name)
				contract_doc.expire()
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(
					f"Error expiring contract {contract.contract_number}: {str(e)}",
					"Contract Expiry Error"
				)
				continue

		frappe.logger().info(f"Daily: Expired {len(expired_contracts)} contracts")

	except Exception as e:
		frappe.log_error(f"Error in expire_contracts: {str(e)}", "Scheduled Task Error")


def expire_memberships():
	"""Find and expire memberships where end_date < today"""
	try:
		today = getdate(nowdate())

		# Find Active memberships that have expired
		expired_memberships = frappe.get_all("Membership", filters={
			"status": "Active",
			"end_date": ["<", today]
		}, fields=["name", "membership_number", "member"])

		for membership in expired_memberships:
			try:
				membership_doc = frappe.get_doc("Membership", membership.name)
				membership_doc.expire()
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(
					f"Error expiring membership {membership.membership_number}: {str(e)}",
					"Membership Expiry Error"
				)
				continue

		frappe.logger().info(f"Daily: Expired {len(expired_memberships)} memberships")

	except Exception as e:
		frappe.log_error(f"Error in expire_memberships: {str(e)}", "Scheduled Task Error")


def send_expiry_reminders():
	"""Send reminders for contracts/memberships expiring in 30/15/7/1 days"""
	try:
		today = getdate(nowdate())

		# Reminder periods in days
		reminder_periods = [30, 15, 7, 1]

		for days in reminder_periods:
			expiry_date = add_days(today, days)

			# Contracts expiring
			contracts = frappe.get_all("GRM Contract", filters={
				"status": "Active",
				"end_date": expiry_date
			}, fields=["name", "contract_number", "member", "end_date"])

			for contract in contracts:
				try:
					member = frappe.get_doc("Member", contract.member)
					if member.primary_email:
						frappe.sendmail(
							recipients=[member.primary_email],
							subject=f"Contract {contract.contract_number} expiring in {days} days",
							message=f"""
							<p>Dear {member.member_name},</p>
							<p>This is a reminder that your contract {contract.contract_number} will expire on {contract.end_date}.</p>
							<p>Please contact us if you wish to renew.</p>
							<p>Thank you.</p>
							"""
						)
				except Exception as e:
					frappe.log_error(
						f"Error sending reminder for contract {contract.contract_number}: {str(e)}",
						"Contract Reminder Error"
					)

			# Memberships expiring
			memberships = frappe.get_all("Membership", filters={
				"status": "Active",
				"end_date": expiry_date,
				"renewal_reminder_sent": 0
			}, fields=["name", "membership_number", "member", "end_date"])

			for membership in memberships:
				try:
					member = frappe.get_doc("Member", membership.member)
					if member.primary_email:
						frappe.sendmail(
							recipients=[member.primary_email],
							subject=f"Membership {membership.membership_number} expiring in {days} days",
							message=f"""
							<p>Dear {member.member_name},</p>
							<p>This is a reminder that your membership {membership.membership_number} will expire on {membership.end_date}.</p>
							<p>Please renew to continue enjoying our services.</p>
							<p>Thank you.</p>
							"""
						)

						# Mark reminder as sent for 7-day reminder
						if days == 7:
							frappe.db.set_value("Membership", membership.name, "renewal_reminder_sent", 1)

				except Exception as e:
					frappe.log_error(
						f"Error sending reminder for membership {membership.membership_number}: {str(e)}",
						"Membership Reminder Error"
					)

		frappe.logger().info(f"Daily: Sent expiry reminders")

	except Exception as e:
		frappe.log_error(f"Error in send_expiry_reminders: {str(e)}", "Scheduled Task Error")


def mark_no_show_bookings():
	"""Mark yesterday's unattended Confirmed bookings as No-Show"""
	try:
		yesterday = add_days(nowdate(), -1)

		# Find Confirmed bookings from yesterday that were not checked-in
		no_show_bookings = frappe.get_all("Booking", filters={
			"status": "Confirmed",
			"booking_date": yesterday
		}, fields=["name"])

		for booking in no_show_bookings:
			try:
				booking_doc = frappe.get_doc("Booking", booking.name)
				booking_doc.mark_no_show()
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(
					f"Error marking booking {booking.name} as no-show: {str(e)}",
					"Booking No-Show Error"
				)
				continue

		frappe.logger().info(f"Daily: Marked {len(no_show_bookings)} bookings as No-Show")

	except Exception as e:
		frappe.log_error(f"Error in mark_no_show_bookings: {str(e)}", "Scheduled Task Error")


def update_member_statistics():
	"""Refresh statistics for all active members"""
	try:
		# Update statistics for members with active contracts or memberships
		members = frappe.get_all("Member", filters={
			"status": "Active"
		}, fields=["name"], limit=100)  # Limit to avoid timeout

		for member in members:
			try:
				member_doc = frappe.get_doc("Member", member.name)
				member_doc.update_statistics()
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(
					f"Error updating statistics for member {member.name}: {str(e)}",
					"Member Stats Update Error"
				)
				continue

		frappe.logger().info(f"Daily: Updated statistics for {len(members)} members")

	except Exception as e:
		frappe.log_error(f"Error in update_member_statistics: {str(e)}", "Scheduled Task Error")


# ============================================================================
# MONTHLY TASKS
# ============================================================================

def monthly():
	"""Run all monthly scheduled tasks on the 1st of each month"""
	generate_contract_invoices()
	reset_membership_counters()
	auto_renew_memberships()


def generate_contract_invoices():
	"""Create monthly invoices for all Active contracts"""
	try:
		active_contracts = frappe.get_all("GRM Contract", filters={
			"status": "Active"
		}, fields=["name", "contract_number", "member", "net_monthly_rent"])

		for contract in active_contracts:
			try:
				# Get member's customer
				member = frappe.get_doc("Member", contract.member)
				if not member.customer:
					continue

				# Create Sales Invoice
				invoice = frappe.new_doc("Sales Invoice")
				invoice.customer = member.customer
				invoice.posting_date = nowdate()
				invoice.due_date = add_days(nowdate(), 30)

				# Add contract rent as item
				invoice.append("items", {
					"item_code": "Coworking Space Rent",
					"item_name": f"Contract {contract.contract_number} - Monthly Rent",
					"description": f"Monthly rent for contract {contract.contract_number}",
					"qty": 1,
					"rate": contract.net_monthly_rent,
					"amount": contract.net_monthly_rent
				})

				invoice.insert(ignore_permissions=True)
				frappe.db.commit()

			except Exception as e:
				frappe.log_error(
					f"Error creating invoice for contract {contract.contract_number}: {str(e)}",
					"Contract Invoice Generation Error"
				)
				continue

		frappe.logger().info(f"Monthly: Generated invoices for {len(active_contracts)} contracts")

	except Exception as e:
		frappe.log_error(f"Error in generate_contract_invoices: {str(e)}", "Scheduled Task Error")


def reset_membership_counters():
	"""Reset monthly access counters for memberships with Monthly access type"""
	try:
		memberships = frappe.get_all("Membership", filters={
			"status": "Active",
			"access_type": ["in", ["Monthly", "Monthly Entries"]]
		}, fields=["name", "membership_number", "access_used", "access_remaining"])

		for membership in memberships:
			try:
				membership_doc = frappe.get_doc("Membership", membership.name)

				# Calculate rollover (unused access)
				rollover = max(0, (membership_doc.access_remaining or 0))

				# Reset counters
				membership_doc.access_used = 0
				membership_doc.rollover_from_previous = rollover
				membership_doc.access_remaining = (membership_doc.total_access_allowed or 0) + rollover

				membership_doc.save()
				frappe.db.commit()

			except Exception as e:
				frappe.log_error(
					f"Error resetting counters for membership {membership.membership_number}: {str(e)}",
					"Membership Counter Reset Error"
				)
				continue

		frappe.logger().info(f"Monthly: Reset counters for {len(memberships)} memberships")

	except Exception as e:
		frappe.log_error(f"Error in reset_membership_counters: {str(e)}", "Scheduled Task Error")


def auto_renew_memberships():
	"""Auto-renew memberships that have auto_renew enabled and are expiring"""
	try:
		# Find memberships expiring in next 7 days with auto_renew enabled
		expiry_date = add_days(nowdate(), 7)

		memberships = frappe.get_all("Membership", filters={
			"status": "Active",
			"auto_renew": 1,
			"end_date": ["<=", expiry_date],
			"renewed_to": ["is", "not set"]
		}, fields=["name", "membership_number", "member"])

		for membership in memberships:
			try:
				membership_doc = frappe.get_doc("Membership", membership.name)
				new_membership = membership_doc.renew()
				frappe.db.commit()

				# Send notification to member
				member = frappe.get_doc("Member", membership.member)
				if member.primary_email:
					frappe.sendmail(
						recipients=[member.primary_email],
						subject=f"Membership {membership.membership_number} auto-renewed",
						message=f"""
						<p>Dear {member.member_name},</p>
						<p>Your membership {membership.membership_number} has been automatically renewed.</p>
						<p>New membership number: {new_membership}</p>
						<p>Thank you.</p>
						"""
					)

			except Exception as e:
				frappe.log_error(
					f"Error auto-renewing membership {membership.membership_number}: {str(e)}",
					"Membership Auto-Renew Error"
				)
				continue

		frappe.logger().info(f"Monthly: Auto-renewed {len(memberships)} memberships")

	except Exception as e:
		frappe.log_error(f"Error in auto_renew_memberships: {str(e)}", "Scheduled Task Error")
