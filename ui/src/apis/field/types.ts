export enum APIURL {
  fields = '/fields',
  field = '/field',
}

export interface IField {
  fieldName: string
  fieldDesc: string
  id?: string
  collects?: Array<string>
  updatedAt?: Date
  createdAt?: Date
  checked?: unknown
}
