import axios, { AxiosError, type AxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'
import { isNil } from 'lodash'
import { ElNofify } from '../el-notify'
import { APIStatusCode, type APIResponse } from './types'
import i18n from '@/langs'

const http = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_URL,
  timeout: import.meta.env.VITE_APP_TIMEOUT,
})

http.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    const token = userStore.token
    if (isNil(token)) return config
    config.headers[import.meta.env.VITE_APP_TOKEN_KEY] = token
    return config
  },
  (error: AxiosError) => {
    ElNofify.error(`${i18n.global.t('err_network')}: ${error.message}`)
  },
)

http.interceptors.response.use(
  response => {
    const data: APIResponse<string> = response.data
    switch (data.code) {
      case APIStatusCode.Unauthorized:
        const userStore = useUserStore()
        userStore.logoutAndGotoLogin()
        return
      case APIStatusCode.InternalServerError:
        ElNofify.warning(i18n.global.t(data.data))
        return Promise.reject(data.data)
      default:
        return response.data.data
    }
  },
  (error: AxiosError) => {
    if (isNil(error.status)) {
      ElNofify.error(`${i18n.global.t('err_network')}: ${error.message}`)
    } else {
      switch (error.status) {
        case APIStatusCode.Unauthorized:
          const userStore = useUserStore()
          userStore.logoutAndGotoLogin()
          break
        default:
          break
      }
    }
  },
)

export default class HTTP {
  static getHeaders = () => {
    const userStore = useUserStore()
    if (import.meta.env.VITE_APP_TOKEN_KEY && userStore.token !== '') {
      return { [import.meta.env.VITE_APP_TOKEN_KEY]: userStore.token }
    }
    return {}
  }
  static get = <T>(url: string, config?: AxiosRequestConfig) => {
    return http.get<null, T>(url, config)
  }
  static post = <T, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig<D>,
  ) => {
    return http.post<null, T>(url, data, config)
  }
  static delete = <T>(url: string, config?: AxiosRequestConfig) => {
    return http.delete<null, T>(url, config)
  }
  static put = <T, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig<D>,
  ) => {
    return http.put<null, T>(url, data, config)
  }
  static getUri = (config?: AxiosRequestConfig) => {
    return http.getUri(config)
  }
}
