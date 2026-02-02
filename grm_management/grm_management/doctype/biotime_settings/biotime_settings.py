# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import requests
import json
from datetime import datetime, timedelta


class BioTimeSettings(Document):
	def validate(self):
		"""Validate BioTime settings"""
		if self.enabled:
			self._validate_connection_settings()

	def _validate_connection_settings(self):
		"""Validate server URL and port"""
		if not self.server_url:
			frappe.throw(_("Server URL is required when BioTime is enabled"))
		if not self.port:
			frappe.throw(_("Port is required when BioTime is enabled"))
		if not self.username or not self.password:
			frappe.throw(_("Username and Password are required when BioTime is enabled"))

	def get_base_url(self):
		"""Get base URL for BioTime API"""
		return f"http://{self.server_url}:{self.port}"

	@frappe.whitelist()
	def get_token(self):
		"""Get authentication token from BioTime server"""
		try:
			url = f"{self.get_base_url()}/jwt-api-token-auth/"

			payload = {
				"username": self.username,
				"password": self.get_password("password")
			}

			response = requests.post(url, json=payload, timeout=10)

			if response.status_code == 200:
				data = response.json()
				self.access_token = data.get("token")
				# BioTime tokens typically expire in 24 hours
				self.token_expiry = frappe.utils.add_to_date(frappe.utils.now_datetime(), hours=24)
				self.save()

				frappe.msgprint(_("Authentication successful! Token retrieved."), indicator="green", alert=True)

				return {
					"success": True,
					"token": self.access_token
				}
			else:
				error_msg = f"Authentication failed: {response.status_code} - {response.text}"
				frappe.log_error(error_msg, "BioTime Authentication Error")
				frappe.throw(_(error_msg))

		except Exception as e:
			error_msg = f"Error getting BioTime token: {str(e)}"
			frappe.log_error(error_msg, "BioTime Token Error")
			frappe.throw(_(error_msg))

	def ensure_token_valid(self):
		"""Ensure access token is valid, refresh if expired"""
		if not self.access_token:
			self.get_token()
			return

		# Check if token is expired or will expire in next 5 minutes
		if self.token_expiry:
			expiry = frappe.utils.get_datetime(self.token_expiry)
			now = frappe.utils.now_datetime()

			if expiry <= now + timedelta(minutes=5):
				self.get_token()

	def get_headers(self):
		"""Get request headers with authentication"""
		self.ensure_token_valid()

		return {
			"Authorization": f"JWT {self.access_token}",
			"Content-Type": "application/json"
		}

	@frappe.whitelist()
	def test_connection(self):
		"""Test connection to BioTime server"""
		try:
			# First get token
			self.get_token()

			# Then test by fetching some data
			url = f"{self.get_base_url()}/iclock/api/terminals/"

			response = requests.get(url, headers=self.get_headers(), timeout=10)

			if response.status_code == 200:
				data = response.json()
				device_count = data.get("count", 0)

				frappe.msgprint(
					_("Connection successful!<br>Devices found: {0}").format(device_count),
					indicator="green",
					alert=True
				)

				return {
					"success": True,
					"device_count": device_count
				}
			else:
				error_msg = f"Connection test failed: {response.status_code}"
				frappe.msgprint(_(error_msg), indicator="red", alert=True)
				return {"success": False, "error": error_msg}

		except Exception as e:
			error_msg = str(e)
			frappe.log_error(f"BioTime connection test error: {error_msg}", "BioTime Connection Test")
			frappe.msgprint(_("Connection test failed: {0}").format(error_msg), indicator="red", alert=True)
			return {"success": False, "error": error_msg}

	@frappe.whitelist()
	def sync_attendance(self):
		"""Sync attendance data from BioTime server"""
		try:
			self.ensure_token_valid()

			# Determine date range
			if self.sync_from_date:
				from_date = self.sync_from_date
			else:
				# Default to last sync time or 7 days ago
				from_date = self.last_sync_time.date() if self.last_sync_time else frappe.utils.add_days(frappe.utils.nowdate(), -7)

			if self.sync_to_date:
				to_date = self.sync_to_date
			else:
				to_date = frappe.utils.nowdate()

			# Fetch attendance transactions
			url = f"{self.get_base_url()}/iclock/api/transactions/"

			params = {
				"start_date": from_date,
				"end_date": to_date,
				"page_size": self.batch_size or 100,
				"page": 1
			}

			new_logs = 0
			duplicate_logs = 0
			total_fetched = 0

			while True:
				response = requests.get(url, headers=self.get_headers(), params=params, timeout=30)

				if response.status_code != 200:
					error_msg = f"Failed to fetch attendance: {response.status_code}"
					frappe.log_error(error_msg, "BioTime Sync Error")
					break

				data = response.json()
				results = data.get("data", [])

				if not results:
					break

				total_fetched += len(results)

				# Process each attendance record
				for record in results:
					created = self._create_access_log_from_biotime(record)
					if created:
						new_logs += 1
					else:
						duplicate_logs += 1

				frappe.db.commit()

				# Check if there are more pages
				if not data.get("next"):
					break

				params["page"] += 1

			# Update sync status
			self.last_sync_time = frappe.utils.now_datetime()
			self.last_sync_status = "Success"
			self.save()

			frappe.msgprint(
				_("Sync completed!<br>Total fetched: {0}<br>New logs: {1}<br>Duplicates: {2}").format(
					total_fetched, new_logs, duplicate_logs
				),
				indicator="green",
				alert=True
			)

			return {
				"success": True,
				"total_fetched": total_fetched,
				"new_logs": new_logs,
				"duplicate_logs": duplicate_logs
			}

		except Exception as e:
			error_msg = str(e)
			frappe.log_error(f"BioTime sync error: {error_msg}", "BioTime Sync Error")

			self.last_sync_status = "Failed"
			self.save()

			frappe.throw(_("Sync failed: {0}").format(error_msg))

	def _create_access_log_from_biotime(self, record):
		"""Create Access Log from BioTime transaction record

		Args:
			record: BioTime transaction data

		Returns:
			bool: True if new log created, False if duplicate
		"""
		try:
			# Extract data from BioTime record
			# Field names may vary depending on BioTime version
			emp_code = record.get("emp_code") or record.get("employee_code")
			punch_time = record.get("punch_time") or record.get("time")
			punch_state = record.get("punch_state", 0)  # 0=Check-In, 1=Check-Out
			terminal_sn = record.get("terminal_sn") or record.get("device_sn")

			if not emp_code or not punch_time:
				return False

			# Parse timestamp
			timestamp = frappe.utils.get_datetime(punch_time)

			# Check for duplicate
			existing = frappe.db.exists("Access Log", {
				"zk_user_id": str(emp_code),
				"event_time": timestamp
			})

			if existing:
				return False

			# Find member by employee code (mapped to ZK User ID)
			member = frappe.db.get_value("Member", {"zk_user_id": str(emp_code)}, "name")

			# Find device by serial number
			device = None
			if terminal_sn:
				device = frappe.db.get_value("Access Device", {"serial_number": terminal_sn}, "name")

			# Create Access Log
			log = frappe.new_doc("Access Log")
			log.zk_user_id = str(emp_code)
			log.event_time = timestamp
			log.event_type = "Check-In" if punch_state == 0 else "Check-Out"

			if member:
				log.member = member
				# Get member's location
				member_doc = frappe.get_doc("Member", member)
				# Try to get location from active contract or membership
				contract = frappe.db.get_value("GRM Contract", {"member": member, "status": "Active"}, "name")
				if contract:
					contract_doc = frappe.get_doc("GRM Contract", contract)
					if contract_doc.spaces:
						space = frappe.get_doc("Space", contract_doc.spaces[0].space)
						log.location = space.location

			if device:
				log.device = device

			log.context_type = "BioTime"
			log.insert(ignore_permissions=True)

			return True

		except Exception as e:
			frappe.log_error(f"Error creating access log from BioTime record: {str(e)}", "BioTime Log Creation Error")
			return False

	@frappe.whitelist()
	def sync_devices(self):
		"""Sync device list from BioTime server to Access Device records"""
		try:
			self.ensure_token_valid()

			url = f"{self.get_base_url()}/iclock/api/terminals/"

			response = requests.get(url, headers=self.get_headers(), timeout=30)

			if response.status_code != 200:
				frappe.throw(_("Failed to fetch devices: {0}").format(response.status_code))

			data = response.json()
			devices = data.get("data", [])

			created_count = 0
			updated_count = 0

			for device_data in devices:
				sn = device_data.get("sn") or device_data.get("terminal_sn")
				name = device_data.get("alias") or device_data.get("terminal_name") or sn
				ip_address = device_data.get("ip_address")

				if not sn:
					continue

				# Check if device exists
				existing = frappe.db.get_value("Access Device", {"serial_number": sn}, "name")

				if existing:
					# Update existing device
					device = frappe.get_doc("Access Device", existing)
					device.device_name = name
					if ip_address:
						device.ip_address = ip_address
					device.save()
					updated_count += 1
				else:
					# Create new device
					device = frappe.new_doc("Access Device")
					device.device_name = name
					device.device_code = sn
					device.serial_number = sn
					device.device_type = "BioTime"
					device.status = "Online"
					if ip_address:
						device.ip_address = ip_address
						device.port = self.port
					device.insert(ignore_permissions=True)
					created_count += 1

			frappe.db.commit()

			frappe.msgprint(
				_("Device sync completed!<br>Created: {0}<br>Updated: {1}").format(created_count, updated_count),
				indicator="green",
				alert=True
			)

			return {
				"success": True,
				"created": created_count,
				"updated": updated_count
			}

		except Exception as e:
			error_msg = str(e)
			frappe.log_error(f"BioTime device sync error: {error_msg}", "BioTime Device Sync Error")
			frappe.throw(_("Device sync failed: {0}").format(error_msg))


@frappe.whitelist()
def get_biotime_settings():
	"""Get BioTime Settings singleton"""
	if not frappe.db.exists("BioTime Settings", "BioTime Settings"):
		settings = frappe.new_doc("BioTime Settings")
		settings.insert(ignore_permissions=True)

	return frappe.get_doc("BioTime Settings", "BioTime Settings")
