import httpClient from '../../utils/request'
import { LoginParam, Menu, User } from './types'

enum URL {
    login = '/user/action/login',
    logout = '/user/action/logout',
    getProfile = '/user',
    getMyMenuPerms = '/user/menus'
}

export const login = (loginParam: LoginParam) => httpClient.post<string>({ url: URL.login, data: loginParam })
export const logout = () => httpClient.get<boolean>({ url: URL.logout})
export const getProfile = () => httpClient.get<User>({ url: URL.getProfile })
export const getMyMenuPerms = () => httpClient.get<Array<Menu>>({ url: URL.getMyMenuPerms })

