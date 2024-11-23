export enum APIURL {
  getFieldCollects = '/field-collects',
}

export interface IFieldCollect {
  id?: string
  collectName: string
  collectDesc?: string
  updatedAt?: Date
  createdAt?: Date
}
