# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

"""
Hijri Calendar Utilities for KSA
Converts Gregorian dates to Hijri (Islamic) dates
"""

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate
from datetime import date

# Hijri month names in Arabic and English
HIJRI_MONTHS_AR = [
	"محرم", "صفر", "ربيع الأول", "ربيع الثاني", "جمادى الأولى", "جمادى الآخرة",
	"رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
]

HIJRI_MONTHS_EN = [
	"Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani", "Jumada al-Ula", "Jumada al-Akhirah",
	"Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
]

def gregorian_to_hijri(greg_date):
	"""
	Convert Gregorian date to Hijri date
	Uses a simplified approximation algorithm

	Args:
		greg_date: Date object or date string

	Returns:
		dict: {'year': int, 'month': int, 'day': int, 'formatted': str, 'formatted_ar': str}
	"""
	if isinstance(greg_date, str):
		greg_date = getdate(greg_date)

	if not isinstance(greg_date, date):
		return None

	# Convert to Julian Day Number
	a = (14 - greg_date.month) // 12
	y = greg_date.year + 4800 - a
	m = greg_date.month + 12 * a - 3
	jdn = greg_date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

	# Convert JDN to Hijri
	# Islamic calendar epoch in JDN
	islamic_epoch = 1948440

	l = jdn - islamic_epoch + 10632
	n = (l - 1) // 10631
	l = l - 10631 * n + 354
	j = ((10985 - l) // 5316) * ((50 * l) // 17719) + (l // 5670) * ((43 * l) // 15238)
	l = l - ((30 - j) // 15) * ((17719 * j) // 50) - (j // 16) * ((15238 * j) // 43) + 29
	m = (24 * l) // 709
	d = l - (709 * m) // 24
	y = 30 * n + j - 30

	hijri_year = int(y)
	hijri_month = int(m)
	hijri_day = int(d)

	# Format the date
	formatted = f"{hijri_day} {HIJRI_MONTHS_EN[hijri_month - 1]} {hijri_year} هـ"
	formatted_ar = f"{hijri_day} {HIJRI_MONTHS_AR[hijri_month - 1]} {hijri_year} هـ"

	return {
		'year': hijri_year,
		'month': hijri_month,
		'day': hijri_day,
		'formatted': formatted,
		'formatted_ar': formatted_ar
	}

@frappe.whitelist()
def get_hijri_date(gregorian_date):
	"""
	Whitelisted method to get Hijri date from Gregorian date

	Args:
		gregorian_date: Date string in YYYY-MM-DD format

	Returns:
		dict: Hijri date information
	"""
	try:
		return gregorian_to_hijri(gregorian_date)
	except Exception as e:
		frappe.log_error(f"Error converting to Hijri: {str(e)}")
		return None

def format_dual_date(greg_date, show_hijri=True):
	"""
	Format a date showing both Gregorian and Hijri calendars

	Args:
		greg_date: Gregorian date
		show_hijri: Whether to show Hijri date

	Returns:
		str: Formatted dual date string
	"""
	if not greg_date:
		return ""

	greg_formatted = frappe.utils.formatdate(greg_date, "dd/MM/yyyy")

	if not show_hijri:
		return greg_formatted

	hijri = gregorian_to_hijri(greg_date)
	if hijri:
		return f"{greg_formatted} ({hijri['formatted_ar']})"

	return greg_formatted
