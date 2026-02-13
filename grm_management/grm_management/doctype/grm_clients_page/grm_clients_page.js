// Copyright (c) 2026, Wael ELsafty and contributors
// For license information, please see license.txt

frappe.ui.form.on("GRM Clients Page", {
	refresh(frm) {
		frm.add_custom_button(
			__("Reorder Clients | ترتيب العملاء"),
			function () {
				show_reorder_dialog(frm);
			}
		);
	},
});

function show_reorder_dialog(frm) {
	const clients = (frm.doc.clients || []).slice().sort(
		(a, b) => a.idx - b.idx
	);

	if (!clients.length) {
		frappe.msgprint(__("No clients to reorder | لا يوجد عملاء للترتيب"));
		return;
	}

	const dialog = new frappe.ui.Dialog({
		title: __("Drag & Drop to Reorder Clients | اسحب وأفلت لترتيب العملاء"),
		size: "extra-large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "reorder_area",
			},
		],
		primary_action_label: __("Apply Order | تطبيق الترتيب"),
		primary_action() {
			const cards = dialog.$wrapper.find(".reorder-card");
			const new_order = [];
			cards.each(function (index) {
				new_order.push($(this).attr("data-name"));
			});

			// Reorder the child table rows to match the new card order
			const rows_by_name = {};
			(frm.doc.clients || []).forEach((r) => {
				rows_by_name[r.name] = r;
			});

			new_order.forEach((name, i) => {
				if (rows_by_name[name]) {
					rows_by_name[name].idx = i + 1;
				}
			});

			frm.doc.clients.sort((a, b) => a.idx - b.idx);
			frm.dirty();
			frm.refresh_fields();
			dialog.hide();
			frm.save().then(() => {
				frappe.show_alert({
					message: __("Order saved successfully. | تم حفظ الترتيب بنجاح."),
					indicator: "green",
				});
			});
		},
	});

	const wrapper = dialog.fields_dict.reorder_area.$wrapper;
	wrapper.html("");

	const grid = $(`<div class="reorder-grid"></div>`);

	clients.forEach(function (c, idx) {
		const card = $(`
			<div class="reorder-card" data-name="${c.name}">
				<div class="reorder-card-handle">
					<span class="drag-handle">&#9776;</span>
					<span class="reorder-index">${idx + 1}</span>
				</div>
				<div class="reorder-card-img">
					${
						c.client_img
							? `<img src="${c.client_img}" alt="${c.client_title || ""}" />`
							: `<div class="reorder-card-placeholder">No Image</div>`
					}
				</div>
				<div class="reorder-card-title">${c.client_title || "—"}</div>
			</div>
		`);
		grid.append(card);
	});

	wrapper.append(grid);

	new Sortable(grid[0], {
		animation: 250,
		handle: ".reorder-card",
		ghostClass: "sortable-ghost",
		chosenClass: "sortable-chosen",
		dragClass: "sortable-drag",
		onEnd() {
			grid.find(".reorder-card").each(function (i) {
				$(this).find(".reorder-index").text(i + 1);
			});
		},
	});

	wrapper.append(`
		<style>
			.reorder-grid {
				display: grid;
				grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
				gap: 12px;
				padding: 8px 0;
			}
			.reorder-card {
				background: var(--fg-color);
				border: 1px solid var(--border-color);
				border-radius: 10px;
				padding: 12px;
				cursor: grab;
				user-select: none;
				transition: box-shadow 0.2s, transform 0.2s;
				display: flex;
				flex-direction: column;
				align-items: center;
				text-align: center;
			}
			.reorder-card:hover {
				box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
				transform: translateY(-2px);
			}
			.reorder-card:active {
				cursor: grabbing;
			}
			.reorder-card-handle {
				display: flex;
				align-items: center;
				justify-content: space-between;
				width: 100%;
				margin-bottom: 10px;
				font-size: 13px;
				color: var(--text-muted);
			}
			.reorder-card-handle .drag-handle {
				font-size: 16px;
			}
			.reorder-card-handle .reorder-index {
				background: var(--bg-color);
				border-radius: 50%;
				width: 24px;
				height: 24px;
				display: inline-flex;
				align-items: center;
				justify-content: center;
				font-weight: 700;
				font-size: 11px;
			}
			.reorder-card-img {
				width: 100px;
				height: 100px;
				display: flex;
				align-items: center;
				justify-content: center;
				margin-bottom: 10px;
			}
			.reorder-card-img img {
				max-width: 100%;
				max-height: 100%;
				object-fit: contain;
				border-radius: 6px;
			}
			.reorder-card-placeholder {
				width: 100%;
				height: 100%;
				background: var(--bg-color);
				border-radius: 6px;
				display: flex;
				align-items: center;
				justify-content: center;
				color: var(--text-muted);
				font-size: 12px;
			}
			.reorder-card-title {
				font-weight: 600;
				font-size: 13px;
				color: var(--text-color);
				line-height: 1.3;
				word-break: break-word;
			}
			.sortable-ghost {
				opacity: 0.3;
			}
			.sortable-chosen {
				box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
				transform: scale(1.05);
			}
			.sortable-drag {
				opacity: 0.9;
			}
		</style>
	`);

	dialog.show();
}
