export enum APIURL {
  // Auth
  login = '/user/action/login',
  logout = '/user/action/logout',
  getProfile = '/user',
  getMyMenuPerms = '/user/menus',
  // User management CRUD
  users = '/users',
  user = '/user',
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
  userStatus: number
  updatedAt: Date
  createdAt: Date
}

export interface IUserDetail extends IUser {
  roles: Array<string>
}

export interface IUserCreate {
  username: string
  password: string
  realName?: string
  phone?: string
  email?: string
  userStatus?: number
}

export interface IUserUpdate {
  realName?: string
  phone?: string
  email?: string
  userStatus?: number
}

export interface IUserStatusChange {
  userStatus: number
}

export interface IUserAssignRoles {
  roleIds: Array<string>
}

export interface IMenu {
  permName: string
  permDesc: string
  updatedAt: Date
  createdAt: Date
  submenus: Array<IMenu>
}