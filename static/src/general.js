import { defaultCustomizationModal, defaultEquipmentModal, defaultFeatModal, defaultImprovementModal, defaultItemModal, defaultManeuverModal, defaultPowerModal, destroyTable, fetchArchetypInputs, fetchBackgroundInputs, fetchClassInputs, fetchCustomizationInputs, fetchEquipmentInputs, fetchFeatInputs, fetchImprovementInputs, fetchItemInputs, fetchManeuverInputs, fetchPowerInputs, fetchSpeciesInputs, getActiveFilters, getMDEValue, refreshTableData, setupFilterableTable, setupMDE, setupTableFilters, ToastError, ToastSuccess, updateClearAllFiltersButton, updateFilters, updateSubTypeFields } from "./utils.js";
let isDragging = false;
let mouseDownPos = { x: 0, y: 0 };
const DRAG_THRESHOLD = 5; // pixels
function initClickDragDetection() {
    $(document).on('mousedown', 'tbody tr', function (e) {
        isDragging = false;
        mouseDownPos = { x: e.clientX, y: e.clientY };
    });
    $(document).on('mousemove', 'tbody tr', function (e) {
        if (mouseDownPos.x !== 0 || mouseDownPos.y !== 0) {
            const deltaX = Math.abs(e.clientX - mouseDownPos.x);
            const deltaY = Math.abs(e.clientY - mouseDownPos.y);
            if (deltaX > DRAG_THRESHOLD || deltaY > DRAG_THRESHOLD) {
                e.stopPropagation();
                isDragging = true;
            }
        }
    });
    $(document).on('mouseup', 'tbody tr', function () {
        setTimeout(() => {
            isDragging = false;
            mouseDownPos = { x: 0, y: 0 };
        }, 10);
    });
    $(document).on('click mouseup mousemove mousedown', 'tbody tr', function (e) {
        if (isDragging) {
            e.stopPropagation();
            e.preventDefault();
            return false;
        }
    });
}
$(document).on('DOMContentLoaded', function () {
    initClickDragDetection();
});
function boolColumn(data, type) {
    if (data) {
        if (type == "filter")
            return "Yes";
        return `<i class="fa fa-check text-success"></i>`; // Green checkmark
    }
    else {
        if (type == "filter")
            return "No";
        return `<i class="fa fa-times text-danger"></i>`; // Red "x"
    }
}
function propertyColumn(data, type, category) {
    if (type === "filter") {
        return data.split(", ").map((c) => c.replace(/[\d]/g, "").split("(")[0].trim());
    }
    const escapeHtml = (text) => {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    };
    const properties = data.split(", ").map((c) => c.trim());
    const referenceTable = $("#reference-table");
    const propertiesData = JSON.parse(referenceTable.data("properties") || "[]");
    return properties
        .map((property) => {
        const clean_prop = property.replace(/[\d]/g, "").split("(")[0].trim();
        const matchingProperty = propertiesData.find((prop) => {
            return (prop.name.toLowerCase() === clean_prop.toLowerCase() &&
                prop.type.value === category);
        });
        if (matchingProperty) {
            return `<span class="info-link" data-name="${escapeHtml(matchingProperty.name)}" data-text="${escapeHtml(matchingProperty.text)}">${escapeHtml(property)}</span>`;
        }
        else {
            return escapeHtml(property);
        }
    })
        .join(", ");
}
$(document).on("click", ".info-link", function (e) {
    e.stopPropagation();
    const name = $(this).data("name"); // Get the name from the data attribute
    const text = $(this).data("text"); // Get the text from the data attribute
    // Populate the modal title and body
    $("#info-modal .modal-title").text(name);
    $("#info-modal .modal-body").html(text);
    // Show the modal
    $("#info-modal").modal("show");
});
// Generic Content
if ($("#content-edit-form").length) {
    setupMDE("content-body");
    $(".content-submit-btn").on('click', function () {
        const con = {
            id: $(this).data('key'),
            key: $(this).data('key'),
            content: getMDEValue('content-body')
        };
        $.ajax({
            url: `api/content`,
            type: "PATCH",
            contentType: "application/json",
            data: JSON.stringify(con),
            success: function () {
                location.reload();
            },
            error: function () {
                ToastError("Failed to update content");
            }
        });
    });
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
    table.columns().search('');
    table.search('');
    table.draw();
    updateClearAllFiltersButton();
});
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
            render: function (data, type) {
                return boolColumn(data, type);
            }
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
            error: function (xhr) {
                ToastError(`Failed ${xhr.responseText?.toString()}`);
            },
            data: function (d) {
                d["type"] = window.location.pathname.includes("tech_powers") ? "tech" : "force";
            }
        },
        pageLength: 500,
        columns: columns,
        order: [[1, 'asc'], [0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true,
    });
    if (params.has('name')) {
        $("#filter-search").val(params.get('name'));
        table.column(0).search(params.get('name') || '').draw();
        updateClearAllFiltersButton();
    }
    setupTableFilters(tableName, [0, 2]);
}
$(document).on('click', "#power-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    if (isDragging)
        return; // Prevent click action if user was dragging
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
    const columns = [
        {
            data: "image_url",
            render: function (data, type, row) {
                return `
                <a href="/species/${encodeURIComponent(row.value.toString().toLowerCase())}">
                    <div class="species-preview-container">
                        <img src="${data ? data : `${window.location.origin}/static/images/placeholder-trooper.jpg`}" 
                                alt="species image" 
                                class="species-preview"
                                onerror="this.src='static/images/placeholder-trooper.jpg'; this.onerror=null;"/>
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
    ];
    setupFilterableTable("#species-table", columns, [[1, 'asc']], [0, 1], [], undefined, 1);
}
$('#species-edit-form').on('show.bs.modal', function () {
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
            url: `${window.location.origin}/api/species`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(species),
            success: function () {
                ToastSuccess("Species Added");
                refreshTableData("#species-table", `${window.location.origin}/api/species`);
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
    const columns = [
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
            width: "10%",
            render: function (data, type, row) {
                if (!data)
                    return "";
                if (type == 'sort')
                    return Number(data);
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
    ];
    setupFilterableTable("#class-table", columns, [[0, 'asc']], [0, 1, 4], [{ targets: 2, type: "num" }]);
}
$('#class-edit-form').on('show.bs.modal', function () {
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
            url: `${window.location.origin}/api/classes`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(prim_class),
            success: function () {
                ToastSuccess("Primary Class Added");
                refreshTableData("#class-table", `${window.location.origin}/api/classes`);
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
    const columns = [
        {
            title: "Archetype",
            data: "value",
            render: function (data) {
                return `<a href="/archetypes/${encodeURIComponent(data.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`;
            }
        },
        {
            title: "Class",
            data: "parent_name"
        }
    ];
    const params = new URLSearchParams(window.location.search);
    setupFilterableTable("#archetype-table", columns, [[0, 'asc']], [0], [], { 1: params.get('class') });
}
$("#archetype-edit-form").on('show.bs.modal', function () {
    setupMDE('archetype-flavortext');
    setupMDE('archetype-level-table');
    const archetype = fetchArchetypInputs();
    if (!archetype.id) {
        $("#archetype-delete").addClass("d-none");
    }
    else {
        $("#archetype-delete").removeClass("d-none");
    }
});
$(document).on('click', '#archetype-submit', function () {
    const archetype = fetchArchetypInputs();
    if (!archetype.id) {
        $.ajax({
            url: `api/archetypes`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(archetype),
            success: function () {
                ToastSuccess("Archetype Added");
                refreshTableData("#archetype-table", `${window.location.origin}/api/archetypes`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/archetypes`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(archetype),
            success: function () {
                window.location.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#archetype-delete-confirmed', function () {
    const archetype = fetchArchetypInputs();
    if (!archetype.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/archetypes/${archetype.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Archetype Deleted");
            window.location.href = `/archetypes`;
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Equipment
if ($("#equipment-table").length) {
    const params = new URLSearchParams(window.location.search);
    const tableName = "#equipment-table";
    const filterExclusions = [0];
    destroyTable(tableName);
    const columns = [
        {
            title: "Name",
            data: "name"
        }
    ];
    if (window.location.pathname.includes('weapons')) {
        filterExclusions.push(3, 4);
        columns.push({
            title: "Type",
            data: "sub_category",
            // @ts-expect-error cmon man
            render: function (data) {
                if (!data)
                    return '';
                return data.value;
            }
        }, {
            title: "Property",
            data: "properties",
            render: function (data, type) {
                return propertyColumn(data, type, "Weapon");
            }
        }, {
            title: "Cost",
            data: "cost"
        }, {
            title: "Damage",
            render: function (data, type, row) {
                try {
                    if (!("dmg_number_of_die" in row) || !row.dmg_number_of_die || row.dmg_number_of_die == 0)
                        return '';
                    const properties = row.properties.split(', ').map(c => c.replace(/[\s\d]/g, ''));
                    if (properties.includes('special'))
                        return 'Special';
                    return `${row.dmg_number_of_die}d${row.dmg_die_type || ""} [${row.dmg_type || ""}]`;
                }
                catch {
                    return '';
                }
            }
        }, {
            title: "Damage Die",
            visible: false,
            data: "dmg_die_type",
            render: function (data) {
                if (!data)
                    return '';
                return `d${data}`;
            }
        }, {
            title: "Damage Type",
            visible: false,
            data: "dmg_type"
        });
    }
    else if (window.location.pathname.includes('armor')) {
        filterExclusions.push(3, 4);
        columns.push({
            title: "Type",
            data: "sub_category",
            // @ts-expect-error cmon man
            render: function (data) {
                if (!data)
                    return '';
                return data.value;
            }
        }, {
            title: "Property",
            data: "properties",
            render: function (data, type) {
                return propertyColumn(data, type, "Armor");
            }
        }, {
            title: "Cost",
            data: "cost"
        }, {
            title: "AC",
            data: "ac"
        }, {
            title: "Stealth",
            data: "stealth_dis",
            render: function (data) {
                if (!data)
                    return '-';
                return data == true ? "Disadvantage" : '-';
            }
        });
    }
    else {
        filterExclusions.push(2, 3);
        columns.push({
            title: "Category",
            data: "category",
            // @ts-expect-error cmon man
            render: function (data) {
                if (!data)
                    return '';
                return data.value;
            }
        }, {
            title: "Cost",
            data: "cost"
        });
    }
    const table = $(tableName).DataTable({
        ajax: {
            url: 'api/equipment',
            error: function (xhr) {
                ToastError(`Failed ${xhr.responseText?.toString()}`);
            },
            dataSrc: '',
            data: function (d) {
                d["type"] = window.location.pathname.includes("weapons") ? "weapon" : window.location.pathname.includes("armor") ? "armor" : "adventuring";
            }
        },
        pageLength: 500,
        columns: columns,
        order: [[1, 'asc'], [0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true,
    });
    if (params.has('name')) {
        $("#filter-search").val(params.get('name'));
        table.column(0).search(params.get('name') || '').draw();
        updateClearAllFiltersButton();
    }
    setupTableFilters(tableName, filterExclusions);
}
$(document).on('click', "#equipment-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    if (isDragging)
        return; // Prevent click action if user was dragging
    const table = $("#equipment-table").DataTable();
    const row = table.row(this);
    const equipment = row.data();
    let stop = false;
    if ($(this).hasClass("bold-row"))
        stop = true;
    $("#equipment-table tbody tr").removeClass("bold-row");
    $('.dropdown-row').remove();
    if (!equipment || stop)
        return;
    let editButton = '';
    if (document.body.dataset.admin == "True") {
        editButton = `
            <button type="button"
                id="edit-equipment-btn-${equipment.id}"
                class="btn btn-sm btn-outline-primary ms-3 position-relative edit-button"
                data-equip-id="${equipment.id}"
                title="Edit Equipment"
                data-bs-toggle="modal"
                data-bs-target="#equipment-edit-form">
                <i class="fa fa-pencil"></i>
            </button>
        `;
    }
    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                ${editButton}
                <div class="p-3">
                    ${equipment.description} 
                </div>
            </td>
        </tr>
    `;
    $(this).after(additionalInfo);
    $(this).addClass("bold-row");
});
$(document).on('click', '#equipment-next', function () {
    const equipment_category_option = $("#equipment-category").find(":selected");
    if (!equipment_category_option.val()) {
        ToastError("Select an equipment category first");
    }
    let equipment = fetchEquipmentInputs();
    if (equipment.id !== undefined) {
        equipment = {};
    }
    equipment.category = { "id": Number(equipment_category_option.val()), "value": equipment_category_option.html() };
    defaultEquipmentModal(equipment);
});
$(document).on('click', '#equipment-table .edit-button', function () {
    const table = $("#equipment-table").DataTable();
    const equipId = $(this).data('equip-id');
    const equipment = table.rows().data().toArray().find((row) => row.id == equipId);
    if (!equipment)
        ToastError("Equipment not found");
    defaultEquipmentModal(equipment);
});
$(document).on('click', '#equipment-submit', function () {
    const equipment = fetchEquipmentInputs();
    if (!equipment.id) {
        $.ajax({
            url: `api/equipment`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(equipment),
            success: function () {
                ToastSuccess("Equipment Added");
                $("#equipment-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `api/equipment`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(equipment),
            success: function () {
                ToastSuccess("Equipment Updated");
                $("#equipment-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#equipment-delete-confirmed', function () {
    const equipment = fetchEquipmentInputs();
    if (!equipment.id)
        return;
    $.ajax({
        url: `/api/equipment/${equipment.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Equipment Deleted");
            $("#equipment-table").DataTable().ajax.reload();
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Enhanced Items
if ($("#item-table").length) {
    const params = new URLSearchParams(window.location.search);
    const tableName = "#item-table";
    destroyTable(tableName);
    const table = $(tableName).DataTable({
        ajax: {
            url: 'api/enhanced_items',
            dataSrc: '',
            error: function (xhr) {
                ToastError(`Failed ${xhr.responseText?.toString()}`);
            },
            data: function (d) {
                d["type"] = window.location.pathname.replace("/enhanced_", "").replace("_", " ");
            }
        },
        pageLength: 2000,
        order: [[1, 'asc'], [0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true,
        columns: [
            {
                title: "Name",
                data: "name"
            },
            {
                title: "Type",
                data: "type",
                render: function (data) {
                    if (!data)
                        return '';
                    return data.value;
                }
            },
            {
                title: "Subtype",
                data: "subtype",
                render: function (data, type, row) {
                    if (row.subtype_ft)
                        return row.subtype_ft;
                    if (!data)
                        return '';
                    return data.value;
                }
            },
            {
                title: "Rarity",
                data: "rarity",
                render: function (data, type) {
                    if (!data)
                        return '';
                    if (type == 'sort')
                        return data.id;
                    return data.value;
                }
            },
            {
                title: "Prerequisite?",
                data: "prerequisite",
                render: function (data, type) {
                    return boolColumn(data, type);
                }
            },
            {
                title: "Attunement?",
                data: "attunement",
                render: function (data, type) {
                    return boolColumn(data, type);
                }
            },
            {
                title: "Cost",
                data: "cost"
            }
        ]
    });
    if (params.has('name')) {
        $("#filter-search").val(params.get('name'));
        table.column(0).search(params.get('name') || '').draw();
        updateClearAllFiltersButton();
    }
    setupTableFilters(tableName, [0, 1, 6]);
}
$(document).on('click', "#item-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    if (isDragging)
        return; // Prevent click action if user was dragging
    const table = $("#item-table").DataTable();
    const row = table.row(this);
    const item = row.data();
    let stop = false;
    if ($(this).hasClass("bold-row"))
        stop = true;
    $("#item-table tbody tr").removeClass("bold-row");
    $('.dropdown-row').remove();
    if (!item || stop)
        return;
    let editButton = '';
    let prereq = '';
    if (document.body.dataset.admin == "True") {
        editButton = `
            <button type="button"
                id="edit-item-btn-${item.id}"
                class="btn btn-sm btn-outline-primary ms-3 position-relative edit-button"
                data-item-id="${item.id}"
                title="Edit Item"
                data-bs-toggle="modal"
                data-bs-target="#item-edit-form">
                <i class="fa fa-pencil"></i>
            </button>
        `;
    }
    if (item.prerequisite) {
        prereq = `
            <div class="p-3 text-center">
                <p><strong>Prerequisite:</strong> ${item.prerequisite}</p>
            </div>
        `;
    }
    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                ${editButton}
                ${prereq}
                <div class="p-3">
                    ${item.html_text} 
                </div>
            </td>
        </tr>
    `;
    $(this).after(additionalInfo);
    $(this).addClass("bold-row");
});
$(document).on('click', '#item-next', function () {
    const item_type_option = $("#item-type").find(":selected");
    if (!item_type_option.val()) {
        ToastError("Select an item category first");
    }
    let item = fetchItemInputs();
    if (item.id !== undefined) {
        item = {};
    }
    item.type = { "id": Number(item_type_option.val()), "value": item_type_option.html() };
    defaultItemModal(item);
});
$(document).on('change', '#item-subtype', function () {
    updateSubTypeFields();
});
$(document).on('click', '#item-table .edit-button', function () {
    const table = $("#item-table").DataTable();
    const itemId = $(this).data('item-id');
    const item = table.rows().data().toArray().find((row) => row.id == itemId);
    if (!item)
        ToastError("Enhance Item not found");
    defaultItemModal(item);
});
$(document).on('click', '#item-submit', function () {
    const item = fetchItemInputs();
    if (!item.id) {
        $.ajax({
            url: `api/enhanced_items`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(item),
            success: function () {
                ToastSuccess("Enhanced Item Added");
                $("#item-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `api/enhanced_items`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(item),
            success: function () {
                ToastSuccess("Enhanced Item Updated");
                $("#item-table").DataTable().ajax.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#item-delete-confirmed', function () {
    const item = fetchItemInputs();
    if (!item.id)
        return;
    $.ajax({
        url: `/api/enhanced_items/${item.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Enhanced Item Deleted");
            $("#item-table").DataTable().ajax.reload();
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Feats
if ($("#feat-table").length) {
    const columns = [
        {
            title: "Name",
            data: "name"
        },
        {
            title: "Ability Score Increase",
            data: "attributes",
            render: function (data, type) {
                if (!data)
                    return '';
                if (type == "filter")
                    return data.map(c => c.replace(/[\d]/g, '').split(" ")[0]);
                return data.join(" or ");
            }
        },
        {
            title: "Prerequisite?",
            data: "prerequisite",
            render: function (data, type) {
                return boolColumn(data, type);
            }
        }
    ];
    setupFilterableTable("#feat-table", columns, [[0, 'asc']], [0]);
}
$(document).on('click', "#feat-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    if (isDragging)
        return; // Prevent click action if user was dragging
    const table = $("#feat-table").DataTable();
    const row = table.row(this);
    const feat = row.data();
    let stop = false;
    if ($(this).hasClass("bold-row"))
        stop = true;
    $("#feat-table tbody tr").removeClass("bold-row");
    $('.dropdown-row').remove();
    if (!feat || stop)
        return;
    let editButton = '';
    let prereq = '';
    if (document.body.dataset.admin == "True") {
        editButton = `
            <button type="button"
                id="edit-feat-btn-${feat.id}"
                class="btn btn-sm btn-outline-primary ms-3 position-relative edit-button"
                data-feat-id="${feat.id}"
                title="Edit Feat"
                data-bs-toggle="modal"
                data-bs-target="#feat-edit-form">
                <i class="fa fa-pencil"></i>
            </button>
        `;
    }
    if (feat.prerequisite) {
        prereq = `
        <div class="p-3 text-center">
            <p><strong>Prerequisite:</strong> ${feat.prerequisite}</p>
        </div>
    `;
    }
    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                ${editButton}
                ${prereq}
                <div class="p-3">
                    ${feat.html_text} 
                </div>
            </td>
        </tr>
    `;
    $(this).after(additionalInfo);
    $(this).addClass("bold-row");
});
$(document).on('click', '#feat-table .edit-button', function () {
    const table = $("#feat-table").DataTable();
    const featId = $(this).data('feat-id');
    const feat = table.rows().data().toArray().find((row) => row.id == featId);
    if (!feat)
        ToastError("Power not found");
    defaultFeatModal(feat);
});
$(document).on('click', '#new-feat-btn', function () {
    let feat = fetchFeatInputs();
    if (feat.id !== undefined) {
        feat = {};
        const source_option = $("#feat-source").find(`option:contains('Resolute Homebrew')`);
        feat.source = {
            id: Number(source_option.val()),
            name: source_option.html()
        };
    }
    defaultFeatModal(feat);
});
$(document).on('click', '#feat-submit', function () {
    const feat = fetchFeatInputs();
    if (!feat.id) {
        $.ajax({
            url: `${window.location.origin}/api/features`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(feat),
            success: function () {
                ToastSuccess("Feature Added");
                refreshTableData("#feat-table", `${window.location.origin}/api/features`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/features`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(feat),
            success: function () {
                ToastSuccess("Feature Updated");
                refreshTableData("#feat-table", `${window.location.origin}/api/features`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#feat-delete-confirmed', function () {
    const feat = fetchFeatInputs();
    if (!feat.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/features/${feat.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Feature Deleted");
            refreshTableData("#feat-table", `${window.location.origin}/api/features`);
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Backgrounds
if ($("#background-table").length) {
    const columns = [
        {
            title: "Name",
            data: "name",
            render: function (data) {
                return `<a href="/backgrounds/${encodeURIComponent(data.toString().toLowerCase())}" class="background-link undecorated-link text-black">${data}</a>`;
            }
        },
        {
            title: "Skill Proficiency",
            data: "skills",
            render: function (data, type, row) {
                const validSkills = [
                    "Athletics", "Acrobatics", "Sleight of Hand", "Stealth", "Investigation",
                    "Lore", "Nature", "Piloting", "Technology", "Animal Handling", "Insight",
                    "Medicine", "Perception", "Survival", "Deception", "Intimidation",
                    "Performance", "Persuasion"
                ];
                if (!data)
                    return '';
                if (type == "filter") {
                    const regex = new RegExp(validSkills.join("|"), "gi");
                    return data.match(regex) || [];
                }
                return `<a href="/backgrounds/${encodeURIComponent(row.name.toString().toLowerCase())}" class="background-link undecorated-link text-black">${data}</a>`;
            }
        }
    ];
    setupFilterableTable("#background-table", columns, [[0, 'asc']], [0], []);
}
$('#background-edit-form').on('show.bs.modal', function () {
    setupMDE("background-flavortext");
    setupMDE("background-feats");
    setupMDE("background-personality");
    setupMDE("background-ideal");
    setupMDE("background-flaw");
    setupMDE("background-bond");
    const background = fetchBackgroundInputs();
    if (!background.id) {
        $("#background-delete").addClass("d-none");
    }
    else {
        $("#background-delete").removeClass("d-none");
    }
});
$(document).on('click', "#background-submit", function () {
    const background = fetchBackgroundInputs();
    if (!background.id) {
        $.ajax({
            url: `api/backgrounds`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(background),
            success: function () {
                ToastSuccess("Background Added");
                refreshTableData("#background-table", `${window.location.origin}/api/backgrounds`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/backgrounds`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(background),
            success: function () {
                window.location.reload();
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#background-delete-confirmed', function () {
    const background = fetchBackgroundInputs();
    if (!background.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/backgrounds/${background.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Background Deleted");
            window.location.href = `/backgrounds`;
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Maneuvers
if ($("#maneuver-table").length) {
    const columns = [
        {
            title: "Name",
            data: "name",
        },
        {
            title: "Type",
            data: "type",
            render: function (data) {
                if (!data)
                    return '';
                return data.value.toString();
            }
        },
        {
            title: "Prerequisite?",
            data: "prerequisite",
            render: function (data, type) {
                return boolColumn(data, type);
            }
        }
    ];
    setupFilterableTable("#maneuver-table", columns, [[0, 'asc']], [0]);
}
$(document).on('click', "#maneuver-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    if (isDragging)
        return; // Prevent click action if user was dragging
    const table = $("#maneuver-table").DataTable();
    const row = table.row(this);
    const maneuver = row.data();
    let stop = false;
    if ($(this).hasClass("bold-row"))
        stop = true;
    $("#maneuver-table tbody tr").removeClass("bold-row");
    $('.dropdown-row').remove();
    if (!maneuver || stop)
        return;
    let editButton = '';
    let prereq = '';
    if (document.body.dataset.admin == "True") {
        editButton = `
            <button type="button"
                id="edit-maneuver-btn-${maneuver.id}"
                class="btn btn-sm btn-outline-primary ms-3 position-relative edit-button"
                data-id="${maneuver.id}"
                title="Edit Maneuver"
                data-bs-toggle="modal"
                data-bs-target="#maneuver-edit-form">
                <i class="fa fa-pencil"></i>
            </button>
        `;
    }
    if (maneuver.prerequisite) {
        prereq = `
            <div class="p-3 text-center">
                <p><strong>Prerequisite:</strong> ${maneuver.prerequisite}</p>
            </div>
        `;
    }
    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                ${editButton}
                ${prereq}
                <div class="p-3">
                    ${maneuver.description ? maneuver.description : ''} 
                </div>
            </td>
        </tr>
    `;
    $(this).after(additionalInfo);
    $(this).addClass("bold-row");
});
$(document).on('click', '#maneuver-table .edit-button', function () {
    const table = $("#maneuver-table").DataTable();
    const manId = $(this).data('id');
    const maneuver = table.rows().data().toArray().find((row) => row.id == manId);
    if (!maneuver)
        ToastError("Maneuver not found");
    defaultManeuverModal(maneuver);
});
$(document).on('click', '#maneuver-submit', function () {
    const maneuver = fetchManeuverInputs();
    if (!maneuver.id) {
        $.ajax({
            url: `${window.location.origin}/api/maneuvers`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(maneuver),
            success: function () {
                ToastSuccess("Maneuver Added");
                refreshTableData("#maneuver-table", `${window.location.origin}/api/maneuvers`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/maneuvers`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(maneuver),
            success: function () {
                ToastSuccess("Maneuver Updated");
                refreshTableData("#maneuver-table", `${window.location.origin}/api/maneuvers`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#maneuver-delete-confirmed', function () {
    const maneuver = fetchManeuverInputs();
    if (!maneuver.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/maneuvers/${maneuver.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Maneuver Deleted");
            refreshTableData("#maneuver-table", `${window.location.origin}/api/maneuvers`);
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Customizations
if ($("#customization-table").length) {
    const columns = [
        {
            title: "Name",
            data: "name"
        }
    ];
    setupFilterableTable("#customization-table", columns, [[0, 'asc']], [0]);
}
$(document).on('click', "#customization-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    if (isDragging)
        return; // Prevent click action if user was dragging
    const table = $("#customization-table").DataTable();
    const row = table.row(this);
    const customization = row.data();
    let stop = false;
    if ($(this).hasClass("bold-row"))
        stop = true;
    $("#customization-table tbody tr").removeClass("bold-row");
    $('.dropdown-row').remove();
    if (!customization || stop)
        return;
    let editButton = '';
    if (document.body.dataset.admin == "True") {
        editButton = `
            <button type="button"
                id="edit-customization-btn-${customization.id}"
                class="btn btn-sm btn-outline-primary ms-3 position-relative edit-button"
                data-id="${customization.id}"
                title="Edit Equipment"
                data-bs-toggle="modal"
                data-bs-target="#customization-edit-form">
                <i class="fa fa-pencil"></i>
            </button>
        `;
    }
    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                ${editButton}
                <div class="p-3">
                    ${customization.html_text} 
                </div>
            </td>
        </tr>
    `;
    $(this).after(additionalInfo);
    $(this).addClass("bold-row");
});
$(document).on('click', '#customization-next', function () {
    const customization_type_option = $("#customization-type").find(":selected");
    if (!customization_type_option.val()) {
        ToastError("Select an Customization type first");
    }
    let customization = fetchCustomizationInputs();
    if (customization.id !== undefined) {
        customization = {};
    }
    customization.type = { "id": Number(customization_type_option.val()), "value": customization_type_option.html() };
    console.log(customization);
    defaultCustomizationModal(customization);
});
$(document).on('click', '#customization-table .edit-button', function () {
    const table = $("#customization-table").DataTable();
    const objId = $(this).data('id');
    const customization = table.rows().data().toArray().find((row) => row.id == objId);
    if (!customization)
        ToastError("Customization not found");
    defaultCustomizationModal(customization);
});
$(document).on('click', '#customization-submit', function () {
    const customization = fetchCustomizationInputs();
    console.log(customization);
    if (!customization.id) {
        $.ajax({
            url: `${window.location.origin}/api/customizations`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(customization),
            success: function () {
                ToastSuccess("customization Added");
                refreshTableData("#customization-table", `${window.location.origin}/api/customizations?type=${customization.type.value}`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/customizations`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(customization),
            success: function () {
                ToastSuccess("Customization Updated");
                refreshTableData("#customization-table", `${window.location.origin}/api/customizations?type=${customization.type.value}`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#customization-delete-confirmed', function () {
    const customization = fetchCustomizationInputs();
    if (!customization.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/customizations/${customization.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Customization Deleted");
            refreshTableData("#customization-table", `${window.location.origin}/api/customizations?type=${customization.type.value}`);
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
// Improvements
if ($("#improvement-table").length) {
    const columns = [
        {
            title: "Name",
            data: "name"
        },
        {
            title: "Prerequisite?",
            data: "prerequisite",
            render: function (data, type) {
                return boolColumn(data, type);
            }
        }
    ];
    setupFilterableTable("#improvement-table", columns, [[0, 'asc']], [0]);
}
$(document).on('click', "#improvement-table tbody tr", function () {
    if ($(this).closest('btn').length)
        return;
    if (isDragging)
        return; // Prevent click action if user was dragging
    const table = $("#improvement-table").DataTable();
    const row = table.row(this);
    const improvement = row.data();
    let stop = false;
    if ($(this).hasClass("bold-row"))
        stop = true;
    $("#improvement-table tbody tr").removeClass("bold-row");
    $('.dropdown-row').remove();
    if (!improvement || stop)
        return;
    let editButton = '';
    let prereq = '';
    if (document.body.dataset.admin == "True") {
        editButton = `
            <button type="button"
                id="edit-improvement-btn-${improvement.id}"
                class="btn btn-sm btn-outline-primary ms-3 position-relative edit-button"
                data-id="${improvement.id}"
                title="Edit Improvement"
                data-bs-toggle="modal"
                data-bs-target="#improvement-edit-form">
                <i class="fa fa-pencil"></i>
            </button>
        `;
    }
    if (improvement.prerequisite) {
        prereq = `
            <div class="p-3 text-center">
                <p><strong>Prerequisite:</strong> ${improvement.prerequisite}</p>
            </div>
        `;
    }
    const additionalInfo = `
        <tr class="dropdown-row">
            <td colspan="${table.columns().count()}">
                ${editButton}
                ${prereq}
                <div class="p-3">
                    ${improvement.html_text} 
                </div>
            </td>
        </tr>
    `;
    $(this).after(additionalInfo);
    $(this).addClass("bold-row");
});
$(document).on('click', '#improvement-next', function () {
    const improvement_type_option = $("#improvement-type").find(":selected");
    if (!improvement_type_option.val()) {
        ToastError("Select an Improvement type first");
    }
    let improvement = fetchImprovementInputs();
    if (improvement.id !== undefined) {
        improvement = {};
    }
    improvement.type = { "id": Number(improvement_type_option.val()), "value": improvement_type_option.html() };
    defaultImprovementModal(improvement);
});
$(document).on('click', '#improvement-table .edit-button', function () {
    const table = $("#improvement-table").DataTable();
    const objId = $(this).data('id');
    const improvement = table.rows().data().toArray().find((row) => row.id == objId);
    if (!improvement)
        ToastError("Improvement not found");
    defaultImprovementModal(improvement);
});
$(document).on('click', '#improvement-submit', function () {
    const improvement = fetchImprovementInputs();
    if (!improvement.id) {
        $.ajax({
            url: `${window.location.origin}/api/improvements`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(improvement),
            success: function () {
                ToastSuccess("Improvement Added");
                refreshTableData("#improvement-table", `${window.location.origin}/api/improvements?type=${improvement.type.value}`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
    else {
        $.ajax({
            url: `${window.location.origin}/api/improvements`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(improvement),
            success: function () {
                ToastSuccess("Improvement Updated");
                refreshTableData("#improvement-table", `${window.location.origin}/api/improvements?type=${improvement.type.value}`);
            },
            error: function (e) {
                ToastError(`Failed: ${e.responseText}`);
            }
        });
    }
});
$(document).on('click', '#improvement-delete-confirmed', function () {
    const improvement = fetchImprovementInputs();
    if (!improvement.id)
        return;
    $.ajax({
        url: `${window.location.origin}/api/improvements/${improvement.id}`,
        type: "delete",
        contentType: "application/json",
        success: function () {
            ToastError("Improvement Deleted");
            refreshTableData("#improvement-table", `${window.location.origin}/api/improvements?type=${improvement.type.value}`);
        },
        error: function (e) {
            ToastError(`Failed: ${e.responseText}`);
        }
    });
});
