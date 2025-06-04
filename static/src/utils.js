export function ToastError(message) {
    $("#error-toast .toast-body").html(message);
    $("#error-toast").toast("show");
}
export function ToastSuccess(message) {
    $("#confirm-toast .toast-body").html(message);
    $("#confirm-toast").toast("show");
}
export function destroyTable(table) {
    if ($.fn.DataTable.isDataTable(table)) {
        $(table).DataTable().destroy();
    }
}
export function updateClearAllFiltersButton() {
    if ($('#active-filters .badge').length > 0) {
        $('#clear-all-filters').removeClass('d-none');
    }
    else {
        $('#clear-all-filters').addClass('d-none');
    }
}
export function setupTableFilters(table_name, exceptions) {
    const table = $(table_name).DataTable();
    table.on("xhr", function () {
        const data = table.ajax.json();
        const columns = table.settings().init().columns;
        const $filterMenu = $("#filter-dropdown");
        $filterMenu.empty();
        columns.forEach((col, colIdx) => {
            if (!col.data || (exceptions && exceptions.includes(colIdx)))
                return;
            const values = Array.from(new Set(data.map(row => {
                const raw = row[col.data.toString()];
                if (raw == null)
                    return;
                if (col.render) {
                    // @ts-expect-error This works...idk why typescript has issues with it
                    const render = col.render(raw, 'display', row).toString();
                    return render.split(",")[0];
                }
                return raw.split(",")[0];
            }).filter(v => v != null && v !== "")));
            values.sort((a, b) => a.localeCompare(b, undefined, { numberic: true, sensitivity: 'base' }));
            if (values.length == 0)
                return;
            const subMenuID = `submenu-${colIdx}`;
            const subMenu = `
                    <li class="drowdown-submenu">
                        <div class="dropdown-item">${col.title} &raquo;</div>
                        <ul class="dropdown-menu dropdown-submenu" id=${subMenuID}>
                            ${values.map(val => `<li><div class="dropdown-item filter-option" data-col="${colIdx}" data-value="${val}">${val}</div></li>`).join('')}
                        </ul>
                    </li>
                    `;
            $filterMenu.append(subMenu);
        });
    });
}
export function setSelectInputValue(select_id, value) {
    const elm = $(select_id);
    if (!elm)
        return;
    elm.val(value);
}
export function getActiveFilters(colIdx) {
    const activeValues = $(`#submenu-${colIdx} .filter-option.active`).map(function () {
        return $.fn.dataTable.util.escapeRegex(String($(this).data('value')));
    }).get();
    return activeValues;
}
export function updateFilters(colIdx) {
    const activeValues = getActiveFilters(colIdx);
    const tableID = $("#filter-dropdown").data('table');
    const table = $(tableID).DataTable();
    if (activeValues.length > 0) {
        table.column(colIdx).search(activeValues.join('|'), true, false).draw();
    }
    else {
        table.column(colIdx).search('').draw();
    }
}
export function defaultPowerModal(power) {
    if (!power.id) {
        $("#power-edit-form").removeData("id");
        $("#power-delete").addClass("d-none");
    }
    else {
        $("#power-edit-form").data("id", power.id);
        $("#power-delete").removeClass("d-none");
    }
    $("#power-name").val(power.name);
    $("#power-prereq").val(power.pre_requisite);
    $("#power-casttime").val(power.casttime);
    $("#power-range").val(power.range);
    setSelectInputValue("#power-source", power.source?.id?.toString() ?? "");
    $("#power-conc").prop('checked', power.concentration ?? false);
    if (power.type.value == "Tech") {
        $('#align-col').addClass('d-none');
    }
    else {
        $('#align-col').removeClass('d-none');
    }
    $("#power-level").val(power.level);
    $("#power-duration").val(power.duration);
    // @ts-expect-error It exists
    if (window.powerMDE) {
        // @ts-expect-error It exists
        window.powerMDE.toTextArea();
    }
    $("#power-desc").val(power.description);
    //@ts-expect-error It exists
    window.powerMDE = new EasyMDE({
        element: document.getElementById('power-desc'),
        autofocus: true,
        sideBySideFullscreen: false,
        autoRefresh: { delay: 300 },
        maxHeight: "20vh",
        toolbar: ["undo", "redo", "|", "bold", "italic", "heading", "|", "code", "quote", "unordered-list", "ordered-list", "|", "link"]
    });
}
export function fetchPowerInputs() {
    const power = {};
    power.id = $("#power-edit-form").data("id");
    power.name = $("#power-name").val().toString();
    power.type = window.location.pathname.includes("tech_powers") ? { id: 2, value: "Tech" } : { id: 1, value: "Force" };
    power.pre_requisite = $("#power-prereq").val().toString();
    power.casttime = $("#power-casttime").val().toString();
    power.range = $("#power-range").val().toString();
    const source_option = $("#power-source").find(':selected');
    power.source = {
        id: Number(source_option.val()),
        name: source_option.html(),
    };
    //@ts-expect-error It exists
    if (window.powerMDE) {
        //@ts-expect-error It exists
        power.description = window.powerMDE.value();
    }
    power.concentration = $("#power-conc").prop('checked');
    if ($("#power-alignment").length) {
        const align_option = $("#power-alignment").find(':selected');
        if (align_option) {
            power.alignment = {
                id: Number(align_option.val()),
                value: align_option.html()
            };
        }
    }
    power.level = Number($("#power-level").val());
    power.duration = $("#power-duration").val().toString();
    return power;
}
