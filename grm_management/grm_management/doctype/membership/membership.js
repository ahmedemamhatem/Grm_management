frappe.ui.form.on('Membership', {
    package: function(frm) {
        if (frm.doc.package) {
            frappe.db.get_doc('Package', frm.doc.package).then(pkg => {
                frm.set_value('package_price', pkg.price);
                frm.set_value('access_type', pkg.access_type);
                frm.set_value('meeting_hours_allowed', pkg.meeting_room_hours);
                frm.set_value('guest_passes_allowed', pkg.guest_passes);
                frm.set_value('printing_pages_allowed', (pkg.printing_bw_pages || 0) + (pkg.printing_color_pages || 0));
                if (pkg.access_type == 'Unlimited') {
                    frm.set_value('total_access_allowed', 0);
                    frm.set_value('access_remaining', 0);
                } else {
                    frm.set_value('total_access_allowed', pkg.access_limit_value || 0);
                    frm.set_value('access_remaining', (pkg.access_limit_value || 0) - (frm.doc.access_used || 0) + (frm.doc.rollover_from_previous || 0));
                }
            })
        }
    },
    status: function(frm) {
        if (frm.doc.status === 'Paused') {
            frm.set_df_property('pause_start', 'reqd', 1);
            frm.set_df_property('pause_end', 'reqd', 1);
        } else {
            frm.set_df_property('pause_start', 'reqd', 0);
            frm.set_df_property('pause_end', 'reqd', 0);
        }
    }
});