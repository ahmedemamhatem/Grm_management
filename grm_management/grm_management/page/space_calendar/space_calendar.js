frappe.pages['space_calendar'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Space Booking Calendar',
		single_column: true
	});

	new SpaceBookingCalendar(page);
}

class SpaceBookingCalendar {
	constructor(page) {
		this.page = page;
		this.filters = {};
		this.current_date = frappe.datetime.get_today();
		this.current_view = 'week';
		this.setup_page();
		this.load_calendar();
	}

	setup_page() {
		// Add view switcher in menu
		this.page.add_menu_item(__('Week View'), () => {
			this.current_view = 'week';
			this.load_calendar();
		});

		this.page.add_menu_item(__('Day View'), () => {
			this.current_view = 'day';
			this.load_calendar();
		});

		this.page.add_menu_item(__('Month View'), () => {
			this.current_view = 'month';
			this.load_calendar();
		});

		// Add action buttons
		this.page.set_primary_action(__('New Booking'), () => {
			this.create_booking_dialog();
		});

		this.page.add_button(__('Today'), () => {
			this.current_date = frappe.datetime.get_today();
			this.load_calendar();
		});

		this.page.add_button(__('Previous'), () => {
			this.navigate(-1);
		});

		this.page.add_button(__('Next'), () => {
			this.navigate(1);
		});

		this.$calendar = $('<div class="booking-calendar-container">').appendTo(this.page.main);
	}

	navigate(direction) {
		if (this.current_view === 'day') {
			this.current_date = frappe.datetime.add_days(this.current_date, direction);
		} else if (this.current_view === 'week') {
			this.current_date = frappe.datetime.add_days(this.current_date, direction * 7);
		} else {
			this.current_date = frappe.datetime.add_months(this.current_date, direction);
		}
		this.load_calendar();
	}

	get_week_start(date) {
		// Get start of week (Sunday)
		let d = frappe.datetime.str_to_obj(date);
		let day = d.getDay();
		let diff = d.getDate() - day;
		return frappe.datetime.obj_to_str(new Date(d.setDate(diff)));
	}

	get_day_name(date) {
		// Get day name from date (e.g., "Monday", "Tuesday")
		const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
		let d = frappe.datetime.str_to_obj(date);
		return days[d.getDay()];
	}

	load_calendar() {
		let start_date, end_date;

		if (this.current_view === 'day') {
			start_date = end_date = this.current_date;
		} else if (this.current_view === 'week') {
			start_date = this.get_week_start(this.current_date);
			end_date = frappe.datetime.add_days(start_date, 6);
		} else {
			// Month view
			let d = frappe.datetime.str_to_obj(this.current_date);
			start_date = frappe.datetime.obj_to_str(new Date(d.getFullYear(), d.getMonth(), 1));
			end_date = frappe.datetime.obj_to_str(new Date(d.getFullYear(), d.getMonth() + 1, 0));
		}

		frappe.call({
			method: 'grm_management.grm_management.page.space_calendar.space_calendar.get_calendar_data',
			args: {
				start_date: start_date,
				end_date: end_date,
				location: null,
				space_type: null,
				space: null
			},
			callback: (r) => {
				if (r.message) {
					this.render_calendar(r.message, start_date, end_date);
				}
			}
		});
	}

