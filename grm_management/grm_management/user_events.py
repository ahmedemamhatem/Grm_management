# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_user_update(doc, method):
	"""Create GRM Tenant for website users when they sign up or are created

	This hook is triggered after a User document is saved.
	It creates a GRM Tenant record for website users who don't have one yet.
	"""
	# Skip if the signup endpoint already created the tenant
	if getattr(doc.flags, "ignore_tenant_creation", False):
		return

	# Only process for enabled users
	if not doc.enabled:
		return

	# Skip for system users (Administrator, Guest)
	if doc.name in ["Administrator", "Guest"]:
		return

	# Check if user has Website User role (website signup)
	has_website_role = any(
		role.role in ["Website User", "Customer"]
		for role in doc.roles
	)

	if not has_website_role:
		return

	# Check if tenant already exists for this user
	existing_tenant = frappe.db.exists("GRM Tenant", {"primary_email": doc.email})
	if existing_tenant:
		return

	# Also check by user link if there's a user field
	# For now, we'll link by email

	try:
		create_tenant_for_user(doc)
	except Exception as e:
		frappe.log_error(
			f"Error creating tenant for user {doc.email}: {str(e)}",
			"GRM Tenant Auto-Creation Error"
		)


def create_tenant_for_user(user_doc):
	"""Create a GRM Tenant record for a website user

	Args:
		user_doc: The User document

	Returns:
		str: The name of the created GRM Tenant
	"""
	# Determine tenant name
	tenant_name = user_doc.full_name or user_doc.first_name or user_doc.email.split("@")[0]

	# Create tenant
	tenant = frappe.new_doc("GRM Tenant")
	tenant.tenant_name = tenant_name
	tenant.tenant_type = "Individual"
	tenant.status = "Active"
	tenant.primary_contact_person = tenant_name
	tenant.primary_email = user_doc.email
	tenant.primary_phone = user_doc.mobile_no or user_doc.phone

	# Insert with ignore_permissions to allow creation during signup
	tenant.insert(ignore_permissions=True)

	frappe.db.commit()

	frappe.msgprint(
		_("Welcome! Your tenant account has been created: {0}").format(tenant.name),
		alert=True
	)

	return tenant.name


def get_tenant_for_user(user=None):
	"""Get the GRM Tenant linked to a user

	Args:
		user: User email (optional, defaults to current user)

	Returns:
		str: GRM Tenant name or None
	"""
	if not user:
		user = frappe.session.user

	if user in ["Administrator", "Guest"]:
		return None

	# Get user email
	user_email = frappe.db.get_value("User", user, "email") or user

	# Find tenant by email
	tenant = frappe.db.get_value("GRM Tenant", {"primary_email": user_email}, "name")

	return tenant


@frappe.whitelist()
def ensure_tenant_exists():
	"""Ensure current logged-in user has a tenant record

	Creates one if it doesn't exist.

	Returns:
		dict: Tenant info or error message
	"""
	user = frappe.session.user

	if user in ["Administrator", "Guest"]:
		return {"success": False, "message": "System users don't need tenant accounts"}

	# Check if tenant exists
	tenant = get_tenant_for_user(user)

	if tenant:
		tenant_doc = frappe.get_doc("GRM Tenant", tenant)
		return {
			"success": True,
			"tenant": tenant,
			"tenant_name": tenant_doc.tenant_name,
			"exists": True
		}

	# Create tenant for user
	try:
		user_doc = frappe.get_doc("User", user)
		tenant_name = create_tenant_for_user(user_doc)
		tenant_doc = frappe.get_doc("GRM Tenant", tenant_name)

		return {
			"success": True,
			"tenant": tenant_name,
			"tenant_name": tenant_doc.tenant_name,
			"exists": False,
			"message": "Tenant created successfully"
		}
	except Exception as e:
		frappe.log_error(f"Error creating tenant: {str(e)}", "Tenant Creation Error")
		return {
			"success": False,
			"message": str(e)
		}
