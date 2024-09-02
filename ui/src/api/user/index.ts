import httpClient from '../../utils/request'
import { LoginParam } from './types'

enum URL {
    login = '/user/action/login'
}

export const login = (loginParam: LoginParam) => httpClient.post<string>({ url: URL.login, data: loginParam })

