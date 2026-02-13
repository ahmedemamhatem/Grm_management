# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe


def _msg(en, ar):
	"""Return bilingual message dict."""
	return {"en": en, "ar": ar}


@frappe.whitelist(allow_guest=True)
def get_our_customers():
	"""Get clients from the GRM Clients Page, ordered by table row index.

	Returns:
		200: List of clients
		500: Server error
	"""
	try:
		doc = frappe.get_single("GRM Clients Page")

		result = [
			{
				"img": c.client_img,
				"title": c.client_title,
				"url": c.client_url,
			}
			for c in (doc.clients or [])
		]

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Clients retrieved successfully", "تم جلب العملاء بنجاح"),
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
