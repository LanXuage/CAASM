export enum APIURL {
  login = '/user/action/login',
  logout = '/user/action/logout',
  getProfile = '/user',
  getMyMenuPerms = '/user/menus',
}

export interface IToken {
  value: string
  expiryTime: Date
}

export interface ILoginParam {
  username: string
  password: string
  captcha: string
  s: string
}

export interface IUser {
  id: string
  username: string
  realName: string
  phone: string
  email: string
  userStatus: string
  updatedAt: Date
  createdAt: Date
}

export interface IMenu {
  permName: string
  permDesc: string
  updatedAt: Date
  createdAt: Date
  submenus: Array<IMenu>
}
