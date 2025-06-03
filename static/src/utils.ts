export function ToastError(message: string): void{
    $("#error-toast .toast-body").html(message)
    $("#error-toast").toast("show")
}

export function ToastSuccess(message: string): void{
    $("#confirm-toast .toast-body").html(message)
    $("#confirm-toast").toast("show")
}

export function destroyTable(table: string): void{
    if ($.fn.DataTable.isDataTable(table)){
        $(table).DataTable().destroy();
    }
}

export function updateClearAllFiltersButton(): void {
    if ($('#active-filters .badge').length > 0) {
        $('#clear-all-filters').removeClass('d-none');
    } else {
        $('#clear-all-filters').addClass('d-none');
    }
}

export function setupTableFilters(table_name: string, exceptions?: number[]) {
    const table = $(table_name).DataTable();

    table.on("xhr", function(){
        const data = <object[]> table.ajax.json()
        const columns = table.settings().init().columns
        const $filterMenu = $("#filter-dropdown")

        $filterMenu.empty()

        columns.forEach((col, colIdx) => {
            if (!col.data || (exceptions && exceptions.includes(colIdx))) return

            const values = Array.from(new Set(data.map(row => {
                const raw = row[col.data.toString()]
                if (raw == null) return

                if (col.render){
                    // @ts-expect-error This works...idk why typescript has issues with it
                    const render = col.render(raw, 'display', row).toString()
                    return render.split(",")[0]
                }
                return raw.split(",")[0]
            }).filter(v => v != null && v !== "")))

            values.sort((a, b) => a.localeCompare(b, undefined, {numberic: true, sensitivity: 'base'}))

            if (values.length == 0) return

            const subMenuID = `submenu-${colIdx}`

            const subMenu = `
                    <li class="drowdown-submenu">
                        <div class="dropdown-item">${col.title} &raquo;</div>
                        <ul class="dropdown-menu dropdown-submenu" id=${subMenuID}>
                            ${values.map(val => `<li><div class="dropdown-item filter-option" data-col="${colIdx}" data-value="${val}">${val}</div></li>`).join('')}
                        </ul>
                    </li>
                    `
            $filterMenu.append(subMenu)
        })
    })
}

export function populateSelectOption(selector, options, selectedValues, defaultOption) {
    const select = $(selector)
        .html("")
        .append(`<option value="">${defaultOption}</option>`);
    options.forEach(option => {
        select.append(`<option value="${option.id}" ${selectedValues.indexOf(option.id) > -1 ? 'selected' : ''}>${option.name}</option>`);
    });
}

export function getActiveFilters(colIdx: number): string[]{
    const activeValues = $(`#submenu-${colIdx} .filter-option.active`).map(function() {
        return $.fn.dataTable.util.escapeRegex(String($(this).data('value')));
    }).get();

    return activeValues
}

export function updateFilters(colIdx: number): void{
    const activeValues = getActiveFilters(colIdx)
    const tableID = $("#filter-dropdown").data('table')
    const table = $(tableID).DataTable();

    if (activeValues.length > 0) {
        table.column(colIdx).search(activeValues.join('|'), true, false).draw();
    } else {
        table.column(colIdx).search('').draw();
    }
}