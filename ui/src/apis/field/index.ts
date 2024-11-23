import HTTP from '@/utils/http'
import { APIURL, type IField } from './types'
import { BulkMethod } from '../common/types'

export default class Field {
  static getFields = () => HTTP.get<Array<IField>>(APIURL.fields)
  static addField = (data: IField) =>
    HTTP.post<IField, IField>(APIURL.field, data)
  static delField = (vid: string) =>
    HTTP.delete<boolean>(`${APIURL.field}/${vid}`)
  static modifyField = (data: IField) =>
    HTTP.put<IField, IField>(`${APIURL.field}/${data.id}`, data)
  static delBulkFields = (ids: Array<string | undefined>) =>
    HTTP.post<string>(`${APIURL.fields}/bulk`, {
      method: BulkMethod.DELETE,
      data: ids,
    })
  static addBulkFields = (filenames: Array<string>) =>
    HTTP.post<string>(`${APIURL.fields}/bulk`, {
      method: BulkMethod.POST,
      data: filenames,
    })
}
