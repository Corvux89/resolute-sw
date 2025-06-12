
import { EnhancedItem, Equipment, Power } from "./types.js";
import { defaultEquipmentModal, defaultItemModal, defaultPowerModal, destroyTable, fetchArchetypInputs, fetchClassInputs, fetchEquipmentInputs, fetchItemInputs, fetchPowerInputs, fetchSpeciesInputs, getActiveFilters, setupMDE, setupTableFilters, ToastError, ToastSuccess, updateClearAllFiltersButton, updateFilters, updateSubTypeFields } from "./utils.js";

// Generic Content
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
                    name: "save",
                    title: "Save",
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

$(document).on('click', '.filter-option', function(e){
    e.preventDefault();
    const colIdx = $(this).data('col');
    const tableID = $("#filter-dropdown").data('table')
    const table = $(tableID).DataTable();
    // Highlight selected
    $(this).toggleClass('active');

    updateFilters(colIdx)

    // Remove all badges for this column
    $(`[id^=filter-badge-${colIdx}-]`).remove();

    const activeValues = getActiveFilters(colIdx)

    // Add badges for all active values
    activeValues.forEach(val => {
        const badgeId = `filter-badge-${colIdx}-${String(val).replace(/\W/g, '')}`;
        const $option = $(`#submenu-${colIdx} .filter-option.active`).filter(function() {
            return $.fn.dataTable.util.escapeRegex(String($(this).data('value'))) === val;
        });

        if ($(`#${badgeId}`).length === 0) {
            $('#active-filters').append(
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

    updateFilters(colIdx)

    updateClearAllFiltersButton()
});

$(document).on('click', '#clear-all-filters', function() {
    $('.filter-option.active').removeClass('active');
    $('#active-filters').empty();
    $("#filter-search").val('')
    const tableID = $("#filter-dropdown").data('table')
    const table = $(tableID).DataTable();
    table.columns().search('').draw();
    table.search('').draw()
    updateClearAllFiltersButton()
});

// Powers
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
                title: "Duration",
                data: "duration"
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
            }
        )
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
        updateClearAllFiltersButton()
    }
    setupTableFilters(tableName, [0,2])
}

