import HTTP from '@/utils/http'
import type { ILoginParam, IMenu, IToken, IUser } from './types'
import { APIURL } from './types'

export default class User {
  static login = (loginParam: ILoginParam) =>
    HTTP.post<IToken, ILoginParam>(APIURL.login, loginParam)
  static logout = () => HTTP.get<boolean>(APIURL.logout)
  static getProfile = () => HTTP.get<IUser>(APIURL.getProfile)
  static getMyMenuPerms = () => HTTP.get<Array<IMenu>>(APIURL.getMyMenuPerms)
}