	render_calendar(data, start_date, end_date) {
		let html = `
			<style>
				.booking-calendar-container {
					overflow: auto;
					background: #f5f7fa;
					padding: 0;
					margin: -15px;
					margin-top: 0;
					position: relative;
					z-index: 1;
				}
				.booking-calendar {
					width: 100%;
					border-collapse: collapse;
					margin: 0;
					font-size: 14px;
					background: white;
				}
				.booking-calendar th, .booking-calendar td {
					border: 1px solid #d1d8dd;
					padding: 8px 10px;
					vertical-align: middle;
				}
				.booking-calendar th {
					background: #f8f9fa !important;
					color: #2c3e50 !important;
					font-weight: 600;
					text-align: center;
					position: sticky;
					top: 0;
					z-index: 10;
					padding: 10px 8px;
					font-size: 12px;
					line-height: 1.4;
					border-bottom: 2px solid #2c3e50;
				}
				.booking-calendar .time-column {
					background: #ffffff !important;
					color: #495057 !important;
					font-weight: 600;
					width: 80px;
					text-align: center;
					font-size: 12px;
					position: sticky;
					left: 0;
					z-index: 5;
					padding: 6px;
					border-right: 2px solid #d1d8dd;
				}
				.booking-calendar .space-header {
					background: #f8f9fa !important;
					color: #2c3e50 !important;
					font-weight: 600;
					text-align: center;
					padding: 8px 6px;
					font-size: 12px;
					min-width: 120px;
					max-width: 150px;
					word-wrap: break-word;
					line-height: 1.3;
				}
				.booking-calendar .space-header small {
					font-size: 11px;
					opacity: 0.85;
					display: block;
					margin-top: 3px;
					color: #6c757d;
				}
				.time-slot-cell {
					position: relative;
					height: 35px;
					min-height: 35px;
					cursor: pointer;
					transition: all 0.2s ease;
					background: #fafbfc;
				}
				.time-slot-cell:hover {
					background: #e3f2fd;
				}
				.time-slot-cell.booked {
					background-color: transparent;
					padding: 0;
				}
				.booking-block {
					background: #3498db;
					color: white;
					padding: 8px 10px;
					border-radius: 4px;
					margin: 1px;
					cursor: pointer;
					font-size: 13px;
					box-shadow: 0 1px 3px rgba(0,0,0,0.12);
					border: 1px solid rgba(255,255,255,0.3);
					transition: all 0.2s ease;
					animation: fadeIn 0.3s ease;
				}
				.booking-block:hover {
					transform: translateY(-1px);
					box-shadow: 0 2px 6px rgba(0,0,0,0.2);
				}
				@keyframes fadeIn {
					from { opacity: 0; }
					to { opacity: 1; }
				}
				.booking-block.confirmed {
					background: #2ecc71;
				}
				.booking-block.checkedin {
					background: #27ae60;
				}
				.booking-block.draft {
					background: #95a5a6;
				}
				.booking-block.expired {
					background: #e74c3c;
					animation: blink 1.5s infinite;
				}
				@keyframes blink {
					0%, 100% { opacity: 1; }
					50% { opacity: 0.6; }
				}
				.booking-info {
					font-weight: 600;
					margin-bottom: 3px;
					font-size: 13px;
					white-space: nowrap;
					overflow: hidden;
					text-overflow: ellipsis;
				}
				.booking-time {
					font-size: 12px;
					opacity: 0.9;
				}
				.calendar-header {
					display: none;
				}
				.legend {
					display: none;
				}
				.legend-item {
					display: flex;
					align-items: center;
					gap: 6px;
					padding: 4px 10px;
					font-size: 11px;
				}
				.legend-color {
					width: 16px;
					height: 16px;
					border-radius: 3px;
				}
				.booking-actions-menu {
					position: fixed;
					background: white;
					border-radius: 8px;
					box-shadow: 0 4px 20px rgba(0,0,0,0.2);
					padding: 6px;
					z-index: 1000;
					min-width: 180px;
					animation: menuSlideIn 0.2s ease;
					border: 1px solid #e4e7eb;
				}
				@keyframes menuSlideIn {
					from {
						opacity: 0;
						transform: translateY(-5px);
					}
					to {
						opacity: 1;
						transform: translateY(0);
					}
				}
				.booking-action-item {
					padding: 8px 12px;
					cursor: pointer;
					border-radius: 4px;
					transition: all 0.15s ease;
					font-size: 13px;
					display: flex;
					align-items: center;
					gap: 8px;
					color: #2c3e50;
				}
				.booking-action-item:hover {
					background: #3498db;
					color: white;
				}
				.booking-action-item.danger:hover {
					background: #e74c3c;
					color: white;
				}
			</style>
		`;

		// Calendar title
		html += `<div class="calendar-header">
			${frappe.datetime.str_to_user(start_date)}`;
		if (start_date !== end_date) {
			html += ` - ${frappe.datetime.str_to_user(end_date)}`;
		}
		html += ` (${this.current_view.toUpperCase()} VIEW)</div>`;

		// Legend
		html += `
			<div class="legend">
				<div class="legend-item">
					<div class="legend-color" style="background: #95a5a6;"></div>
					<span>Draft</span>
				</div>
				<div class="legend-item">
					<div class="legend-color" style="background: #2ecc71;"></div>
					<span>Confirmed</span>
				</div>
				<div class="legend-item">
					<div class="legend-color" style="background: #27ae60;"></div>
					<span>Checked-in</span>
				</div>
				<div class="legend-item">
					<div class="legend-color" style="background: #e74c3c;"></div>
					<span>Expired</span>
				</div>
			</div>
		`;

		if (this.current_view === 'week' || this.current_view === 'day') {
			html += this.render_week_view(data, start_date, end_date);
		} else {
			html += this.render_month_view(data, start_date, end_date);
		}

		this.$calendar.html(html);

		// Bind events
		this.$calendar.find('.time-slot-cell').on('click', (e) => {
			let $cell = $(e.currentTarget);
			if (!$cell.hasClass('booked')) {
				this.create_booking_from_slot($cell.data());
			}
		});

		this.$calendar.find('.booking-block').on('click', (e) => {
			e.stopPropagation();
			let booking_id = $(e.currentTarget).data('booking');
			this.show_booking_actions(booking_id, e);
		});
	}

