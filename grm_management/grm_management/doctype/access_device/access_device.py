# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import re


class AccessDevice(Document):
	def validate(self):
		"""Validate device configuration"""
		# Set use_biotime flag based on connection_mode
		if self.connection_mode == "BioTime API":
			self.use_biotime = 1
		else:
			self.use_biotime = 0

		# Only validate IP/port for Direct ZK mode
		if self.connection_mode == "Direct ZK":
			self._validate_ip_address()
			self._validate_port()

	def _validate_ip_address(self):
		"""Validate IP address format"""
		if self.ip_address:
			ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
			if not re.match(ip_pattern, self.ip_address):
				frappe.throw(_("Invalid IP address format: {0}").format(self.ip_address))

			# Validate each octet is 0-255
			octets = self.ip_address.split('.')
			for octet in octets:
				if int(octet) > 255:
					frappe.throw(_("Invalid IP address: octet {0} is greater than 255").format(octet))

	def _validate_port(self):
		"""Validate port number"""
		if self.port:
			if self.port < 1 or self.port > 65535:
				frappe.throw(_("Port number must be between 1 and 65535"))

	def get_connection(self):
		"""Get ZK device connection

		Returns:
			ZK object or None if connection failed
		"""
		try:
			# Import pyzk library
			from zk import ZK

			# Create ZK connection
			zk = ZK(
				self.ip_address,
				port=self.port,
				timeout=5,
				password=self.communication_key or 0,
				force_udp=True if self.connectiontype == 'UDP' else False,
				ommit_ping=False
			)

			# Connect to device
			conn = zk.connect()

			# Update status
			self.status = 'Online'
			self.last_sync_status = 'Success'
			self.last_error = None
			self.db_set('status', 'Online', update_modified=False)

			return conn

		except ImportError:
			frappe.log_error("pyzk library not installed. Run: pip install pyzk", "ZK Connection Error")
			frappe.msgprint(_("pyzk library not installed. Please contact administrator."), indicator="red", alert=True)
			return None

		except Exception as e:
			error_msg = str(e)
			frappe.log_error(f"Error connecting to device {self.device_name}: {error_msg}", "ZK Connection Error")

			# Update status
			self.status = 'Offline'
			self.last_sync_status = 'Failed'
			self.last_error = error_msg
			self.db_set('status', 'Offline', update_modified=False)
			self.db_set('last_error', error_msg, update_modified=False)

			return None

	@frappe.whitelist()
	def test_connection(self):
		"""Test connection to ZK device"""
		try:
			conn = self.get_connection()

			if conn:
				# Get device info
				firmware = conn.get_firmware_version()
				users_count = len(conn.get_users())
				records_count = len(conn.get_attendance())

				conn.disconnect()

				self.status = 'Online'
				self.last_sync_time = frappe.utils.now()
				self.last_sync_status = 'Success'
				self.last_error = None
				self.save()

				frappe.msgprint(
					_("Connection successful!<br>Firmware: {0}<br>Users: {1}<br>Records: {2}").format(
						firmware, users_count, records_count
					),
					indicator="green",
					alert=True
				)

				return {
					"success": True,
					"firmware": firmware,
					"users_count": users_count,
					"records_count": records_count
				}
			else:
				frappe.msgprint(_("Connection failed. Check device settings."), indicator="red", alert=True)
				return {"success": False}

		except Exception as e:
			frappe.log_error(f"Error testing connection: {str(e)}", "ZK Connection Test Error")
			frappe.msgprint(_("Connection test failed: {0}").format(str(e)), indicator="red", alert=True)
			return {"success": False, "error": str(e)}

	@frappe.whitelist()
	def sync_attendance(self):
		"""Sync attendance logs from device (Direct ZK or BioTime API)"""
		# Check connection mode
		if self.connection_mode == "BioTime API":
			return self._sync_attendance_biotime()
		else:
			return self._sync_attendance_direct_zk()

	def _sync_attendance_direct_zk(self):
		"""Sync attendance logs from ZK device and create Access Log records"""
		try:
			conn = self.get_connection()

			if not conn:
				frappe.throw(_("Failed to connect to device"))

			# Get all attendance records
			attendance = conn.get_attendance()

			if not attendance:
				frappe.msgprint(_("No attendance records found"), indicator="orange", alert=True)
				conn.disconnect()
				return

			# Track statistics
			new_logs = 0
			duplicate_logs = 0

			for record in attendance:
				# Check if log already exists
				existing = frappe.db.exists("Access Log", {
					"device": self.name,
					"zk_user_id": str(record.user_id),
					"event_time": record.timestamp
				})

				if existing:
					duplicate_logs += 1
					continue

				# Find member by ZK User ID
				member = frappe.db.get_value("Member", {"zk_user_id": str(record.user_id)}, "name")

				# Create Access Log
				log = frappe.new_doc("Access Log")
				log.device = self.name
				log.zk_user_id = str(record.user_id)
				log.event_time = record.timestamp
				log.event_type = "Check-In" if record.punch == 0 else "Check-Out"

				if member:
					log.member = member

				# Set location from device
				if self.location:
					log.location = self.location

				log.insert(ignore_permissions=True)
				new_logs += 1

			conn.disconnect()

			# Update sync status
			self.last_sync_time = frappe.utils.now()
			self.last_sync_status = 'Success'
			self.last_error = None
			self.save()

			frappe.msgprint(
				_("Sync completed. New logs: {0}, Duplicates: {1}").format(new_logs, duplicate_logs),
				indicator="green",
				alert=True
			)

			return {
				"success": True,
				"new_logs": new_logs,
				"duplicate_logs": duplicate_logs
			}

		except Exception as e:
			error_msg = str(e)
			frappe.log_error(f"Error syncing attendance from device {self.device_name}: {error_msg}", "ZK Sync Error")

			self.last_sync_status = 'Failed'
			self.last_error = error_msg
			self.save()

			frappe.throw(_("Sync failed: {0}").format(error_msg))

	def _sync_attendance_biotime(self):
		"""Sync attendance via BioTime API for this specific device"""
		try:
			# Get BioTime settings
			biotime_settings = frappe.get_doc("BioTime Settings", "BioTime Settings")

			if not biotime_settings.enabled:
				frappe.throw(_("BioTime integration is not enabled. Please configure BioTime Settings."))

			biotime_settings.ensure_token_valid()

			# Fetch attendance for this device only
			url = f"{biotime_settings.get_base_url()}/iclock/api/transactions/"

			# Use last sync time or default to 7 days ago
			from_date = self.last_sync_time.date() if self.last_sync_time else frappe.utils.add_days(frappe.utils.nowdate(), -7)
			to_date = frappe.utils.nowdate()

			params = {
				"start_date": from_date,
				"end_date": to_date,
				"terminal_sn": self.serial_number,  # Filter by this device's serial number
				"page_size": 100,
				"page": 1
			}

			new_logs = 0
			duplicate_logs = 0
			total_fetched = 0

			while True:
				response = frappe.requests.get(url, headers=biotime_settings.get_headers(), params=params, timeout=30)

				if response.status_code != 200:
					error_msg = f"Failed to fetch attendance: {response.status_code}"
					frappe.log_error(error_msg, "BioTime Device Sync Error")
					break

				data = response.json()
				results = data.get("data", [])

				if not results:
					break

				total_fetched += len(results)

				# Process each attendance record
				for record in results:
					created = biotime_settings._create_access_log_from_biotime(record)
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
			self.last_sync_time = frappe.utils.now()
			self.last_sync_status = 'Success'
			self.last_error = None
			self.save()

			frappe.msgprint(
				_("BioTime sync completed. Total: {0}, New: {1}, Duplicates: {2}").format(
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
			frappe.log_error(f"Error syncing attendance via BioTime: {error_msg}", "BioTime Device Sync Error")

			self.last_sync_status = 'Failed'
			self.last_error = error_msg
			self.save()

			frappe.throw(_("BioTime sync failed: {0}").format(error_msg))


# Utility functions for ZK device operations

@frappe.whitelist()
def add_user_to_device(device_name, zk_user_id, name, card_number=None, privilege=0):
	"""Add user to ZK device

	Args:
		device_name: Access Device name
		zk_user_id: User ID (integer)
		name: User name (max 24 chars)
		card_number: Card number (optional)
		privilege: User privilege level (0=User, 14=Admin)

	Returns:
		bool: Success status
	"""
	try:
		device = frappe.get_doc("Access Device", device_name)
		conn = device.get_connection()

		if not conn:
			return False

		# Add user
		conn.set_user(
			uid=int(zk_user_id),
			name=name[:24],
			privilege=int(privilege),
			password='',
			group_id='',
			user_id=str(zk_user_id),
			card=card_number or ''
		)

		conn.disconnect()

		return True

	except Exception as e:
		frappe.log_error(f"Error adding user to device: {str(e)}", "ZK Add User Error")
		return False


@frappe.whitelist()
def remove_user_from_device(device_name, zk_user_id):
	"""Remove user from ZK device

	Args:
		device_name: Access Device name
		zk_user_id: User ID to remove

	Returns:
		bool: Success status
	"""
	try:
		device = frappe.get_doc("Access Device", device_name)
		conn = device.get_connection()

		if not conn:
			return False

		# Delete user
		conn.delete_user(uid=int(zk_user_id))

		conn.disconnect()

		return True

	except Exception as e:
		frappe.log_error(f"Error removing user from device: {str(e)}", "ZK Remove User Error")
		return False


@frappe.whitelist()
def clear_device_attendance(device_name):
	"""Clear all attendance records from ZK device

	Args:
		device_name: Access Device name

	Returns:
		bool: Success status
	"""
	try:
		device = frappe.get_doc("Access Device", device_name)
		conn = device.get_connection()

		if not conn:
			return False

		# Clear attendance data
		conn.clear_attendance()

		conn.disconnect()

		frappe.msgprint(_("Attendance data cleared from device"), indicator="green", alert=True)

		return True

	except Exception as e:
		frappe.log_error(f"Error clearing attendance from device: {str(e)}", "ZK Clear Attendance Error")
		frappe.throw(_("Failed to clear attendance: {0}").format(str(e)))
		return False
