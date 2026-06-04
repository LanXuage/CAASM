export enum APIURL {
  roles = '/roles',
  role = '/role',
}

export interface IRole {
  id: string
  roleName: string
  roleDesc: string
  updatedAt: Date
  createdAt: Date
}

export interface IRoleDetail extends IRole {
  permIds: Array<string>
  userIds: Array<string>
}

export interface IRoleCreate {
  roleName: string
  roleDesc?: string
}

export interface IRoleUpdate {
  roleName?: string
  roleDesc?: string
}

export interface IRoleAssignPerms {
  permIds: Array<string>
}

export interface IRoleAssignUsers {
  userIds: Array<string>
}

export interface IRoleInherit {
  parentRoleId: string
}

export interface IRoleMutex {
  mutexRoleId: string
}