	render_week_view(data, start_date, end_date) {
		if (!data.spaces || data.spaces.length === 0) {
			return '<div class="alert alert-info">No spaces found. Please adjust your filters.</div>';
		}

		let html = '<div style="overflow-x: auto;"><table class="booking-calendar"><thead>';

		// Two-row header: Row 1 = Day names (merged), Row 2 = Space names
		let dates = [];
		let current = start_date;
		while (current <= end_date) {
			dates.push(current);
			current = frappe.datetime.add_days(current, 1);
		}

		// Row 1: Day names (merged columns)
		html += '<tr><th class="time-column" rowspan="2" style="position: sticky; left: 0; z-index: 15;">Time</th>';
		dates.forEach(date => {
			let is_today = date === frappe.datetime.get_today();
			let day_name = is_today ? 'TODAY' : this.get_day_name(date);
			let spaces_count = data.spaces.length;
			html += `<th class="space-header" colspan="${spaces_count}">${day_name}</th>`;
		});
		html += '</tr>';

		// Row 2: Space names
		html += '<tr>';
		dates.forEach(date => {
			data.spaces.forEach(space => {
				let space_display = space.space_name.length > 30 ? space.space_name.substring(0, 27) + '...' : space.space_name;
				html += `<th class="space-header"><small>${space_display}</small></th>`;
			});
		});
		html += '</tr></thead><tbody>';

		// Generate 30-minute time slots (8 AM - 10 PM)
		// Track which cells are occupied by rowspan bookings
		let occupied_cells = {}; // Key: "date_space_slot", Value: true

		for (let hour = 8; hour <= 21; hour++) {
			for (let minute = 0; minute < 60; minute += 30) {
				let time = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
				let time_12hr;
				if (hour > 12) {
					time_12hr = `${hour - 12}:${String(minute).padStart(2, '0')} PM`;
				} else if (hour === 12) {
					time_12hr = `12:${String(minute).padStart(2, '0')} PM`;
				} else {
					time_12hr = `${hour}:${String(minute).padStart(2, '0')} AM`;
				}

				html += `<tr><td class="time-column">${time_12hr}</td>`;

				dates.forEach(date => {
					data.spaces.forEach(space => {
						let cell_key = `${date}_${space.name}_${time}`;

						// Skip if this cell is occupied by a rowspan booking
						if (occupied_cells[cell_key]) {
							return; // Don't render this cell
						}

						// Find bookings that START at this exact time slot
						let bookings = data.bookings.filter(b =>
							b.space === space.name &&
							b.booking_date === date &&
							b.start_time.substr(0, 5) === time
						);

						if (bookings.length > 0) {
							// Render booking with rowspan
							let booking = bookings[0]; // Take first if multiple

							// Calculate duration in 30-minute slots
							let start_parts = booking.start_time.split(':');
							let end_parts = booking.end_time.split(':');
							let start_minutes = parseInt(start_parts[0]) * 60 + parseInt(start_parts[1]);
							let end_minutes = parseInt(end_parts[0]) * 60 + parseInt(end_parts[1]);
							let duration_minutes = end_minutes - start_minutes;
							let duration_hours = duration_minutes / 60;
							let rowspan = Math.ceil(duration_minutes / 30);

							// Mark cells as occupied
							for (let i = 0; i < rowspan; i++) {
								let slot_time_minutes = start_minutes + (i * 30);
								let slot_hour = Math.floor(slot_time_minutes / 60);
								let slot_minute = slot_time_minutes % 60;
								let slot_time = `${String(slot_hour).padStart(2, '0')}:${String(slot_minute).padStart(2, '0')}`;
								occupied_cells[`${date}_${space.name}_${slot_time}`] = true;
							}

							let status_class = booking.status.toLowerCase().replace(/-/g, '');
							if (booking.is_expired) status_class = 'expired';

							html += `<td class="time-slot-cell booked" rowspan="${rowspan}" data-space="${space.name}" data-date="${date}" data-time="${time}">`;
							html += `
								<div class="booking-block ${status_class}" data-booking="${booking.name}" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
									<div class="booking-info">${booking.tenant_name || 'Unknown'}</div>
									<div class="booking-time">${booking.start_time.substr(0,5)} - ${booking.end_time.substr(0,5)}</div>
									<div class="booking-time" style="font-weight: 600; margin-top: 3px;">⏱️ ${duration_hours}h</div>
									${booking.is_expired ? '<div class="booking-time">⏰ EXPIRED</div>' : ''}
								</div>
							`;
							html += '</td>';
						} else {
							// Empty slot - check if any booking covers this time
							let covering_bookings = data.bookings.filter(b =>
								b.space === space.name &&
								b.booking_date === date &&
								b.start_time.substr(0, 5) < time &&
								b.end_time.substr(0, 5) > time
							);

							let cell_class = covering_bookings.length > 0 ? 'time-slot-cell booked' : 'time-slot-cell';
							html += `<td class="${cell_class}" data-space="${space.name}" data-date="${date}" data-time="${time}"></td>`;
						}
					});
				});

				html += '</tr>';
			}
		}

		html += '</tbody></table></div>';
		return html;
	}

