# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.desk.desktop import Workspace as OriginalWorkspace


def boot_session(bootinfo):
	"""Patch Frappe Workspace bug with onboarding_list"""
	# Monkey patch the get_onboardings method to disable onboarding completely
	def patched_get_onboardings(self):
		"""Disabled onboarding - returns empty list"""
		return []

	# Apply the patch
	OriginalWorkspace.get_onboardings = patched_get_onboardings
