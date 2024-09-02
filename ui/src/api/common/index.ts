import httpRequest from '../../utils/request'

enum URL {
    captcha = '/captcha'
}

export const getCaptcha = (s: string) => httpRequest.get<string>({ url: URL.captcha, params: { s } });