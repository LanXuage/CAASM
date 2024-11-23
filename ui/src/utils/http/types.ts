import { HttpStatusCode } from 'axios'

export enum HttpStatusCodeExt {
  NAME_OR_PASSWORD = 444,
}

export type IAPIStatusCode = HttpStatusCode | HttpStatusCodeExt

export const APIStatusCode = {
  ...HttpStatusCode,
  ...HttpStatusCodeExt,
}

export interface APIResponse<T = unknown> {
  code: IAPIStatusCode
  data: T
}
