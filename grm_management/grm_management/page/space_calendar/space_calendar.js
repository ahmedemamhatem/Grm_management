frappe.pages['space_calendar'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Space Calendar',
		single_column: true
	});

	new SpaceCalendar(page);
}

class SpaceCalendar {
	constructor(page) {
		this.page = page;
		this.calendar = null;
		this.setup_page();
		this.make_calendar();
	}

	setup_page() {
		// Add filter for location
		this.page.add_field({
			fieldname: 'location',
			label: __('Location'),
			fieldtype: 'Link',
			options: 'GRM Location',
			change: () => this.refresh_calendar()
		});

		// Add filter for space type
		this.page.add_field({
			fieldname: 'space_type',
			label: __('Space Type'),
			fieldtype: 'Link',
			options: 'GRM Space Type',
			change: () => this.refresh_calendar()
		});

		// Add filter for space
		this.page.add_field({
			fieldname: 'space',
			label: __('Space'),
			fieldtype: 'Link',
			options: 'GRM Space',
			change: () => this.refresh_calendar()
		});

		// Add view switcher
		this.page.add_field({
			fieldname: 'view_type',
			label: __('View'),
			fieldtype: 'Select',
			options: ['Month', 'Week', 'Day', 'List'],
			default: 'Week',
			change: () => this.change_view()
		});

		// Add refresh button
		this.page.set_primary_action(__('New Booking'), () => {
			frappe.new_doc('GRM Booking');
		});

		this.page.add_button(__('Refresh'), () => {
			this.refresh_calendar();
		});
	}

	make_calendar() {
		this.$calendar = $('<div class="grm-space-calendar">').appendTo(this.page.main);

		this.$calendar.fullCalendar({
			header: {
				left: 'prev,next today',
				center: 'title',
				right: 'month,agendaWeek,agendaDay,listWeek'
			},
			defaultView: 'agendaWeek',
			editable: false,
			selectable: true,
			selectHelper: true,
			allDaySlot: false,
			slotDuration: '00:30:00',
			minTime: '06:00:00',
			maxTime: '22:00:00',
			businessHours: {
				dow: [0, 1, 2, 3, 4, 5, 6],
				start: '08:00',
				end: '20:00'
			},
			eventLimit: true,
			events: (start, end, timezone, callback) => {
				this.get_events(start, end, callback);
			},
			select: (start, end) => {
				this.create_booking(start, end);
			},
			eventClick: (event) => {
				frappe.set_route('Form', 'GRM Booking', event.id);
			},
			eventRender: (event, element) => {
				element.find('.fc-title').html(event.title);
				element.attr('title', event.description);
			}
		});
	}

	get_events(start, end, callback) {
		let filters = {
			booking_date: ['between', [
				moment(start).format('YYYY-MM-DD'),
				moment(end).format('YYYY-MM-DD')
			]]
		};

		// Apply additional filters
		let location = this.page.get_field('location').get_value();
		let space_type = this.page.get_field('space_type').get_value();
		let space = this.page.get_field('space').get_value();

		if (space) {
			filters.space = space;
		}

		frappe.call({
			method: 'grm_management.grm_management.page.space_calendar.space_calendar.get_bookings',
			args: {
				start: moment(start).format('YYYY-MM-DD'),
				end: moment(end).format('YYYY-MM-DD'),
				location: location,
				space_type: space_type,
				space: space
			},
			callback: (r) => {
				if (r.message) {
					let events = r.message.map(booking => {
						return {
							id: booking.name,
							title: `${booking.space_name} - ${booking.member_name}`,
							start: `${booking.booking_date}T${booking.start_time}`,
							end: `${booking.booking_date}T${booking.end_time}`,
							color: this.get_status_color(booking.status),
							description: `
								<strong>${booking.space_name}</strong><br>
								Member: ${booking.member_name}<br>
								Status: ${booking.status}<br>
								Duration: ${booking.duration_hours} hours<br>
								Amount: ${format_currency(booking.total_amount)}
							`
						};
					});
					callback(events);
				}
			}
		});
	}

	get_status_color(status) {
		const colors = {
			'Draft': '#9e9e9e',
			'Confirmed': '#2196f3',
			'Checked-in': '#4caf50',
			'Checked-out': '#607d8b',
			'No-show': '#ff9800',
			'Cancelled': '#f44336'
		};
		return colors[status] || '#9e9e9e';
	}

	create_booking(start, end) {
		let space = this.page.get_field('space').get_value();

		let booking = frappe.model.get_new_doc('GRM Booking');
		booking.booking_date = moment(start).format('YYYY-MM-DD');
		booking.start_time = moment(start).format('HH:mm:ss');
		booking.end_time = moment(end).format('HH:mm:ss');

		if (space) {
			booking.space = space;
		}

		frappe.set_route('Form', 'GRM Booking', booking.name);
	}

	refresh_calendar() {
		this.$calendar.fullCalendar('refetchEvents');
	}

	change_view() {
		let view_type = this.page.get_field('view_type').get_value();
		let view_map = {
			'Month': 'month',
			'Week': 'agendaWeek',
			'Day': 'agendaDay',
			'List': 'listWeek'
		};
		this.$calendar.fullCalendar('changeView', view_map[view_type]);
	}
}
