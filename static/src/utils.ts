import { Archetype, EnhancedItem, Equipment, Feat, Power, PrimaryClass, Species } from "./types.js";

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

export function setupMDE(element: string, default_text?: string, clear_text: boolean = false): void{
    const textarea = document.getElementById(element);
    if (!textarea) return;

    if (window[element] && typeof window[element].toTextArea === "function"){
        window[element].toTextArea()
    }

    if (default_text || clear_text) $(`#${element}`).val(default_text)
    
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
    if ($('#active-filters .badge').length > 0 || $("#filter-search").val() != "") {
        $('#clear-all-filters').removeClass('d-none');
    } else {
        $('#clear-all-filters').addClass('d-none');
    }
}

export function updateSubTypeFields(): void{
    const numberOfOptions = $("#equipment-subcategory").find("option").length;
    if (numberOfOptions == 1){
        $("#item-subtype-col").addClass("d-none")
        $("#item-subtype-ft-col").removeClass("d-none")
    } else {
        $("#item-subtype-col").removeClass("d-none")
        const subtype_options = $("#item-subtype").find(':selected')

        if (subtype_options.val() && subtype_options.html() == "Specific" || subtype_options.html() == "Other"){
            $("#item-subtype-ft-col").removeClass("d-none")
        } else {
            $("#item-subtype-ft-col").addClass("d-none")
        }
    }
}

export function updateSubCategoryFields(): void{
    const numberOfOptions = $("#equipment-subcategory").find("option").length;
    if (numberOfOptions == 1){
        $("#equipment-subcategory-col").addClass("d-none")
    } else {
        $("#item-subcategory-col").removeClass("d-none")
    }
}

export function setupTableFilters(table_name: string, exceptions?: number[], initialFilters?: {[colIdx: number]: string}) {
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
                if (raw == null || raw == undefined) return
                try{
                    if (col.render){
                        // @ts-expect-error This works...idk why typescript has issues with it
                        const render = col.render(raw, 'display', row).toString()
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = render;
                        return tempDiv.textContent.split(",")[0] ?? ""
                    }
                    return typeof raw === "string" ? raw.split(",")[0] : raw.toString();
                } catch{
                    return
                }
                
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

         // Reapply active state for dropdown items based on initial filters
        if (initialFilters) {
            Object.entries(initialFilters).forEach(([colIdx, filterValue]) => {
                if (!filterValue) return
                const submenuID = `submenu-${colIdx}`;
                const $submenuItem = $(`#${submenuID} .filter-option`).filter(function () {
                    return $(this).data('value').toString().toLowerCase() === filterValue.toLowerCase();
                });

                if ($submenuItem.length) {
                    $submenuItem.trigger('click');
                }
            });
        }
    })

    if ($("#filter-search").length){
        $('#filter-search').on('input', function() {
            const params = new URLSearchParams(window.location.search);
            table.search($(this).val().toString()).draw();
            updateClearAllFiltersButton()

            if (params.has('name') && $(this).val() == ""){
                table.column(0).search("").draw()
            }
        });
    }
}

export function setSelectInputValue(select_id: string, value: string): void{
    const elm = $(select_id)
    if (!elm) return
    elm.val(value)
}

function prefillCheckboxGroup(groupId: string, values: string[]): void {
    const checkboxGroup = $(`#${groupId}`);
    if (!checkboxGroup.length) {
        console.error(`Checkbox group with ID "${groupId}" not found.`);
        return;
    }

    values.forEach((value) => {
        const checkbox = checkboxGroup.find(`input[type="checkbox"][id="${value}"]`);
        if (checkbox.length) {
            checkbox.prop("checked", true);
        } else {
            console.warn(`Checkbox with ID "${value}" not found in group "${groupId}".`);
        }
    });
}

function getSelectedCheckboxValues(groupId: string): string[] {
    const selectedValues: string[] = [];
    const checkboxGroup = $(`#${groupId}`);
    if (!checkboxGroup.length) {
        console.error(`Checkbox group with ID "${groupId}" not found.`);
        return selectedValues;
    }

    checkboxGroup.find('input[type="checkbox"]:checked').each(function () {
        selectedValues.push($(this).attr('id') || '');
    });

    return selectedValues;
}

