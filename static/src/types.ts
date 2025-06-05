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