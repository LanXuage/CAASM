export enum APIURL {
  perms = '/perms',
  perm = '/perm',
  permGroups = '/perm-groups',
  permGroup = '/perm-group',
}

export interface IPerm {
  id: string
  permName: string
  permDesc: string
  updatedAt: Date
  createdAt: Date
}

export interface IPermCreate {
  permName: string
  permDesc?: string
  permGroupId?: string
}

export interface IPermUpdate {
  permName?: string
  permDesc?: string
}

export interface IPermInclude {
  childPermId: string
}

export interface IPermGroup {
  id: string
  permGroupName: string
  permGroupDesc: string
  updatedAt: Date
  createdAt: Date
}

export interface IPermGroupCreate {
  permGroupName: string
  permGroupDesc?: string
}