export function renderDropdownOptions(dropdownId: string, options: { value: string; label: string }[], allowNone: boolean = false): void {
    const dropdown = $(dropdownId);
    dropdown.empty(); // Clear existing options

    if (allowNone) {
        options = [{ value: '', label: '' }, ...options];
    }

    options.forEach((option) => {
        dropdown.append(`<option value="${option.value}">${option.label}</option>`);
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
    setSelectInputValue("#power-source", power.source && power.source.id ? power.source.id.toString() : "6")
    $("#power-conc").prop('checked', power.concentration ?? false)
    
    if (power.type.value == "Tech") {
        $('#align-col').addClass('d-none');
    } else {
        $('#align-col').removeClass('d-none');
    }
    $("#power-level").val(power.level)
    $("#power-duration").val(power.duration)

    setupMDE("power-desc", power.description, true)
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
        flavortext: $("#species-flavortext").val().toString(),
    }

    return species
}

export function fetchClassInputs(): PrimaryClass{
    const source_option = $("#class-source").find(':selected')
    const ability_option = $("#class-ability").find(":selected")
    const caster_option = $("#class-caster").find(":selected")

    const prim_class: PrimaryClass = {
        id: $("#class-edit-form").data('id'),
        value: $("#class-name").val().toString(),
        image_url: $("#class-image").val().toString(),
        source: {
            id: Number(source_option.val()),
            name: source_option.html()
        },
        primary_ability: ability_option.val().toString(),
        hit_die: Number($("#class-hd").val()),
        level_1_hp: $("#class-level1").val().toString(),
        higher_hp: $("#class-higher").val().toString(),
        armor_prof: $("#class-armor").val().toString(),
        weapon_prof: $("#class-weapon").val().toString(),
        tool_prof: $("#class-tool").val().toString(),
        saving_throws: $("#class-saving").val().toString(),
        skill_choices: $("#class-skill").val().toString(),
        archetype_flavor: $("#class-archetype").val().toString(),
        caster_type: caster_option.val() ? {
            id: Number(caster_option.val()),
            value: caster_option.html()
        } 
        : null,
        starting_equipment: getMDEValue("class-equipment"),
        flavortext: getMDEValue("class-flavortext"),
        level_changes: getMDEValue("class-level-changes"),
        features: getMDEValue("class-features"),
    }

    return prim_class
}

export function fetchArchetypInputs(): Archetype{
    const source_option = $("#archetype-source").find(':selected')
    const caster_option = $("#archetype-caster-type").find(":selected")
    let parent_option = null

    if ($("#archetype-parent").length){
        parent_option = $("#archetype-parent").find(':selected')
    }

    const archetype: Archetype = {
        id: $("#archetype-edit-form").data('id'),
        value: $("#archetype-name").val().toString(),
        parent: parent_option ? Number(parent_option.val()) : $("#archetype-edit-form").data('parent'),
        image_url: $("#archetype-image-url").val().toString(),
        caster_type: caster_option.val() ? {
           id: Number(caster_option.val()),
           value: caster_option.html()
        } : null,
        source: {
            id: Number(source_option.val()),
            name: source_option.html()
        },
        flavortext: getMDEValue('archetype-flavortext'),
        level_table: getMDEValue('archetype-level-table')
    }
    return archetype
}

export function defaultEquipmentModal(equip: Equipment): void{
    if (!equip.id){
        $("#equipment-edit-form").removeData("id")
        $("#equipment-delete").addClass("d-none")
    } else {
        $("#equipment-edit-form").data('id', equip.id)
        $("#equipment-delete").removeClass("d-none")
    }

    if (equip.category?.value == 'Armor'){
        $("#ac-col").removeClass("d-none")
        $("#equipment-ac").val(equip.ac)
        $("#stealth-col").removeClass("d-none")
        $("#equipment-stealth-dis").prop('checked', equip.stealth_dis ?? false)
        $("#equipment-properties").val(equip.properties)
        $("#damage-row").addClass("d-none")
    } else if (equip.category?.value == 'Weapon'){
        $("#damage-row").removeClass("d-none")
        $("#equipment-dmg-number-die").val(equip.dmg_number_of_die)
        $("#equipment-dmg-die-type").val(equip.dmg_die_type)
        $("#equipment-dmg-type").val(equip.dmg_type)
        $("#equipment-properties").val(equip.properties)
        $("#ac-col").addClass("d-none")
        $("#stealth-col").addClass("d-none")
    } else {
        $("#damage-row").addClass("d-none")
        $("#ac-col").addClass("d-none")
        $("#stealth-col").addClass("d-none")
        $("#prop-col").addClass("d-none")
    }

    const allSubCats = $("#equipment-edit-form").data('subcategory')

    if (!allSubCats){
        console.error("Missing Sub Categories");
        ToastError("Something went wrong");
        return;
    }

    // Filter and map subtypes based on the item's type
    const subtypes = allSubCats
        .filter((s) => s.parent === equip.category.id) // Filter subtypes by parent type
        .map((s) => ({ value: s.id, label: s.value })); 

    renderDropdownOptions("#equipment-subcategory", subtypes, true)
    setSelectInputValue("#equipment-subcategory", equip.sub_category && equip.sub_category.id ? equip.sub_category.id.toString() : "")
    updateSubCategoryFields()

    $("#equipment-edit-form").data('category', equip.category)
    $("#equipment-name").val(equip.name)
    $("#equipment-description").val(equip.description)
    $("#equipment-cost").val(equip.cost)
    $("#equipment-weight").val(equip.weight)
    setSelectInputValue("#equipment-source", equip.source && equip.source.id ? equip.source.id.toString() : "6");

}

export function fetchEquipmentInputs(): Equipment {
    const source_option = $("#equipment-source").find(":selected")
    const subcat_option = $("#equipment-subcategory").find(":selected")

    const equip: Equipment = {
        id: $("#equipment-edit-form").data('id'),
        name: $("#equipment-name").val().toString(),
        source: {
            id: Number(source_option.val()),
            name: source_option.html()
        },
        description: $("#equipment-description").val().toString(),
        cost: Number($("#equipment-cost").val()),
        weight: Number($("#equipment-weight").val()),
        category: $("#equipment-edit-form").data('category'),
        dmg_number_of_die: Number($("#equipment-dmg-number-die").val()),
        dmg_die_type: Number($("#equipment-dmg-die-type").val()),
        dmg_type: $("#equipment-dmg-type").val().toString(),
        sub_category: subcat_option.val() ? {
            id: Number(subcat_option.val()),
            value: subcat_option.html()
        }: null,
        properties: $("#equipment-properties").val().toString(),
        ac: $("#equipment-ac").val().toString(),
        stealth_dis: $("#equipment-stealth-dis").prop("checked")
    }

    return equip
}

export function defaultItemModal(item: EnhancedItem): void {
    if (!item.id){
        $("#item-edit-form").removeData("id")
        $("#item-delete").addClass("d-none")
    } else {
        $("#item-edit-form").data('id', item.id)
        $("#item-delete").removeClass("d-none")
    }

    $("#item-name").val(item.name)
    $("#item-cost").val(item.cost)
    $("#item-subtype-ft").val(item.subtype_ft)

    const allSubtypes = $("#item-edit-form").data("subtypes");

    if (!allSubtypes) {
        console.error("Missing subtypes");
        ToastError("Something went wrong");
        return;
    }

    // Filter and map subtypes based on the item's type
    const subtypes = allSubtypes
        .filter((s) => s.parent === item.type.id) // Filter subtypes by parent type
        .map((s) => ({ value: s.id, label: s.value })); 

    renderDropdownOptions("#item-subtype", subtypes, true)
    setSelectInputValue("#item-subtype", item.subtype && item.subtype.id ? item.subtype.id.toString() : "")
    updateSubTypeFields()

    setSelectInputValue("#item-source", item.source && item.source.id ? item.source?.id?.toString() : "6")
    setSelectInputValue("#item-rarity", item.rarity && item.rarity.id ? item.rarity.id.toString() : "1")
    $("#item-attunement").prop('checked', item.attunement ?? false)
    $("#item-edit-form").data('type', item.type)

    setupMDE("item-text", item.text, true)
}

export function fetchItemInputs(): EnhancedItem{
    const source_option = $("#item-source").find(":selected")
    const subtype_option = $("#item-subtype").find(":selected")
    const rarity_option = $("#item-rarity").find(":selected")

    const item: EnhancedItem = {
        id: $("#item-edit-form").data('id'),
        name: $("#item-name").val().toString(),
        type: $("#item-edit-form").data('type'),
        rarity: {
            id: Number(rarity_option.val()),
            value: rarity_option.html()
        },
        attunement: $("#item-attunement").prop('checked'),
        text: getMDEValue("item-text"),
        prerequisite: $("#item-prerequisite").val().toString(),
        subtype_ft: $("#item-subtype-ft").val().toString(),
        subtype: subtype_option.val() ? { 
            id: Number(subtype_option.val()),
            value: subtype_option.html(),
        } : null,
        cost: Number($("#item-cost").val()),
        source: {
            id: Number(source_option.val()),
            name: source_option.html()
        }
    }

    return item
}

export function defaultFeatModal(feat: Feat): void{
    if (!feat.id){
        $("#feat-edit-form").removeData("id")
        $("#feat-delete").addClass("d-none")
    } else {
        $("#feat-edit-form").data('id', feat.id)
        $("#feat-delete").removeClass("d-none")
    }

    $("#feat-name").val(feat.name)
    $("#feat-prereq").val(feat.prerequisite)
    setSelectInputValue("#feat-source", feat.source && feat.source.id ? feat.source?.id?.toString() : "6")
    setupMDE("feat-text", feat.text, true)
    prefillCheckboxGroup("feat-attributes", feat.attributes)
}

export function fetchFeatInputs(): Feat{
    const source_option = $("#feat-source").find(":selected")

    const feat: Feat = {
        id: $("#feat-edit-form").data('id'),
        name: $("#feat-name").val().toString(),
        source: {
            id: Number(source_option.val()),
            name: source_option.html()
        },
        attributes: getSelectedCheckboxValues("feat-attributes"),
        prerequisite: $("#feat-prereq").val().toString(),
        text: getMDEValue("feat-text")
    }

    return feat
}