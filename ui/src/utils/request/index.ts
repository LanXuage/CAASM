import axios,
{
    AxiosInstance,
    InternalAxiosRequestConfig,
    AxiosRequestConfig,
    AxiosError,
    AxiosResponse,
    HttpStatusCode
} from 'axios'
import { ResponseModel } from './types'
import { useUserStore } from '../../store/user'
import { useRouter } from 'vue-router'

class HttpRequest {
    service: AxiosInstance

    constructor() {
        this.service = axios.create({
            baseURL: import.meta.env.VITE_APP_BASE_URL,
            timeout: 30 * 1000
        });

        this.service.interceptors.request.use(
            (config: InternalAxiosRequestConfig) => {
                const userStore = useUserStore()
                if (import.meta.env.VITE_APP_TOKEN_KEY && userStore.token) {
                    config.headers[import.meta.env.VITE_APP_TOKEN_KEY] = userStore.token
                }
                return config
            },
            (error: AxiosError) => {
                console.log('requestError: ', error)
                return Promise.reject(error);
            },
            {
                synchronous: false,
                runWhen: ((config: InternalAxiosRequestConfig) => {
                    console.log('config', config)
                    return true
                })
            }
        );

        this.service.interceptors.response.use(
            (response: AxiosResponse<ResponseModel>): AxiosResponse['data'] => {
                const userStore = useUserStore()
                const router = useRouter()
                const { data } = response
                const { code } = data
                if (code) {
                    if (code != HttpStatusCode.Ok) {
                        switch (code) {
                            case HttpStatusCode.NotFound:
                                // the method to handle this code
                                break;
                            case HttpStatusCode.Unauthorized:
                                // the method to handle this code
                                userStore.token = undefined
                                userStore.user = undefined
                                router.push('/login')
                                break;
                            default:
                                break;
                        }
                        return Promise.reject(data.msg)
                    } else {
                        return data
                    }
                } else {
                    return Promise.reject('Error! code missing!')
                }
            },
            (error: any) => {
                return Promise.reject(error);
            }
        );
    }

    request<T = any>(config: AxiosRequestConfig): Promise<T> {
        return new Promise((resolve, reject) => {
            try {
                this.service.request<ResponseModel<T>>(config)
                    .then((res: AxiosResponse['data']) => {
                        resolve((res as ResponseModel<T>).data);
                    })
                    .catch((err) => {
                        reject(err)
                    })
            } catch (err) {
                return Promise.reject(err)
            }
        })
    }

    get<T = any>(config: AxiosRequestConfig): Promise<T> {
        return this.request({ method: 'GET', ...config })
    }
    post<T = any>(config: AxiosRequestConfig): Promise<T> {
        return this.request({ method: 'POST', ...config })
    }
    put<T = any>(config: AxiosRequestConfig): Promise<T> {
        return this.request({ method: 'PUT', ...config })
    }
    del<T = any>(config: AxiosRequestConfig): Promise<T> {
        return this.request({ method: 'DELETE', ...config })
    }
}

const httpRequest = new HttpRequest()

export default httpRequest
