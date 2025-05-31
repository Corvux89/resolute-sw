import { param } from "jquery";
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
                title: "Pre-Requisite?",
                data: "pre_requisite"
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
        pageLength: 25,
        columns: columns,
        order: [[0,'asc']],
        dom: 'lrtip',
        //@ts-expect-error idk why this errors but it does
        responsive: true,
    })

      if (params.has('name')){
        $("#filter-name").val(params.get('name'))
        table.column(0).search(params.get('name') || '').draw();
    }

    table.on("xhr", function(){
        const data = <Power[]> table.ajax.json()

        const levels = Array.from(new Set(data.map(row => row.level)))
        .sort((a, b) => a - b)
        .map(id => ({ id: id == 0 ? "At-Will": id, name: id == 0 ? "At-Will": id}))

        populateSelectOption("#filter-level", levels, [], "All Levels")

        if ($("#filter-alignment").length){
            const alignmentMap = new Map();
            data.forEach(row => {
                if (row.alignment && !alignmentMap.has(row.alignment.id)) {
                    alignmentMap.set(row.alignment.id, { id: row.alignment.id, name: row.alignment.value });
                }
            });

            const alignments = Array.from(alignmentMap.values())
            .sort((a, b) => a.id - b.id)
            .map(alignment => ({id: alignment.name, name: alignment.name}))

            populateSelectOption("#filter-alignment", alignments, [], "All Alignments");
        }
    })

    $('#filter-name').on('input', function() {
        table.column(0).search((this as HTMLInputElement).value).draw();
    });

    $('#filter-level').on('change', function() {
         const selected = Array.from((this as HTMLSelectElement).selectedOptions).map(opt => opt.value).filter(v => v !== "");
        if (selected.length === 0) {
            table.column(1).search('').draw();
        } else {
            const regex = selected.map(val => '^' + $.fn.dataTable.util.escapeRegex(val) + '$').join('|');
            table.column(1).search(regex, true, false).draw();
        }
    });

    $('#filter-prereq').on('input', function() {
        table.column(2).search((this as HTMLInputElement).value).draw();
    });

    $('#filter-alignment').on('change', function() {
        const val = (this as HTMLSelectElement).value;
        table.column(3).search(val).draw();
    });
}

$(document).on('click', "#power-table tbody tr", function() {
    const table = $("#power-table").DataTable()
    const row = table.row(this)
    const power = row.data() as Power

    if ($(this).next().hasClass('dropdown-row')){
        $(this).next().remove()
        return
    }

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

})