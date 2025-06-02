import { Power } from "./types.js";

export function ToastError(message: string): void{
    $("#error-toast .toast-body").html(message)
    $("#error-toast").toast("show")
}

export function ToastSuccess(message: string): void{
    $("#confirm-toast .toast-body").html(message)
    $("#confirm-toast").toast("show")
}

function destroyTable(table: string): void{
    if ($.fn.DataTable.isDataTable(table)){
        $(table).DataTable().destroy();
    }
}

function updateClearAllFiltersButton() {
    if ($('#active-power-filters .badge').length > 0) {
        $('#clear-all-filters').removeClass('d-none');
    } else {
        $('#clear-all-filters').addClass('d-none');
    }
}

function populateSelectOption(selector, options, selectedValues, defaultOption) {
    const select = $(selector)
        .html("")
        .append(`<option value="">${defaultOption}</option>`);
    options.forEach(option => {
        select.append(`<option value="${option.id}" ${selectedValues.indexOf(option.id) > -1 ? 'selected' : ''}>${option.name}</option>`);
    });
}

if ($("#content-edit-form").length){
    //@ts-expect-error This is pulled in from a parent and no import needed
    const easyMDE = new EasyMDE(
        {
            element: document.getElementById('content-body'),
            autofocus: true,
            sideBySideFullscreen: false,
            autoRefresh: { delay: 300},
            maxHeight: "80vh",
            toolbar: ["undo","redo",
                {
                    "name": "save",
                    className: "fa-solid fa-floppy-disk",
                    action: (editor) => {
                        const key = $("#content-submit-button").data('key')
                        const content = editor.value()
                        $.ajax({
                            url: `api/content/${key}`,
                            type: "PATCH",
                            contentType: "application/json",
                            data: JSON.stringify({ content }),
                            success: function() {
                                ToastSuccess("Content saved. Refresh to view.")
                            },
                            error: function() {
                                ToastError("Failed to update content")
                            }
                        });
                    }
                },
                "|","bold","italic","heading","|","code","quote","unordered-list","ordered-list","|","link"] 
        }
    )

    $("#content-submit-button").on('click', function(){
        const key = $(this).data('key');
        const content = easyMDE.value()

        $.ajax({
            url: `api/content/${key}`,
            type: "PATCH",
            contentType: "application/json",
            data: JSON.stringify({ content }),
            success: function() {
                location.reload();
            },
            error: function() {
                ToastError("Failed to update content")
            }
        });
    })
}