	render_month_view(data, start_date, end_date) {
		if (!data.spaces || data.spaces.length === 0) {
			return '<div class="alert alert-info">No spaces found. Please adjust your filters.</div>';
		}

		let html = '<div style="padding: 20px;">';

		data.spaces.forEach(space => {
			html += `
				<div class="card" style="margin-bottom: 20px; border-left: 4px solid #667eea;">
					<div class="card-header" style="background-color: #f8f9fa;">
						<h5 style="margin: 0;">${space.space_name} - ${space.space_type}</h5>
					</div>
					<div class="card-body">
			`;

			let space_bookings = data.bookings.filter(b => b.space === space.name);

			if (space_bookings.length === 0) {
				html += '<p class="text-muted">No bookings this period</p>';
			} else {
				html += '<div class="row">';
				space_bookings.forEach(booking => {
					let status_class = booking.status.toLowerCase().replace(/-/g, '');
					if (booking.is_expired) status_class = 'expired';

					html += `
						<div class="col-md-6 col-lg-4">
							<div class="booking-block ${status_class}" data-booking="${booking.name}" style="margin-bottom: 10px;">
								<div class="booking-info">${booking.tenant_name || 'Unknown'}</div>
								<div class="booking-time">${frappe.datetime.str_to_user(booking.booking_date)}</div>
								<div class="booking-time">${booking.start_time.substr(0,5)} - ${booking.end_time.substr(0,5)}</div>
								${booking.is_expired ? '<div class="booking-time">⏰ EXPIRED</div>' : ''}
							</div>
						</div>
					`;
				});
				html += '</div>';
			}

			html += '</div></div>';
		});

		html += '</div>';
		return html;
	}

