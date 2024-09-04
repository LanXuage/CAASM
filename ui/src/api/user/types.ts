export interface LoginParam {
    username: string
    password: string
    captcha: string
    s: string
}

export interface User {
    id: string
    username: string
    realName: string
    phone: string
    email: string
    userStatus: string
    updatedAt: Date
    createdAt: Date
}