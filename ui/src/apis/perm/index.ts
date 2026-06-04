import HTTP from '@/utils/http'
import type {
  IPerm, IPermCreate, IPermUpdate, IPermInclude,
  IPermGroup, IPermGroupCreate,
} from './types'
import { APIURL } from './types'

export default class Perm {
  static getPerms = () => HTTP.get<Array<IPerm>>(APIURL.perms)
  static getPerm = (id: string) => HTTP.get<IPerm>(`${APIURL.perm}/${id}`)
  static createPerm = (data: IPermCreate) =>
    HTTP.post<IPerm, IPermCreate>(APIURL.perm, data)
  static updatePerm = (id: string, data: IPermUpdate) =>
    HTTP.put<string, IPermUpdate>(`${APIURL.perm}/${id}`, data)
  static deletePerm = (id: string) =>
    HTTP.delete<string>(`${APIURL.perm}/${id}`)
  static setInclude = (id: string, data: IPermInclude) =>
    HTTP.post<string, IPermInclude>(`${APIURL.perm}/${id}/include`, data)
  static getPermGroups = () => HTTP.get<Array<IPermGroup>>(APIURL.permGroups)
  static createPermGroup = (data: IPermGroupCreate) =>
    HTTP.post<IPermGroup, IPermGroupCreate>(APIURL.permGroup, data)
}