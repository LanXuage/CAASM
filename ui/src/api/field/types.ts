export interface Field {
    fieldName: string
    fieldDesc: string
    id?: string
    collects?: Array<string>
    updatedAt?: Date
    createdAt?: Date
    checked?: any
}