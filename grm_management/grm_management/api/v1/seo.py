# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cstr, strip_html


def _msg(en, ar):
    """Return bilingual message dict."""
    return {"en": en, "ar": ar}


# Default SEO data for known pages (fallback when no doctype is configured)
DEFAULT_SEO = {
    "home": {
        "title": "GRM - Workspace Solutions",
        "title_ar": "GRM - حلول مساحات العمل",
        "description": "Find and book premium workspaces, private offices, meeting rooms, and co-working spaces.",
        "description_ar": "ابحث واحجز مساحات العمل المميزة، المكاتب الخاصة، قاعات الاجتماعات، ومساحات العمل المشتركة.",
        "keywords": "workspace, coworking, office, meeting room, booking",
        "keywords_ar": "مساحة عمل, عمل مشترك, مكتب, قاعة اجتماعات, حجز",
    },
    "spaces": {
        "title": "Browse Spaces",
        "title_ar": "تصفح المساحات",
        "description": "Explore available workspaces and book the perfect space for your needs.",
        "description_ar": "استكشف مساحات العمل المتاحة واحجز المساحة المثالية لاحتياجاتك.",
        "keywords": "spaces, offices, meeting rooms, coworking, available spaces",
        "keywords_ar": "مساحات, مكاتب, قاعات اجتماعات, عمل مشترك, مساحات متاحة",
    },
    "booking": {
        "title": "My Bookings",
        "title_ar": "حجوزاتي",
        "description": "View and manage your workspace bookings.",
        "description_ar": "عرض وإدارة حجوزات مساحات العمل الخاصة بك.",
        "keywords": "bookings, reservations, my bookings",
        "keywords_ar": "حجوزات, حجز, حجوزاتي",
    },
    "login": {
        "title": "Login",
        "title_ar": "تسجيل الدخول",
        "description": "Log in to your account to manage bookings and spaces.",
        "description_ar": "سجل دخولك لإدارة الحجوزات والمساحات.",
        "keywords": "login, sign in, account",
        "keywords_ar": "تسجيل دخول, حساب",
    },
    "signup": {
        "title": "Create Account",
        "title_ar": "إنشاء حساب",
        "description": "Create your account and start booking workspaces today.",
        "description_ar": "أنشئ حسابك وابدأ حجز مساحات العمل اليوم.",
        "keywords": "signup, register, create account",
        "keywords_ar": "تسجيل, إنشاء حساب, حساب جديد",
    },
    "profile": {
        "title": "My Profile",
        "title_ar": "ملفي الشخصي",
        "description": "Manage your profile settings and account information.",
        "description_ar": "إدارة إعدادات ملفك الشخصي ومعلومات حسابك.",
        "keywords": "profile, account, settings",
        "keywords_ar": "ملف شخصي, حساب, إعدادات",
    },
    "contact": {
        "title": "Contact Us",
        "title_ar": "تواصل معنا",
        "description": "Get in touch with our team for support and inquiries.",
        "description_ar": "تواصل مع فريقنا للدعم والاستفسارات.",
        "keywords": "contact, support, help",
        "keywords_ar": "تواصل, دعم, مساعدة",
    },
    "about": {
        "title": "About Us",
        "title_ar": "من نحن",
        "description": "Learn more about GRM and our workspace solutions.",
        "description_ar": "تعرف على المزيد عن GRM وحلول مساحات العمل لدينا.",
        "keywords": "about, company, workspace provider",
        "keywords_ar": "من نحن, شركة, مزود مساحات عمل",
    },
}


@frappe.whitelist(allow_guest=True)
def get_seo(page=None):
    """Get SEO metadata for a specific page.

    Args:
        page: Page slug (e.g. "home", "spaces", "login", "signup", "booking", "profile")

    Returns:
        200: SEO data for the page
        400: Missing page parameter
        404: Page not found
    """
    try:
        if not page:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Page parameter is required", "معامل الصفحة مطلوب"),
            }

        page = cstr(strip_html(cstr(page))).strip().lower()[:50]

        # Check if a GRM SEO Meta doctype exists (admin-configurable override)
        seo_data = None
        if frappe.db.exists("DocType", "GRM SEO Meta"):
            seo_data = frappe.db.get_value(
                "GRM SEO Meta",
                {"page_slug": page},
                [
                    "title", "title_ar",
                    "description", "description_ar",
                    "keywords", "keywords_ar",
                ],
                as_dict=True,
            )

        # Fallback to defaults
        if not seo_data:
            seo_data = DEFAULT_SEO.get(page)

        if not seo_data:
            frappe.response["http_status_code"] = 404
            return {
                "success": False,
                "http_status_code": 404,
                "message": _msg(
                    "No SEO data found for the specified page",
                    "لم يتم العثور على بيانات SEO للصفحة المحددة"
                ),
            }

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("SEO data retrieved successfully", "تم جلب بيانات SEO بنجاح"),
            "data": {
                "page": page,
                "title": seo_data.get("title", ""),
                "title_ar": seo_data.get("title_ar", ""),
                "description": seo_data.get("description", ""),
                "description_ar": seo_data.get("description_ar", ""),
                "keywords": seo_data.get("keywords", ""),
                "keywords_ar": seo_data.get("keywords_ar", ""),
            },
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "SEO API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


@frappe.whitelist(allow_guest=True)
def get_all_seo():
    """Get SEO metadata for all pages at once.

    Useful for SSR / preloading all meta in one call.

    Returns:
        200: Dict of all pages with their SEO data
    """
    try:
        result = {}

        # Load from doctype if exists
        if frappe.db.exists("DocType", "GRM SEO Meta"):
            records = frappe.get_all(
                "GRM SEO Meta",
                fields=["page_slug", "title", "title_ar", "description", "description_ar", "keywords", "keywords_ar"],
            )
            for r in records:
                result[r.page_slug] = {
                    "title": r.title,
                    "title_ar": r.title_ar,
                    "description": r.description,
                    "description_ar": r.description_ar,
                    "keywords": r.keywords,
                    "keywords_ar": r.keywords_ar,
                }

        # Fill missing pages with defaults
        for page, data in DEFAULT_SEO.items():
            if page not in result:
                result[page] = data

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("All SEO data retrieved successfully", "تم جلب جميع بيانات SEO بنجاح"),
            "data": result,
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "SEO API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }
