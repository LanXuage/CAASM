import HTTP from '@/utils/http'
import type {
  ILoginParam, IMenu, IToken, IUser, IUserDetail,
  IUserCreate, IUserUpdate, IUserStatusChange, IUserAssignRoles,
} from './types'
import { APIURL } from './types'

export default class User {
  // Auth
  static login = (loginParam: ILoginParam) =>
    HTTP.post<IToken, ILoginParam>(APIURL.login, loginParam)
  static logout = () => HTTP.get<boolean>(APIURL.logout)
  static getProfile = () => HTTP.get<IUser>(APIURL.getProfile)
  static getMyMenuPerms = () => HTTP.get<Array<IMenu>>(APIURL.getMyMenuPerms)

  // CRUD
  static getUsers = () => HTTP.get<Array<IUser>>(APIURL.users)
  static getUser = (id: string) => HTTP.get<IUserDetail>(`${APIURL.user}/${id}`)
  static createUser = (data: IUserCreate) =>
    HTTP.post<IUser, IUserCreate>(APIURL.user, data)
  static updateUser = (id: string, data: IUserUpdate) =>
    HTTP.put<string, IUserUpdate>(`${APIURL.user}/${id}`, data)
  static deleteUser = (id: string) =>
    HTTP.delete<string>(`${APIURL.user}/${id}`)
  static changeUserStatus = (id: string, data: IUserStatusChange) =>
    HTTP.post<string, IUserStatusChange>(`${APIURL.user}/${id}/status`, data)
  static assignUserRoles = (id: string, data: IUserAssignRoles) =>
    HTTP.post<string, IUserAssignRoles>(`${APIURL.user}/${id}/roles`, data)
}