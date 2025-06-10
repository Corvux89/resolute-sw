interface GenericCategory {
    id: number
    value: string
}

interface ContentSource {
    id: number
    name: string
    abbreviation?: string
}

export interface Power {
    id?: string
    name?: string
    type?: GenericCategory
    pre_requisite?: string
    casttime?: string
    range?: string
    source?: ContentSource
    description?: string
    concentration?: boolean,
    alignment?: GenericCategory,
    level?: number,
    duration?: string,
    html_desc?: string
}

export interface Species {
    id?: number
    value: string
    distinctions?: string
    eye_options?: string
    flavortext?: string
    hair_options?: string
    height_average?: string
    height_mod?: string
    homeworld?: string
    html_flavortext?: string
    image_url?: string
    language?: string
    size?: string
    skin_options?: string
    source: ContentSource
    traits?: string
    html_traits?: string
    weight_average?: string
    weight_mod?: string
}

export interface PrimaryClass {
    id?: number
    value: string
    summary?: string
    primary_ability?: string
    flavortext?: string
    level_changes?: string
    hit_die?: number
    level_1_hp?: string
    higher_hp?: string
    armor_prof?: string
    weapon_prof?: string
    tool_prof?: string
    saving_throws?: string
    skill_choices?: string
    starting_equipment?: string
    features?: string
    archetype_flavor?: string
    image_url?: string
    html_flavortext?: string
    html_features?: string
    html_level_table?: string
    html_starting_equip?: string
    source?: ContentSource
    caster_type?: GenericCategory
}

export interface Archetype {
    id?: number
    value: string
    parent: number
    caster_type?: GenericCategory
    flavortext?: string
    html_flavortext?: string
    level_table?: string
    html_level_table?: string
    image_url?: string
    parent_name?: string
    source?: ContentSource
}

export interface Equipment {
    id?: string
    name: string
    source?: ContentSource
    description?: string
    cost?: number
    weight?: number
    category?: GenericCategory
    dmg_number_of_die?: number
    dmg_die_type?: number
    dmg_type?: string
    weapon_class?: GenericCategory
    armor_class?: GenericCategory
    properties?: string
    ac?: string
    stealth_dis?: boolean
}