	create_booking_from_slot(data) {
		let d = new frappe.ui.Dialog({
			title: __('Create Booking'),
			fields: [
				{fieldtype: 'Link', fieldname: 'space', label: __('Space'), options: 'GRM Space',
					default: data.space, reqd: 1},
				{fieldtype: 'Link', fieldname: 'tenant', label: __('Tenant'), options: 'GRM Tenant', reqd: 1,
					get_query: () => {return {filters: {'status': 'Active'}}}
				},
				{fieldtype: 'Date', fieldname: 'booking_date', label: __('Date'),
					default: data.date, reqd: 1},
				{fieldtype: 'Time', fieldname: 'start_time', label: __('Start Time'),
					default: data.time, reqd: 1},
				{fieldtype: 'Time', fieldname: 'end_time', label: __('End Time'), reqd: 1},
				{fieldtype: 'Select', fieldname: 'booking_type', label: __('Type'),
					options: 'Hourly\nDaily\nMulti-day', default: 'Hourly'},
				{fieldtype: 'Link', fieldname: 'sales_taxes_and_charges_template', label: __('Sales Tax Template'),
					options: 'Sales Taxes and Charges Template'},
				{fieldtype: 'Int', fieldname: 'expiry_days', label: __('Expire in (days)'),
					default: 7, description: __('Booking will expire if not converted to subscription')}
			],
			primary_action_label: __('Create Booking'),
			primary_action: (values) => {
				frappe.call({
					method: 'grm_management.grm_management.page.space_calendar.space_calendar.create_booking',
					args: values,
					callback: (r) => {
						if (r.message) {
							frappe.show_alert({message: __('Booking created successfully'), indicator: 'green'});
							d.hide();
							this.load_calendar();
						}
					}
				});
			}
		});
		d.show();
	}

	create_booking_dialog() {
		this.create_booking_from_slot({
			date: this.current_date
		});
	}

	show_booking_actions(booking_id, event) {
		// Remove any existing menu
		$('.booking-actions-menu').remove();

		frappe.call({
			method: 'frappe.client.get',
			args: {
				doctype: 'GRM Booking',
				name: booking_id
			},
			callback: (r) => {
				if (r.message) {
					let booking = r.message;

					// Create custom action menu
					let menu_html = '<div class="booking-actions-menu">';

					// View Details
					menu_html += `
						<div class="booking-action-item" data-action="view" data-booking="${booking_id}">
							<i class="fa fa-eye"></i> ${__('View Details')}
						</div>
					`;

					// Update Booking (if not cancelled or checked-out)
					if (booking.status !== 'Cancelled' && booking.status !== 'Checked-out') {
						menu_html += `
							<div class="booking-action-item" data-action="update" data-booking="${booking_id}">
								<i class="fa fa-edit"></i> ${__('Update Booking')}
							</div>
						`;
					}

					// Convert to Subscription (if not cancelled or checked-out)
					if (booking.status !== 'Cancelled' && booking.status !== 'Checked-out') {
						menu_html += `
							<div class="booking-action-item" data-action="convert" data-booking="${booking_id}">
								<i class="fa fa-refresh"></i> ${__('Convert to Subscription')}
							</div>
						`;
					}

					// Cancel Booking (if draft or confirmed)
					if (booking.status === 'Draft' || booking.status === 'Confirmed') {
						menu_html += `
							<div class="booking-action-item danger" data-action="cancel" data-booking="${booking_id}">
								<i class="fa fa-times"></i> ${__('Cancel Booking')}
							</div>
						`;
					}

					menu_html += '</div>';

					// Position menu near click
					let $menu = $(menu_html);
					$('body').append($menu);

					let offset = $(event.currentTarget).offset();
					$menu.css({
						top: event.pageY + 'px',
						left: event.pageX + 'px'
					});

					// Bind action handlers
					$menu.find('.booking-action-item').on('click', (e) => {
						let action = $(e.currentTarget).data('action');
						let booking_id = $(e.currentTarget).data('booking');

						$menu.remove();

						if (action === 'view') {
							frappe.set_route('Form', 'GRM Booking', booking_id);
						} else if (action === 'update') {
							this.update_booking(booking);
						} else if (action === 'convert') {
							this.convert_to_subscription(booking);
						} else if (action === 'cancel') {
							this.cancel_booking(booking_id);
						}
					});

					// Close menu on outside click
					setTimeout(() => {
						$(document).on('click.booking-menu', (e) => {
							if (!$(e.target).closest('.booking-actions-menu').length) {
								$menu.remove();
								$(document).off('click.booking-menu');
							}
						});
					}, 100);
				}
			}
		});
	}

