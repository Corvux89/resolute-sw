import { Power, Species } from "./types.js";

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

export function setupMDE(element: string, default_text?: string): void{
    const textarea = document.getElementById(element);
    if (!textarea) return;

    if (window[element] && typeof window[element].toTextArea === "function"){
        window[element].toTextArea()
    }

    if (default_text) $(`#${element}`).val(default_text)
    
    //@ts-expect-error This is pulled in from a parent and no import needed
    window[element] = new EasyMDE(
        {
            element: document.getElementById(element),
            autofocus: true,
            sideBySideFullscreen: false,
            autoRefresh: {delay: 300},
            maxHeight: "20vh",
            toolbar: ["undo","redo","|","bold","italic","heading","|","code","quote","unordered-list","ordered-list","|","link"] 
        }
    )
}

export function getMDEValue(element: string): string{
    if (window[element] && typeof window[element].value === "function") return window[element].value()
    return ""
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
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = render;
                    return tempDiv.textContent.split(",")[0] ?? ""
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

    if ($("#filter-search").length){
        $('#filter-search').on('input', function() {
            table.search((this as HTMLInputElement).value).draw();
        });
    }
}

export function setSelectInputValue(select_id: string, value: string): void{
    const elm = $(select_id)
    if (!elm) return
    elm.val(value)
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

export function defaultPowerModal(power: Power): void{
    if (!power.id){
        $("#power-edit-form").removeData("id")
        $("#power-delete").addClass("d-none")
    } else{
        $("#power-edit-form").data("id", power.id)     
        $("#power-delete").removeClass("d-none")
    }
    $("#power-name").val(power.name)
    $("#power-prereq").val(power.pre_requisite)
    $("#power-casttime").val(power.casttime)
    $("#power-range").val(power.range)
    setSelectInputValue("#power-source", power.source?.id?.toString() ?? "")
    $("#power-conc").prop('checked', power.concentration ?? false)
    
    if (power.type.value == "Tech") {
        $('#align-col').addClass('d-none');
    } else {
        $('#align-col').removeClass('d-none');
    }
    $("#power-level").val(power.level)
    $("#power-duration").val(power.duration)

    setupMDE("power-desc", power.description)
}

export function fetchPowerInputs(): Power{
    const power: Power = {}
    power.id = $("#power-edit-form").data("id")
    power.name = $("#power-name").val().toString()
    power.type = window.location.pathname.includes("tech_powers") ? {id: 2, value: "Tech"} : {id: 1, value: "Force"}
    power.pre_requisite = $("#power-prereq").val().toString()
    power.casttime = $("#power-casttime").val().toString()
    power.range = $("#power-range").val().toString()
    const source_option = $("#power-source").find(':selected')
    power.source = {
        id: Number(source_option.val()),
        name: source_option.html(),
    }
    power.description = getMDEValue("power-desc")
    power.concentration = $("#power-conc").prop('checked')
    if ($("#power-alignment").length){
        const align_option = $("#power-alignment").find(':selected')
        if (align_option){
            power.alignment = {
                id: Number(align_option.val()),
                value: align_option.html()
            }
        }
    }
    power.level = Number($("#power-level").val())
    power.duration = $("#power-duration").val().toString() 
    return power 
}

export function fetchSpeciesInputs(): Species{
    const source_option = $("#species-source").find(':selected')
    const size_option = $("#species-size").find(':selected')

    const species: Species = {
        id: $("#species-edit-form").data('id'),
        value: $("#species-name").val().toString(),
        source: {
            id: Number(source_option.val()), 
            name: source_option.html()
        },
        distinctions: $("#species-distinctions").val().toString(),
        size: size_option.val().toString(),
        image_url: $("#species-image").val().toString(),
        skin_options: $("#species-skin").val().toString(),
        hair_options: $("#species-hair").val().toString(),
        eye_options: $("#species-eye").val().toString(),
        height_average: $("#species-havg").val().toString(),
        height_mod: $("#species-hmod").val().toString(),
        weight_average: $("#species-wavg").val().toString(),
        weight_mod: $("#species-wmod").val().toString(),
        homeworld: $("#species-world").val().toString(),
        language: $("#species-language").val().toString(),
        traits: getMDEValue("species-traits"),
        flavortext: getMDEValue("species-flavortext"),
    }

    return species
}