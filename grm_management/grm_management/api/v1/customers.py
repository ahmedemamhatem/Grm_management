# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url, cstr


def _msg(en, ar):
	"""Return bilingual message dict."""
	return {"en": en, "ar": ar}


def _get_full_image_url(image_path):
	"""Convert relative image path to full URL."""
	if not image_path:
		return None
	if image_path.startswith("http://") or image_path.startswith("https://"):
		return image_path
	site_url = get_url()
	if image_path.startswith("/"):
		return f"{site_url}{image_path}"
	return f"{site_url}/{image_path}"


@frappe.whitelist(allow_guest=True)
def get_our_customers():
	"""Get customers marked to show on the website.

	This endpoint is publicly accessible (no authentication required).
	Returns customers that have the 'Show in Website' checkbox enabled,
	with their logo images and descriptions.

	Returns:
		200: List of featured customers
		500: Server error

	Example Response:
		{
			"success": true,
			"data": [
				{
					"name": "CUST-0001",
					"customer_name": "Acme Corp",
					"logo": "https://example.com/files/acme-logo.png",
					"description": "Leading technology company",
					"description_ar": "شركة تقنية رائدة",
					"display_order": 1
				}
			],
			"total": 1
		}
	"""
	try:
		customers = frappe.get_all(
			"Customer",
			filters={
				"show_in_website": 1,
				"disabled": 0,
			},
			fields=[
				"name",
				"customer_name",
				"customer_logo",
				"customer_description",
				"customer_description_ar",
				"display_order",
			],
			order_by="display_order asc, customer_name asc",
		)

		result = []
		for c in customers:
			result.append({
				"name": c.get("name"),
				"customer_name": c.get("customer_name"),
				"logo": _get_full_image_url(c.get("customer_logo")),
				"description": c.get("customer_description") or "",
				"description_ar": c.get("customer_description_ar") or "",
				"display_order": c.get("display_order") or 0,
			})

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Customers retrieved successfully", "تم جلب العملاء بنجاح"),
			"data": result,
			"total": len(result),
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Customers API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}
