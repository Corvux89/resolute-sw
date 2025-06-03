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
    id: number
    name: string
    type: GenericCategory
    pre_requisite?: string
    casttime?: string
    range?: string
    source?: ContentSource
    description?: string
    concentration: boolean
    alignment?: GenericCategory,
    level?: number,
    duration?: string,
    html_desc?: string
}