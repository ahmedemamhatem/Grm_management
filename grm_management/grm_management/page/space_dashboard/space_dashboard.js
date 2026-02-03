frappe.pages['space_dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Space Availability Dashboard',
		single_column: false
	});

	new SpaceDashboard(page);
}

class SpaceDashboard {
	constructor(page) {
		this.page = page;
		this.setup_page();
		this.load_dashboard();
	}

	setup_page() {
		// Add date filter
		this.page.add_field({
			fieldname: 'date',
			label: __('Date'),
			fieldtype: 'Date',
			default: frappe.datetime.get_today(),
			change: () => this.load_dashboard()
		});

		// Add location filter
		this.page.add_field({
			fieldname: 'location',
			label: __('Location'),
			fieldtype: 'Link',
			options: 'GRM Location',
			change: () => this.load_dashboard()
		});

		// Add space type filter
		this.page.add_field({
			fieldname: 'space_type',
			label: __('Space Type'),
			fieldtype: 'Link',
			options: 'GRM Space Type',
			change: () => this.load_dashboard()
		});

		// Add refresh button
		this.page.set_primary_action(__('Refresh'), () => {
			this.load_dashboard();
		});

		this.$dashboard = $('<div class="space-dashboard-content">').appendTo(this.page.main);
	}

	load_dashboard() {
		let date = this.page.get_field('date').get_value();
		let location = this.page.get_field('location').get_value();
		let space_type = this.page.get_field('space_type').get_value();

		frappe.call({
			method: 'grm_management.grm_management.page.space_calendar.space_calendar.get_space_availability',
			args: {
				date: date,
				location: location,
				space_type: space_type
			},
			callback: (r) => {
				if (r.message) {
					this.render_dashboard(r.message);
				}
			}
		});
	}

	render_dashboard(spaces) {
		let html = `
			<div class="row">
				<div class="col-md-12">
					<h4>Space Availability for ${this.page.get_field('date').get_value()}</h4>
				</div>
			</div>
			<div class="row" style="margin-top: 20px;">
		`;

		// Group spaces by type
		let grouped = {};
		spaces.forEach(space => {
			if (!grouped[space.space_type]) {
				grouped[space.space_type] = [];
			}
			grouped[space.space_type].push(space);
		});

		// Render each group
		Object.keys(grouped).forEach(type => {
			html += `
				<div class="col-md-12">
					<div class="card" style="margin-bottom: 20px;">
						<div class="card-header">
							<h5>${type}</h5>
						</div>
						<div class="card-body">
							<div class="row">
			`;

			grouped[type].forEach(space => {
				let status_color = space.is_available ? 'success' : 'warning';
				let status_text = space.is_available ? 'Available' : `${space.bookings.length} Booking(s)`;
				let status_class = space.status === 'Rented' ? 'info' : status_color;

				html += `
					<div class="col-md-4 col-sm-6">
						<div class="card space-card" style="margin-bottom: 15px; border-left: 4px solid var(--${status_class});">
							<div class="card-body">
								<div class="d-flex justify-content-between align-items-start">
									<div>
										<h6 class="card-title">${space.space_name}</h6>
										<p class="text-muted mb-1">
											<i class="fa fa-users"></i> Capacity: ${space.capacity}
										</p>
										<p class="text-muted mb-1">
											<i class="fa fa-dollar"></i> ${format_currency(space.hourly_rate)}/hour
										</p>
									</div>
									<div>
										<span class="badge badge-${status_class}">${status_text}</span>
										${space.status === 'Rented' ? '<br><span class="badge badge-info">Rented</span>' : ''}
									</div>
								</div>
				`;

				if (space.bookings.length > 0) {
					html += `
						<div class="mt-2">
							<small class="text-muted">Today's Bookings:</small>
							<ul class="list-unstyled mt-1">
					`;
					space.bookings.forEach(booking => {
						html += `
							<li style="font-size: 12px;">
								<i class="fa fa-clock-o"></i> ${booking.start} - ${booking.end}
								<span class="badge badge-sm badge-${this.get_booking_status_class(booking.status)}">${booking.status}</span>
							</li>
						`;
					});
					html += `
							</ul>
						</div>
					`;
				}

				html += `
								<div class="mt-2">
									<button class="btn btn-sm btn-primary btn-book-space"
										data-space="${space.name}"
										data-space-name="${space.space_name}"
										${!space.is_available ? 'disabled' : ''}>
										<i class="fa fa-calendar"></i> Book Now
									</button>
									<button class="btn btn-sm btn-secondary btn-view-space"
										data-space="${space.name}">
										<i class="fa fa-eye"></i> View
									</button>
								</div>
							</div>
						</div>
					</div>
				`;
			});

			html += `
							</div>
						</div>
					</div>
				</div>
			`;
		});

		html += `</div>`;

		this.$dashboard.html(html);

		// Bind button events
		this.$dashboard.find('.btn-book-space').on('click', (e) => {
			let space = $(e.currentTarget).data('space');
			this.create_booking(space);
		});

		this.$dashboard.find('.btn-view-space').on('click', (e) => {
			let space = $(e.currentTarget).data('space');
			frappe.set_route('Form', 'GRM Space', space);
		});
	}

	get_booking_status_class(status) {
		const classes = {
			'Confirmed': 'primary',
			'Checked-in': 'success',
			'Checked-out': 'secondary',
			'Draft': 'light',
			'Cancelled': 'danger',
			'No-show': 'warning'
		};
		return classes[status] || 'light';
	}

	create_booking(space) {
		let date = this.page.get_field('date').get_value();

		frappe.new_doc('GRM Booking', {
			space: space,
			booking_date: date
		});
	}
}
