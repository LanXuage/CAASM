import HTTP from '@/utils/http'
import type {
  IRole, IRoleDetail, IRoleCreate, IRoleUpdate,
  IRoleAssignPerms, IRoleAssignUsers, IRoleInherit, IRoleMutex,
} from './types'
import { APIURL } from './types'

export default class Role {
  static getRoles = () => HTTP.get<Array<IRole>>(APIURL.roles)
  static getRole = (id: string) => HTTP.get<IRoleDetail>(`${APIURL.role}/${id}`)
  static createRole = (data: IRoleCreate) =>
    HTTP.post<IRole, IRoleCreate>(APIURL.role, data)
  static updateRole = (id: string, data: IRoleUpdate) =>
    HTTP.put<string, IRoleUpdate>(`${APIURL.role}/${id}`, data)
  static deleteRole = (id: string) =>
    HTTP.delete<string>(`${APIURL.role}/${id}`)
  static assignPerms = (id: string, data: IRoleAssignPerms) =>
    HTTP.post<string, IRoleAssignPerms>(`${APIURL.role}/${id}/perms`, data)
  static assignUsers = (id: string, data: IRoleAssignUsers) =>
    HTTP.post<string, IRoleAssignUsers>(`${APIURL.role}/${id}/users`, data)
  static setInherit = (id: string, data: IRoleInherit) =>
    HTTP.post<string, IRoleInherit>(`${APIURL.role}/${id}/inherit`, data)
  static setMutex = (id: string, data: IRoleMutex) =>
    HTTP.post<string, IRoleMutex>(`${APIURL.role}/${id}/mutex`, data)
}