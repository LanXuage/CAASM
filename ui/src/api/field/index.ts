import httpClient from '../../utils/request'
import { Field } from './types'

enum URL {
    fields = '/fields',
    field = '/field'
}

export const getFields = () => httpClient.get<Array<Field>>({ url: URL.fields })
export const addField = (data: Field) => httpClient.post<Field>({ url: URL.field, data })
export const delField = (vid: string) => httpClient.del<boolean>({ url: `${URL.field}/${vid}` })
export const modifyField = (data: Field) => httpClient.put<Field>({ url: `${URL.field}/${data.id}`, data })
export const delBulkFields = (ids: Array<string|undefined>) => httpClient.post<boolean>({ url: `${URL.fields}/bulk`, data: { method: 'DELETE', data: ids } })
export const addBulkFields = (filenames: Array<string>) => httpClient.post<boolean>({ url: `${URL.fields}/bulk`, data: { method: 'POST', data: filenames } })
