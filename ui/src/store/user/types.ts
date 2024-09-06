import type { User } from "../../api/user/types"

export interface UserState {
    user?: User
    lang: string
    useHeader: boolean
    token: string
}