	update_booking(booking) {
		let d = new frappe.ui.Dialog({
			title: __('Update Booking'),
			fields: [
				{fieldtype: 'Link', fieldname: 'space', label: __('Space'), options: 'GRM Space',
					default: booking.space, reqd: 1},
				{fieldtype: 'Link', fieldname: 'tenant', label: __('Tenant'), options: 'GRM Tenant',
					default: booking.tenant, reqd: 1,
					get_query: () => {return {filters: {'status': 'Active'}}}
				},
				{fieldtype: 'Date', fieldname: 'booking_date', label: __('Date'),
					default: booking.booking_date, reqd: 1},
				{fieldtype: 'Time', fieldname: 'start_time', label: __('Start Time'),
					default: booking.start_time, reqd: 1},
				{fieldtype: 'Time', fieldname: 'end_time', label: __('End Time'),
					default: booking.end_time, reqd: 1},
				{fieldtype: 'Select', fieldname: 'booking_type', label: __('Type'),
					options: 'Hourly\nDaily\nMulti-day', default: booking.booking_type},
				{fieldtype: 'Select', fieldname: 'status', label: __('Status'),
					options: 'Draft\nConfirmed\nChecked-in\nChecked-out\nCancelled\nNo-show',
					default: booking.status}
			],
			primary_action_label: __('Update'),
			primary_action: (values) => {
				frappe.call({
					method: 'frappe.client.set_value',
					args: {
						doctype: 'GRM Booking',
						name: booking.name,
						fieldname: values
					},
					callback: (r) => {
						if (r.message) {
							frappe.show_alert({message: __('Booking updated successfully'), indicator: 'green'});
							d.hide();
							this.load_calendar();
						}
					}
				});
			}
		});
		d.show();
	}

	convert_to_subscription(booking) {
		let d = new frappe.ui.Dialog({
			title: __('Convert Booking to Subscription + Invoice + Payment'),
			fields: [
				{fieldtype: 'Link', fieldname: 'tenant', label: __('Tenant'), options: 'GRM Tenant', reqd: 1,
					default: booking.tenant,
					get_query: () => {
						return {filters: {'status': 'Active'}}
					}
				},
				{fieldtype: 'Select', fieldname: 'subscription_type', label: __('Subscription Type'),
					options: 'Hourly\nDaily\nMonthly\nAnnual', default: 'Monthly', reqd: 1},
				{fieldtype: 'Date', fieldname: 'start_date', label: __('Start Date'), default: frappe.datetime.get_today(), reqd: 1},
				{fieldtype: 'Date', fieldname: 'end_date', label: __('End Date'), reqd: 1},
				{fieldtype: 'Section Break'},
				{fieldtype: 'HTML', options: '<p class="text-muted">This will create a subscription, generate an invoice, and record payment automatically.</p>'}
			],
			primary_action_label: __('Create Subscription + Invoice + Payment'),
			primary_action: (values) => {
				frappe.call({
					method: 'grm_management.grm_management.page.space_calendar.space_calendar.convert_booking_to_subscription',
					args: {
						booking_id: booking.name,
						tenant: values.tenant,
						subscription_type: values.subscription_type,
						start_date: values.start_date,
						end_date: values.end_date
					},
					callback: (r) => {
						if (r.message) {
							let msg = `<div>
								<p><b>Subscription:</b> ${r.message.subscription}</p>
								<p><b>Invoice:</b> ${r.message.invoice}</p>
								<p><b>Payment:</b> ${r.message.payment}</p>
							</div>`;
							frappe.msgprint({
								title: __('Conversion Successful'),
								message: msg,
								indicator: 'green'
							});
							d.hide();
							this.load_calendar();
							// Navigate to subscription
							frappe.set_route('Form', 'GRM Subscription', r.message.subscription);
						}
					}
				});
			}
		});
		d.show();
	}

	cancel_booking(booking_id) {
		frappe.confirm(__('Are you sure you want to cancel this booking?'), () => {
			frappe.call({
				method: 'frappe.client.set_value',
				args: {
					doctype: 'GRM Booking',
					name: booking_id,
					fieldname: 'status',
					value: 'Cancelled'
				},
				callback: () => {
					frappe.show_alert({message: __('Booking cancelled'), indicator: 'orange'});
					this.load_calendar();
				}
			});
		});
	}
}