if ($("#power-table").length){
     const params = new URLSearchParams(window.location.search);
    const tableName = "#power-table"
    const columns = [
            {
                title: "Name",
                data: "name"
            },
            {
                title: "Level",
                data: "level",
                render: function (data){ return data==0 ? "At-Will" : data }
            },
            {
                title: "Cast Time",
                data: "casttime"
            },
            {
                title: "Range",
                data: "range"
            },
             { 
                data: 'concentration',
                title: "Conc?",
                render: function(data) { return data ? "Yes" : "No"; }
            }
        ]

    if (window.location.pathname.includes("force_powers")){
        columns.splice(3,0,
            {
                title: "Pre-Requisite?",
                data: "pre_requisite"
            },
            {
            title: "Alignment",
            data: "alignment",
            render: function(data) {return data.value}
        })
    }

    destroyTable(tableName)

    const table = $(tableName).DataTable({
        ajax: {
            url: '/api/powers',
            dataSrc: '',
            data: function(d) {
                d["type"] =  window.location.pathname.includes("tech_powers") ? "tech" : "force"
            }
        },
        pageLength: 500,
        columns: columns,
        order: [[0,'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true,
    })

      if (params.has('name')){
        $("#filter-search").val(params.get('name'))
        table.column(0).search(params.get('name') || '').draw();
    }

    table.on("xhr", function(){
        const data = <Power[]> table.ajax.json()
        const columns = table.settings().init().columns;
        const $filterMenu = $("#power-filter")
        $filterMenu.empty()

        columns.forEach((col, colIdx) => {
            if (!col.data || colIdx===0) return

            const values = Array.from(new Set(data.map(row => {
                const raw = row[col.data.toString()]
                if (col.render){
                    // @ts-expect-error This works...idk why typescript has issues with it
                    const render = col.render(raw, 'display', row).toString()
                    return render.split(",")[0]
                }
                return raw.split(",")[0]

            }).filter(v => v != null && v !== "" && v !==",")))

            values.sort((a, b) => a.localeCompare(b, undefined, {numeric: true, sensitivity: 'base'}));

            if (values.length === 0) return

            const subMenuID = `submenu-${colIdx}`

            const submenu = `
                <li class="drowdown-submenu">
                    <div class="dropdown-item">${col.title} &raquo;</div>
                    <ul class="dropdown-menu dropdown-submenu" id=${subMenuID}>
                        ${values.map(val => `<li><div class="dropdown-item filter-option" data-col="${colIdx}" data-value="${val}">${val}</div></li>`).join('')}
                    </ul>
                </li>
            `
            $filterMenu.append(submenu)
        })
    })

    $('#filter-search').on('input', function() {
        table.search((this as HTMLInputElement).value).draw();
    });
}

$(document).on('click', '.filter-option', function(e){
    e.preventDefault();
    const colIdx = $(this).data('col');
    const table = $("#power-table").DataTable();

    // Highlight selected
    $(this).toggleClass('active');

    // Gather all active values for this column
    const activeValues = $(`#submenu-${colIdx} .filter-option.active`).map(function() {
        return $.fn.dataTable.util.escapeRegex(String($(this).data('value')));
    }).get();
    console.log("ADD FILTERS")
    console.log(activeValues)

    // Build regex for OR search if multiple, or clear if none
    if (activeValues.length > 0) {
        table.column(colIdx).search(activeValues.join('|'), true, false).draw();
    } else {
        table.column(colIdx).search('', true, false).draw();
    }

    // Remove all badges for this column
    $(`[id^=filter-badge-${colIdx}-]`).remove();

    // Add badges for all active values
    activeValues.forEach(val => {
        const badgeId = `filter-badge-${colIdx}-${String(val).replace(/\W/g, '')}`;
        const $option = $(`#submenu-${colIdx} .filter-option.active`).filter(function() {
            return $.fn.dataTable.util.escapeRegex(String($(this).data('value'))) === val;
        });

        if ($(`#${badgeId}`).length === 0) {
            $('#active-power-filters').append(
                `<span class="badge badge-pointer bg-primary me-1"
                    id="${badgeId}"
                    data-col="${colIdx}"
                    data-value="${$option.data('value')}"
                    data-dismiss="badge">
                    ${table.settings().init().columns[colIdx].title}: ${$option.data('value')}
                </span>`
                );
            }
    });  

    updateClearAllFiltersButton()
})

$(document).on('click', '[data-dismiss="badge"]', function() {
    const colIdx = $(this).data('col');
    const value = $(this).data('value');
    
    $(`#submenu-${colIdx} .filter-option`).each(function() {
        if ($(this).data('value') == value) {
            $(this).removeClass('active');
        }
    });

    $(this).remove();

    const activeValues = $(`#submenu-${colIdx} .filter-option.active`).map(function() {
        return $.fn.dataTable.util.escapeRegex(String($(this).data('value')));
    }).get();

    console.log("REMOVE FILTERS")
    console.log(activeValues)

    const table = $("#power-table").DataTable();
    if (activeValues.length > 0) {
        table.column(colIdx).search(activeValues.join('|'), true, false).draw();
    } else {
        table.column(colIdx).search('').draw();
    }

    updateClearAllFiltersButton()
});

$(document).on('click', '#clear-all-filters', function() {
    $('.filter-option.active').removeClass('active');
    $('#active-power-filters').empty();
    const table = $("#power-table").DataTable();
    table.columns().search('').draw();
    updateClearAllFiltersButton()
});

$(document).on('click', "#power-table tbody tr", function() {
    const table = $("#power-table").DataTable()
    const row = table.row(this)
    const power = row.data() as Power

    $("#power-table tbody tr").removeClass("bold-row")

    $('.dropdown-row').remove()

    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                <div class="p-3">
                    ${power.html_desc}
                </div>
            </tb>
        </tr>
    `
    $(this).after(additionalInfo)
    $(this).addClass("bold-row")
})