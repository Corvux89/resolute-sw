import { defaultPowerModal, destroyTable, fetchClassInputs, fetchPowerInputs, fetchSpeciesInputs, getActiveFilters, setupMDE, setupTableFilters, ToastError, ToastSuccess, updateClearAllFiltersButton, updateFilters } from "./utils.js";
// Generic Content
if ($("#content-edit-form").length) {
    //@ts-expect-error This is pulled in from a parent and no import needed
    const easyMDE = new EasyMDE({
        element: document.getElementById('content-body'),
        autofocus: true,
        sideBySideFullscreen: false,
        autoRefresh: { delay: 300 },
        maxHeight: "80vh",
        toolbar: ["undo", "redo",
            {
                name: "save",
                title: "Save",
                className: "fa-solid fa-floppy-disk",
                action: (editor) => {
                    const key = $("#content-submit-button").data('key');
                    const content = editor.value();
                    $.ajax({
                        url: `api/content/${key}`,
                        type: "PATCH",
                        contentType: "application/json",
                        data: JSON.stringify({ content }),
                        success: function () {
                            ToastSuccess("Content saved. Refresh to view.");
                        },
                        error: function () {
                            ToastError("Failed to update content");
                        }
                    });
                }
            },
            "|", "bold", "italic", "heading", "|", "code", "quote", "unordered-list", "ordered-list", "|", "link"]
    });
    $("#content-submit-button").on('click', function () {
        const key = $(this).data('key');
        const content = easyMDE.value();
        $.ajax({
            url: `api/content/${key}`,
            type: "PATCH",
            contentType: "application/json",
            data: JSON.stringify({ content }),
            success: function () {
                location.reload();
            },
            error: function () {
                ToastError("Failed to update content");
            }
        });
    });
}
// Powers
if ($("#power-table").length) {
    const params = new URLSearchParams(window.location.search);
    const tableName = "#power-table";
    const columns = [
        {
            title: "Name",
            data: "name"
        },
        {
            title: "Level",
            data: "level",
            render: function (data) { return data == 0 ? "At-Will" : data; }
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
            title: "Duration",
            data: "duration"
        },
        {
            data: 'concentration',
            title: "Conc?",
            render: function (data) { return data ? "Yes" : "No"; }
        }
    ];
    if (window.location.pathname.includes("force_powers")) {
        columns.splice(3, 0, {
            title: "Alignment",
            data: "alignment",
            render: function (data) { return data.value; }
        });
    }
    destroyTable(tableName);
    const table = $(tableName).DataTable({
        ajax: {
            url: '/api/powers',
            dataSrc: '',
            data: function (d) {
                d["type"] = window.location.pathname.includes("tech_powers") ? "tech" : "force";
            }
        },
        pageLength: 500,
        columns: columns,
        order: [[0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true,
    });
    if (params.has('name')) {
        $("#filter-search").val(params.get('name'));
        table.column(0).search(params.get('name') || '').draw();
    }
    setupTableFilters(tableName, [0, 2]);
}
$(document).on('click', '.filter-option', function (e) {
    e.preventDefault();
    const colIdx = $(this).data('col');
    const tableID = $("#filter-dropdown").data('table');
    const table = $(tableID).DataTable();
    // Highlight selected
    $(this).toggleClass('active');
    updateFilters(colIdx);
    // Remove all badges for this column
    $(`[id^=filter-badge-${colIdx}-]`).remove();
    const activeValues = getActiveFilters(colIdx);
    // Add badges for all active values
    activeValues.forEach(val => {
        const badgeId = `filter-badge-${colIdx}-${String(val).replace(/\W/g, '')}`;
        const $option = $(`#submenu-${colIdx} .filter-option.active`).filter(function () {
            return $.fn.dataTable.util.escapeRegex(String($(this).data('value'))) === val;
        });
        if ($(`#${badgeId}`).length === 0) {
            $('#active-filters').append(`<span class="badge badge-pointer bg-primary me-1"
                    id="${badgeId}"
                    data-col="${colIdx}"
                    data-value="${$option.data('value')}"
                    data-dismiss="badge">
                    ${table.settings().init().columns[colIdx].title}: ${$option.data('value')}
                </span>`);
        }
    });
    updateClearAllFiltersButton();
});
$(document).on('click', '[data-dismiss="badge"]', function () {
    const colIdx = $(this).data('col');
    const value = $(this).data('value');
    $(`#submenu-${colIdx} .filter-option`).each(function () {
        if ($(this).data('value') == value) {
            $(this).removeClass('active');
        }
    });
    $(this).remove();
    updateFilters(colIdx);
    updateClearAllFiltersButton();
});
$(document).on('click', '#clear-all-filters', function () {
    $('.filter-option.active').removeClass('active');
    $('#active-filters').empty();
    $("#filter-search").val('');
    const tableID = $("#filter-dropdown").data('table');
    const table = $(tableID).DataTable();
    table.columns().search('').draw();
    updateClearAllFiltersButton();
});
$(document).on('click', "#power-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    const table = $("#power-table").DataTable();
    const row = table.row(this);
    const power = row.data();
    let stop = false;
    if ($(this).hasClass("bold-row"))
        stop = true;
    $("#power-table tbody tr").removeClass("bold-row");
    $('.dropdown-row').remove();
    if (!power || stop)
        return;
    let editButton = '';
    if (document.body.dataset.admin == "True") {
        editButton = `
            <button type="button"
                id="edit-power-btn-${power.id}"
                class="btn btn-sm btn-outline-primary ms-3 position-relative edit-button"
                data-power-id="${power.id}"
                title="Edit Power"
                data-bs-toggle="modal"
                data-bs-target="#power-edit-form">
                <i class="fa fa-pencil"></i>
            </button>
        `;
    }
    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                ${editButton}
                <div class="p-3">
                    ${power.html_desc} 
                </div>
            </td>
        </tr>
    `;
    $(this).after(additionalInfo);
    $(this).addClass("bold-row");
});
$(document).on('click', '#power-table .edit-button', function () {
    const table = $("#power-table").DataTable();
    const powerId = $(this).data('power-id');
    const power = table.rows().data().toArray().find((row) => row.id == powerId);
    if (!power)
        ToastError("Power not found");
    defaultPowerModal(power);
});
$(document).on('click', '#new-power-btn', function () {
    let power = fetchPowerInputs();
    if (power.id !== undefined) {
        power = {};
        const source_option = $("#power-source").find(`option:contains('Resolute Homebrew')`);
        power.type = window.location.pathname.includes("tech_powers") ? { id: 2, value: "Tech" } : { id: 1, value: "Force" };
        power.source = {
            id: Number(source_option.val()),
            name: source_option.html()
        };
    }
    defaultPowerModal(power);
});
$(document).on('click', '#power-submit', function () {
    const power = fetchPowerInputs();
    if (!power.id) {
        $.ajax({
            url: `api/powers`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(power),
            success: function () {
                ToastSuccess("Power Added");
                $("#power-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `api/powers`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(power),
            success: function () {
                ToastSuccess("Power Updated");
                $("#power-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#power-delete-confirmed', function () {
    const power = fetchPowerInputs();
    if (!power.id)
        return;
    $.ajax({
        url: `/api/powers/${power.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Power Deleted");
            $("#power-table").DataTable().ajax.reload();
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Species List
if ($("#species-table").length) {
    const params = new URLSearchParams(window.location.search);
    const tableName = "#species-table";
    destroyTable(tableName);
    const table = $(tableName).DataTable({
        ajax: {
            url: '/api/species',
            dataSrc: ''
        },
        pageLength: 500,
        columns: [
            {
                data: "image_url",
                render: function (data, type, row) {
                    return `
                    <a href="/species/${encodeURIComponent(row.value.toString().toLowerCase())}">
                        <div class="species-preview-container">
                            <img src="${data ? data : 'static/images/placeholder-trooper.jpg'}" alt="species image" class="species-preview"/>
                        </div>
                    </a>
                    `;
                }
            },
            {
                title: "Name",
                data: "value",
                render: function (data) {
                    return `<a href="/species/${encodeURIComponent(data.toString().toLowerCase())}" class="species-link undecorated-link text-black">${data}</a>`;
                }
            },
            {
                title: "Size",
                data: "size",
                render: function (data, type, row) {
                    return `<a href="/species/${encodeURIComponent(row.value.toString().toLowerCase())}" class="species-link undecorated-link text-black">${data}</a>`;
                }
            }
        ],
        order: [[1, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true
    });
    if (params.has('name')) {
        $("#filter-search").val(params.get('name'));
        table.column(1).search(params.get('name') || '').draw();
    }
    setupTableFilters(tableName, [0, 1]);
}
$('#species-edit-form').on('shown.bs.modal', function () {
    setupMDE("species-flavortext");
    setupMDE("species-traits");
    const species = fetchSpeciesInputs();
    if (!species.id) {
        $("#species-delete").addClass("d-none");
    }
    else {
        $("#species-delete").removeClass("d-none");
    }
});
$(document).on('click', "#species-submit", function () {
    const species = fetchSpeciesInputs();
    if (!species.id) {
        $.ajax({
            url: `api/species`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(species),
            success: function () {
                ToastSuccess("Species Added");
                $("#species-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/species`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(species),
            success: function () {
                window.location.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#species-delete-confirmed', function () {
    const species = fetchSpeciesInputs();
    if (!species.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/species/${species.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Species Deleted");
            window.location.href = `/species`;
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Classes
if ($("#class-table").length) {
    const params = new URLSearchParams(window.location.search);
    const tableName = "#class-table";
    destroyTable(tableName);
    const table = $(tableName).DataTable({
        ajax: {
            url: '/api/classes',
            dataSrc: ''
        },
        pageLength: 500,
        columns: [
            {
                title: "Class",
                data: "value",
                render: function (data) {
                    return `<a href="/classes/${encodeURIComponent(data.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`;
                }
            },
            {
                title: "Desc",
                data: "summary",
                render: function (data, type, row) {
                    return `<a href="/classes/${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`;
                }
            },
            {
                title: "Hit Die",
                data: "hit_die",
                render: function (data, type, row) {
                    if (!data)
                        return "";
                    return `<a href="/classes/${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">d${data}</a>`;
                }
            },
            {
                title: "Primary Ability",
                data: "primary_ability",
                render: function (data, type, row) {
                    if (!data)
                        return "";
                    return `<a href="/classes/${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`;
                }
            },
            {
                title: "Archetypes",
                data: "archetype_flavor",
                render: function (data, type, row) {
                    if (!data)
                        return "";
                    return `<a href="/archetypes?class=${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`;
                }
            }
        ],
        order: [[0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true
    });
    if (params.has('name')) {
        $("#filter-search").val(params.get('name'));
        table.column(0).search(params.get('name') || '').draw();
    }
    setupTableFilters(tableName, [0, 1, 4]);
}
$('#class-edit-form').on('shown.bs.modal', function () {
    setupMDE("class-equipment");
    setupMDE("class-flavortext");
    setupMDE("class-level-changes");
    setupMDE("class-features");
    const prim_class = fetchClassInputs();
    if (!prim_class.id) {
        $("#class-delete").addClass("d-none");
    }
    else {
        $("#class-delete").removeClass("d-none");
    }
});
$(document).on('click', "#class-submit", function () {
    const prim_class = fetchClassInputs();
    if (!prim_class.id) {
        $.ajax({
            url: `api/classes`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(prim_class),
            success: function () {
                ToastSuccess("Primary Class Added");
                $("#class-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/classes`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(prim_class),
            success: function () {
                window.location.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#class-delete-confirmed', function () {
    const prim_class = fetchClassInputs();
    if (!prim_class.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/classes/${prim_class.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Primary Class Deleted");
            window.location.href = `/classes`;
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Archetypes
if ($("#archetype-table").length) {
    const params = new URLSearchParams(window.location.search);
    const tableName = "#archetype-table";
    destroyTable(tableName);
    const table = $(tableName).DataTable({
        ajax: {
            url: '/api/archetypes',
            dataSrc: ''
        },
        pageLength: 500,
        columns: [
            {
                title: "Archetype",
                data: "value"
            },
            {
                title: "Class",
                data: "parent_name"
            }
        ],
        order: [[0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true
    });
    if (params.has('name')) {
        $("#filter-search").val(params.get('name'));
        table.column(1).search(params.get('name') || '').draw();
    }
    setupTableFilters(tableName, [0], { 1: params.get('class') });
}
