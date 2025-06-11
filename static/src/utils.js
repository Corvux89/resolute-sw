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
export function setupMDE(element, default_text) {
    const textarea = document.getElementById(element);
    if (!textarea)
        return;
    if (window[element] && typeof window[element].toTextArea === "function") {
        window[element].toTextArea();
    }
    if (default_text)
        $(`#${element}`).val(default_text);
    //@ts-expect-error This is pulled in from a parent and no import needed
    window[element] = new EasyMDE({
        element: document.getElementById(element),
        autofocus: true,
        sideBySideFullscreen: false,
        autoRefresh: { delay: 300 },
        maxHeight: "20vh",
        toolbar: ["undo", "redo", "|", "bold", "italic", "heading", "|", "code", "quote", "unordered-list", "ordered-list", "|", "link"]
    });
}
export function getMDEValue(element) {
    if (window[element] && typeof window[element].value === "function")
        return window[element].value();
    return "";
}
export function updateClearAllFiltersButton() {
    if ($('#active-filters .badge').length > 0 || $("#filter-search").val() != "") {
        $('#clear-all-filters').removeClass('d-none');
    }
    else {
        $('#clear-all-filters').addClass('d-none');
    }
}
export function setupTableFilters(table_name, exceptions, initialFilters) {
    const table = $(table_name).DataTable();
    // // Apply initial filters and update dropdown/badges
    // if (initialFilters) {
    //     Object.entries(initialFilters).forEach(([colIdx, filterValue]) => {
    //         // Apply the filter to the table
    //         table.column(Number(colIdx)).search(filterValue || '').draw();
    //         // Mark the corresponding dropdown item as active
    //         const submenuID = `submenu-${colIdx}`;
    //         const $submenuItem = $(`#${submenuID} .filter-option`).filter(function () {
    //             return $(this).data('value').toString().toLowerCase() === filterValue.toLowerCase();
    //         });
    //         if ($submenuItem.length) {
    //             $submenuItem.addClass('active');
    //         }
    //     });
    // }
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
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = render;
                    return tempDiv.textContent.split(",")[0] ?? "";
                }
                return typeof raw === "string" ? raw.split(",")[0] : raw.toString();
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
        // Reapply active state for dropdown items based on initial filters
        if (initialFilters) {
            Object.entries(initialFilters).forEach(([colIdx, filterValue]) => {
                if (!filterValue)
                    return;
                const submenuID = `submenu-${colIdx}`;
                const $submenuItem = $(`#${submenuID} .filter-option`).filter(function () {
                    return $(this).data('value').toString().toLowerCase() === filterValue.toLowerCase();
                });
                if ($submenuItem.length) {
                    $submenuItem.trigger('click');
                }
            });
        }
    });
    if ($("#filter-search").length) {
        $('#filter-search').on('input', function () {
            const params = new URLSearchParams(window.location.search);
            table.search($(this).val().toString()).draw();
            updateClearAllFiltersButton();
            if (params.has('name') && $(this).val() == "") {
                table.column(0).search("").draw();
            }
        });
    }
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
    setupMDE("power-desc", power.description);
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
    power.description = getMDEValue("power-desc");
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
export function fetchSpeciesInputs() {
    const source_option = $("#species-source").find(':selected');
    const size_option = $("#species-size").find(':selected');
    const species = {
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
    };
    return species;
}
export function fetchClassInputs() {
    const source_option = $("#class-source").find(':selected');
    const ability_option = $("#class-ability").find(":selected");
    const caster_option = $("#class-caster").find(":selected");
    const prim_class = {
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
    };
    return prim_class;
}
export function fetchArchetypInputs() {
    const source_option = $("#archetype-source").find(':selected');
    const caster_option = $("#archetype-caster-type").find(":selected");
    let parent_option = null;
    if ($("#archetype-parent").length) {
        parent_option = $("#archetype-source").find(':selected');
    }
    const archetype = {
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
    };
    console.log(archetype);
    return archetype;
}
export function defaultEquipmentModal(equip) {
    if (!equip.id) {
        $("#equipment-edit-form").removeData("id");
        $("#equipment-delete").addClass("d-none");
    }
    else {
        $("#equipment-edit-form").data('id', equip.id);
        $("#equipment-delete").removeClass("d-none");
    }
    if (equip.category?.value == 'Armor') {
        setSelectInputValue("#equipment-armor-class", equip.armor_class?.id?.toString() ?? "");
        $("#armor-class-col").removeClass("d-none");
        $("#ac-col").removeClass("d-none");
        $("#equipment-ac").val(equip.ac);
        $("#stealth-col").removeClass("d-none");
        $("#equipment-stealth-dis").prop('checked', equip.stealth_dis ?? false);
        $("#equipment-properties").val(equip.properties);
        $("#weapon-class-col").addClass("d-none");
        $("#damage-row").addClass("d-none");
    }
    else if (equip.category?.value == 'Weapon') {
        setSelectInputValue("#equipment-weapon-class", equip.weapon_class?.id?.toString() ?? "");
        $("#weapon-class-col").removeClass("d-none");
        $("#damage-row").removeClass("d-none");
        $("#equipment-dmg-number-die").val(equip.dmg_number_of_die);
        $("#equipment-dmg-die-type").val(equip.dmg_die_type);
        $("#equipment-dmg-type").val(equip.dmg_type);
        $("#equipment-properties").val(equip.properties);
        $("#armor-class-col").addClass("d-none");
        $("#ac-col").addClass("d-none");
        $("#stealth-col").addClass("d-none");
    }
    else {
        $("#weapon-class-col").addClass("d-none");
        $("#damage-row").addClass("d-none");
        $("#armor-class-col").addClass("d-none");
        $("#ac-col").addClass("d-none");
        $("#stealth-col").addClass("d-none");
        $("#prop-col").addClass("d-none");
    }
    $("#equipment-edit-form").data('category', equip.category);
    $("#equipment-name").val(equip.name);
    $("#equipment-description").val(equip.description);
    $("#equipment-cost").val(equip.cost);
    $("#equipment-weight").val(equip.weight);
    setSelectInputValue("#equipment-source", equip.source?.id?.toString() ?? "6");
}
export function fetchEquipmentInputs() {
    const source_option = $("#equipment-source").find(":selected");
    const weapon_option = $("#equipment-weapon-class").find(":selected");
    const armor_option = $("#equipment-armor-class").find(":selected");
    const equip = {
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
        dmg_number_of_die: Number($("#equipment-dmg-number.die").val()),
        dmg_die_type: Number($("#equipment-dmg-tie-type").val()),
        dmg_type: $("#equipment-dmg-type").val().toString(),
        weapon_class: weapon_option.val() ? {
            id: Number(weapon_option.val()),
            value: weapon_option.html()
        } : null,
        armor_class: armor_option.val() ? {
            id: Number(armor_option.val()),
            value: armor_option.html()
        } : null,
        properties: $("#equipment-properties").val().toString(),
        ac: $("#equipment-ac").val().toString(),
        stealth_dis: $("#equipment-stealth-dis").prop("checked")
    };
    return equip;
}
