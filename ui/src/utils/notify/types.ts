export enum NotifyType {
  notify = 'notify',
  progressLog = 'progressLog',
}

export interface INotify {
  id?: string
  taskId?: string
  notifyType: NotifyType
  title?: string
  msg?: string
  progress?: number
}
