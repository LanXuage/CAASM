import { NotifyQueue } from '@/utils/notify'
import type { IUser, IToken, IMenu } from '@/apis/user/types'

export type LangType = 'zh-cn' | 'zh' | 'zh-tw' | 'tw' | 'en'
export type ThemeType = 'dark' | 'light'

export interface IUserState {
  user?: IUser
  lang: LangType
  theme: ThemeType
  useHeader: boolean
  notifyQueue?: NotifyQueue
  token?: IToken
  menus?: Array<IMenu>
}
