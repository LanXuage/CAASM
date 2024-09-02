export interface ResponseModel<T = any> {
    code: number | string
    msg: string | null
    data: T
}