$(document).on('click', "#power-table tbody tr", function() {
    if ($(this).closest('btn').length) return

    const table = $("#power-table").DataTable()
    const row = table.row(this)
    const power = row.data() as Power
    let stop = false

    if ($(this).hasClass("bold-row")) stop=true

    $("#power-table tbody tr").removeClass("bold-row")

    $('.dropdown-row').remove()

    if (!power || stop) return
    let editButton = ''

    if (document.body.dataset.admin == "True"){
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
        `
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
    `
 
    $(this).after(additionalInfo)
    $(this).addClass("bold-row")
})


$(document).on('click', '#power-table .edit-button', function(){
    const table = $("#power-table").DataTable()
    const powerId = $(this).data('power-id');
    const power: Power = table.rows().data().toArray().find((row: Power) => row.id == powerId);
    
    if (!power) ToastError("Power not found")

    defaultPowerModal(power)
})

$(document).on('click', '#new-power-btn', function(){
    let power: Power = fetchPowerInputs()
    console.log(power) 
    if (power.id !== undefined){
        power = {}
        const source_option = $("#power-source").find(`option:contains('Resolute Homebrew')`)

        power.type = window.location.pathname.includes("tech_powers") ? {id: 2, value: "Tech"} : {id: 1, value: "Force"}

        power.source = {
            id: Number(source_option.val()),
            name: source_option.html()
        }
    }
    defaultPowerModal(power)
})

$(document).on('click', '#power-submit', function(){
    const power = fetchPowerInputs()

    if (!power.id){
        $.ajax({
            url: `api/powers`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(power),
            success: function() {
                ToastSuccess("Power Added")
                $("#power-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    } else {
        $.ajax({
            url: `api/powers`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(power),
            success: function() {
                ToastSuccess("Power Updated")
                $("#power-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    }
})

$(document).on('click', '#power-delete-confirmed', function(){
    const power = fetchPowerInputs()

    if (!power.id) return

    $.ajax({
        url: `/api/powers/${power.id}`,
        type: "delete",
        contentType: "application/json",
        success: function(){
            ToastError("Power Deleted")
            $("#power-table").DataTable().ajax.reload()
        },
        error: function(e){
            ToastError(`Failed: ${e.responseText}`)
        }
        
    })
})

// Species List
if ($("#species-table").length){
    const params = new URLSearchParams(window.location.search);
    const tableName = "#species-table"

    destroyTable(tableName)

    const table = $(tableName).DataTable({
        ajax: {
            url: '/api/species',
            dataSrc: ''
        },
        pageLength: 500,
        columns: [
            {
                data: "image_url",
                render: function(data, type, row){
                    return `
                    <a href="/species/${encodeURIComponent(row.value.toString().toLowerCase())}">
                        <div class="species-preview-container">
                            <img src="${data ? data : 'static/images/placeholder-trooper.jpg'}" alt="species image" class="species-preview"/>
                        </div>
                    </a>
                    `
                }
            },
            {
                title: "Name",
                data: "value",
                render: function(data){
                    return `<a href="/species/${encodeURIComponent(data.toString().toLowerCase())}" class="species-link undecorated-link text-black">${data}</a>`
                }
            },
            {
                title: "Size",
                data: "size",
                render: function(data, type, row){
                    return `<a href="/species/${encodeURIComponent(row.value.toString().toLowerCase())}" class="species-link undecorated-link text-black">${data}</a>`
                }
            }
        ],
        order: [[1, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true
    })

    if (params.has('name')){
        $("#filter-search").val(params.get('name'))
        table.column(1).search(params.get('name') || '').draw();
        updateClearAllFiltersButton()
    }
    setupTableFilters(tableName, [0,1])
}

$('#species-edit-form').on('show.bs.modal', function(){
    setupMDE("species-flavortext")
    setupMDE("species-traits")

    const species = fetchSpeciesInputs()

    if (!species.id){
        $("#species-delete").addClass("d-none")
    } else {
        $("#species-delete").removeClass("d-none")
    }
})

$(document).on('click', "#species-submit", function(){
    const species = fetchSpeciesInputs()

   if (!species.id){
        $.ajax({
            url: `api/species`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(species),
            success: function() {
                ToastSuccess("Species Added")
                $("#species-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    } else {
        $.ajax({
            url: `${window.location.origin}/api/species`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(species),
            success: function() {
                window.location.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    }
})

$(document).on('click', '#species-delete-confirmed', function(){
    const species = fetchSpeciesInputs()

    if (!species.id) return

    $.ajax({
        url: `${window.location.origin}/api/species/${species.id}`,
        type: "delete",
        contentType: "application/json",
        success: function(){
            ToastError("Species Deleted")
            window.location.href = `/species`;
        },
        error: function(e){
            ToastError(`Failed: ${e.responseText}`)
        }
        
    })
})

// Classes
if ($("#class-table").length){
    const params = new URLSearchParams(window.location.search);
    const tableName = "#class-table"

    destroyTable(tableName)

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
                render: function(data){
                    return `<a href="/classes/${encodeURIComponent(data.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`
                }
            },
            {
                title: "Desc",
                data: "summary",
                render: function(data, type, row){
                    return `<a href="/classes/${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`
                }
            },
            {
                title: "Hit Die",
                data: "hit_die",
                render: function(data, type, row){
                    if (!data) return ""

                    return `<a href="/classes/${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">d${data}</a>`
                }
            },
            {
                title: "Primary Ability",
                data: "primary_ability",
                render: function(data, type, row){
                    if (!data) return ""
                    return `<a href="/classes/${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`
                }
            },
            {
                title: "Archetypes",
                data: "archetype_flavor",
                render: function(data, type, row){
                    if (!data) return ""
                    return `<a href="/archetypes?class=${encodeURIComponent(row.value.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`
                }
            }
        ],
        order: [[0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true
    })

    if (params.has('name')){
        $("#filter-search").val(params.get('name'))
        table.column(0).search(params.get('name') || '').draw();
        updateClearAllFiltersButton()
    }
    setupTableFilters(tableName, [0,1,4])
}

$('#class-edit-form').on('show.bs.modal', function(){
    setupMDE("class-equipment")
    setupMDE("class-flavortext")
    setupMDE("class-level-changes")
    setupMDE("class-features")

    const prim_class = fetchClassInputs()

    if (!prim_class.id){
        $("#class-delete").addClass("d-none")
    } else {
        $("#class-delete").removeClass("d-none")
    }
})

$(document).on('click', "#class-submit", function(){
    const prim_class = fetchClassInputs()

   if (!prim_class.id){
        $.ajax({
            url: `api/classes`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(prim_class),
            success: function() {
                ToastSuccess("Primary Class Added")
                $("#class-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    } else {
        $.ajax({
            url: `${window.location.origin}/api/classes`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(prim_class),
            success: function() {
                window.location.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    }
})

$(document).on('click', '#class-delete-confirmed', function(){
    const prim_class = fetchClassInputs()

    if (!prim_class.id) return

    $.ajax({
        url: `${window.location.origin}/api/classes/${prim_class.id}`,
        type: "delete",
        contentType: "application/json",
        success: function(){
            ToastError("Primary Class Deleted")
            window.location.href = `/classes`;
        },
        error: function(e){
            ToastError(`Failed: ${e.responseText}`)
        }
        
    })
})

// Archetypes
if ($("#archetype-table").length){
    const params = new URLSearchParams(window.location.search);
    const tableName = "#archetype-table"

    destroyTable(tableName)

    const table = $(tableName).DataTable({
        ajax: {
            url: '/api/archetypes',
            dataSrc: ''
        },
        pageLength: 500,
        columns: [
            {
                title: "Archetype",
                data: "value",
                render: function(data){
                    return `<a href="/archetypes/${encodeURIComponent(data.toString().toLowerCase())}" class="class-link undecorated-link text-black">${data}</a>`
                }
            },
            {
                title: "Class",
                data: "parent_name"
            }
        ],
        order: [[0,'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true
    })

     if (params.has('name')){
        $("#filter-search").val(params.get('name'))
        table.column(1).search(params.get('name') || '').draw();
        updateClearAllFiltersButton()
    }

    setupTableFilters(tableName, [0], { 1: params.get('class')})
}

$("#archetype-edit-form").on('show.bs.modal', function(){
    setupMDE('archetype-flavortext')
    setupMDE('archetype-level-table')

    const archetype = fetchArchetypInputs()

     if (!archetype.id){
        $("#archetype-delete").addClass("d-none")
    } else {
        $("#archetype-delete").removeClass("d-none")
    }
})

$(document).on('click', '#archetype-submit', function(){
    const archetype = fetchArchetypInputs()

     if (!archetype.id){
        $.ajax({
            url: `api/archetypes`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(archetype),
            success: function() {
                ToastSuccess("Primary Class Added")
                $("#archetype-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    } else {
        $.ajax({
            url: `${window.location.origin}/api/archetypes`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(archetype),
            success: function() {
                window.location.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    }
})

$(document).on('click', '#archetype-delete-confirmed', function(){
    const archetype = fetchArchetypInputs()

    if (!archetype.id) return

    $.ajax({
        url: `${window.location.origin}/api/archetypes/${archetype.id}`,
        type: "delete",
        contentType: "application/json",
        success: function(){
            ToastError("Archetype Deleted")
            window.location.href = `/archetypes`;
        },
        error: function(e){
            ToastError(`Failed: ${e.responseText}`)
        }
        
    })
})

// Equipment
if ($("#equipment-table").length){
    const params = new URLSearchParams(window.location.search);
    const tableName = "#equipment-table"
    const filterExclusions = [0]

    destroyTable(tableName)

    const columns = [
        {
            title: "Name",
            data: "name"
        }
    ]

    if (window.location.pathname.includes('weapons')){
        filterExclusions.push(2,3,4)
        columns.push(
            {
                title: "Type",
                data: "sub_category",
                // @ts-expect-error cmon man
                render: function(data){
                    if (!data) return ''
                    return data.value
                }
            },
            {
                title: "Property",
                data: "properties"
            },
            {
                title: "Cost",
                data: "cost"      
            },
            {
                title: "Damage",
                render: function(data, type, row){
                    try{
                        if (!("dmg_number_of_die" in row) || !row.dmg_number_of_die || row.dmg_number_of_die == 0) return ''
                        const properties = row.properties.split(', ').map(c => c.replace(/[\s\d]/g, ''));                    
                        if (properties.includes('special')) return 'Special'
                        return `${row.dmg_number_of_die}d${row.dmg_die_type || ""} [${row.dmg_type || ""}]`
                    }
                    catch{
                        return ''
                    }
                }
            },
            {
                title: "Damage Die",
                visible: false,
                data: "dmg_die_type",
                render: function(data){
                    if (!data) return ''
                    return `d${data}`
                }
            },
            {
                title: "Damage Type",
                visible: false,
                data: "dmg_type"
            },
            {
                title: "Properties",
                data: "properties",
                visible: false,
                render: function(data){
                    return data.split(', ').map(c => c.replace(/[\d]/g, '').split("(")[0])
                }
            }
        )
    } else if (window.location.pathname.includes('armor')){
        filterExclusions.push(2,3,4)
        columns.push(
            {
                title: "Type",
                data: "sub_category",
                // @ts-expect-error cmon man
                render: function(data){
                    if (!data) return ''
                    return data.value
                }
            },
            {
                title: "Property",
                data: "properties"
            },
            {
                title: "Cost",
                data: "cost"      
            },
            {
                title: "AC",
                data: "ac"
            },
            {
                title: "Stealth",
                data: "stealth_dis",
                render: function(data){
                    if (!data) return '-'
                    return data == true ? "Disadvantage" : '-'
                }
            },
            {
                title: "Properties",
                data: "properties",
                visible: false,
                render: function(data){
                    return data.split(', ').map(c => c.replace(/[\d]/g, '').split("(")[0])
                }
            }
        )
    } else {
        filterExclusions.push(2,3)
        columns.push(
            {
                title: "Category",
                data: "category",
                // @ts-expect-error cmon man
                render: function(data){
                    if (!data) return ''
                    return data.value
                }
            },
            {
                title: "Cost",
                data: "cost"      
            },
        )
    }


    const table = $(tableName).DataTable({
        ajax: {
            url: 'api/equipment',
            dataSrc: '',
            data: function(d){
                
                d["type"] = window.location.pathname.includes("weapons") ? "weapon": window.location.pathname.includes("armor") ? "armor" : "adventuring"
            }
        },
        pageLength: 500,
        columns: columns,
        order: [[1,'asc'], [0, 'asc']],
        dom: 'rti',
        scrollCollapse: true,
        scrollY: "75vh",
        //@ts-expect-error idk why this errors but it does
        responsive: true,
    })

    if (params.has('name')){
        $("#filter-search").val(params.get('name'))
        table.column(0).search(params.get('name') || '').draw();
        updateClearAllFiltersButton()
    }
    setupTableFilters(tableName, filterExclusions)
}

$(document).on('click', "#equipment-table tbody tr", function(){
    if ($(this).closest('btn').length) return

    const table = $("#equipment-table").DataTable()
    const row = table.row(this)
    const equipment = row.data() as Equipment
    let stop = false

    if ($(this).hasClass("bold-row")) stop=true

    $("#equipment-table tbody tr").removeClass("bold-row")

    $('.dropdown-row').remove()

    if (!equipment || stop) return
    let editButton = ''

    if (document.body.dataset.admin == "True"){
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
        `
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
    `
 
    $(this).after(additionalInfo)
    $(this).addClass("bold-row")
})

$(document).on('click', '#equipment-next', function(){
    const equipment_category_option = $("#equipment-category").find(":selected")

    if (!equipment_category_option.val()){
        ToastError("Select an equipment category first")
    }
    
    let equipment: Equipment = fetchEquipmentInputs()

    if (equipment.id !== undefined){
        equipment = {}
    }

    equipment.category = {"id": Number(equipment_category_option.val()), "value": equipment_category_option.html()}


    defaultEquipmentModal(equipment)
})

$(document).on('click', '#equipment-table .edit-button', function(){
    const table = $("#equipment-table").DataTable()
    const equipId = $(this).data('equip-id');
    const equipment: Equipment = table.rows().data().toArray().find((row: Equipment) => row.id == equipId);
    
    if (!equipment) ToastError("Equipment not found")

    console.log(equipment)

    defaultEquipmentModal(equipment)
})

$(document).on('click', '#equipment-submit', function(){
    const equipment = fetchEquipmentInputs()

    if (!equipment.id){
        $.ajax({
            url: `api/equipment`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(equipment),
            success: function() {
                ToastSuccess("Equipment Added")
                $("#equipment-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    } else {
        $.ajax({
            url: `api/equipment`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(equipment),
            success: function() {
                ToastSuccess("Equipment Updated")
                $("#equipment-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    }
})

$(document).on('click', '#equipment-delete-confirmed', function(){
    const equipment = fetchEquipmentInputs()

    if (!equipment.id) return

    $.ajax({
        url: `/api/equipment/${equipment.id}`,
        type: "delete",
        contentType: "application/json",
        success: function(){
            ToastError("Equipment Deleted")
            $("#equipment-table").DataTable().ajax.reload()
        },
        error: function(e){
            ToastError(`Failed: ${e.responseText}`)
        }
        
    })
})

// Enhanced Items
if ($("#item-table").length){
    const params = new URLSearchParams(window.location.search);
    const tableName = "#item-table"
    
    destroyTable(tableName)
    
    const table = $(tableName).DataTable({
        ajax: {
            url: 'api/enhanced_items',
            dataSrc: '',
            data: function(d){
                d["type"] = window.location.pathname.replace("/enhanced_", "").replace("_", " ")
            }
        },
        pageLength: 1000,
        order: [[1,'asc'], [0, 'asc']],
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
                render: function(data){
                    if (!data) return ''
                    return data.value
                }
            },
            {
                title: "Subtype",
                data: "subtype",
                render: function(data, type, row){
                    if (!data) return ''
                    if (row.subtype_ft) return row.subtype_ft
                    return data.value
                }
            },
            {
                title: "Rarity",
                data: "rarity",
                render: function(data){
                    if (!data) return ''
                    return data.value
                }
            },
            {
                title: "Prerequisite?",
                data: "prerequisite",
                render: function(data){

                    if (data) {
                        return `<i class="fa fa-check text-success"></i>`; // Green checkmark
                    } else {
                        return `<i class="fa fa-times text-danger"></i>`; // Red "x"
                    }
                }
            },
            {
                title: "Attunement?",
                data: "attunement",
                render: function(data){
                     if (data) {
                        return `<i class="fa fa-check text-success"></i>`; // Green checkmark
                    } else {
                        return `<i class="fa fa-times text-danger"></i>`; // Red "x"
                    }
                }
            },
            {
                title: "Cost",
                data: "cost"
            }
        ]
    })

    if (params.has('name')){
        $("#filter-search").val(params.get('name'))
        table.column(0).search(params.get('name') || '').draw();
        updateClearAllFiltersButton()
    }
    setupTableFilters(tableName, [0,1,5])
}

$(document).on('click', "#item-table tbody tr", function(){
    if ($(this).closest('btn').length) return

    const table = $("#item-table").DataTable()
    const row = table.row(this)
    const item = row.data() as EnhancedItem
    let stop = false

    if ($(this).hasClass("bold-row")) stop=true

    $("#item-table tbody tr").removeClass("bold-row")

    $('.dropdown-row').remove()

    if (!item || stop) return
    let editButton = ''
    let prereq = ''

    if (document.body.dataset.admin == "True"){
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
        `
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
    `
 
    $(this).after(additionalInfo)
    $(this).addClass("bold-row")
})

$(document).on('click', '#item-next', function(){
    const item_type_option = $("#item-type").find(":selected")

    if (!item_type_option.val()){
        ToastError("Select an item category first")
    }
    
    let item: EnhancedItem = fetchItemInputs()

    if (item.id !== undefined){
        item = {}
    }

    item.type = {"id": Number(item_type_option.val()), "value": item_type_option.html()}

    defaultItemModal(item)
})

$(document).on('change', '#item-subtype', function(){
    updateSubTypeFields()
})

$(document).on('click', '#item-table .edit-button', function(){
    const table = $("#item-table").DataTable()
    const itemId = $(this).data('item-id');
    const item: EnhancedItem = table.rows().data().toArray().find((row: EnhancedItem) => row.id == itemId);
    
    if (!item) ToastError("Enhance Item not found")
    defaultItemModal(item)
})

$(document).on('click', '#item-submit', function(){
    const item = fetchItemInputs()

    if (!item.id){
        $.ajax({
            url: `api/enhanced_items`,
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(item),
            success: function() {
                ToastSuccess("Enhanced Item Added")
                $("#item-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    } else {
        $.ajax({
            url: `api/enhanced_items`,
            type: "patch",
            contentType: "application/json",
            data: JSON.stringify(item),
            success: function() {
                ToastSuccess("Enhanced Item Updated")
                $("#item-table").DataTable().ajax.reload()
            },
            error: function(e) {
                ToastError(`Failed: ${e.responseText}`)
            }
        });
    }
})

$(document).on('click', '#item-delete-confirmed', function(){
    const item = fetchItemInputs()

    if (!item.id) return

    $.ajax({
        url: `/api/enhanced_items/${item.id}`,
        type: "delete",
        contentType: "application/json",
        success: function(){
            ToastError("Enhanced Item Deleted")
            $("#item-table").DataTable().ajax.reload()
        },
        error: function(e){
            ToastError(`Failed: ${e.responseText}`)
        }
        
    })
})