# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GRMClientsPage(Document):
	def validate(self):
		self.make_files_public()

	def make_files_public(self):
		"""Ensure all attached files are stored in the public directory."""
		for row in (self.clients or []):
			_set_file_public(row.client_img)


def _set_file_public(file_url):
	"""Mark a file as public so it is accessible without login."""
	if not file_url or "/private/" not in str(file_url):
		return
	file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
	if file_name:
		doc = frappe.get_doc("File", file_name)
		doc.is_private = 0
		doc.save(ignore_permissions=True)
