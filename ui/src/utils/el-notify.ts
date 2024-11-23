import { ElNotification } from 'element-plus'
import type { NotificationParams } from 'element-plus/es/components'

export class ElNofify {
  static options: NotificationParams = {}

  static do = (type: 'success' | 'info' | 'warning' | 'error', msg: string) => {
    const options: NotificationParams = {}
    Object.assign(options, this.options, { type: type, message: msg })
    return ElNotification(options)
  }

  static success = (msg: string) => {
    return this.do('success', msg)
  }

  static info = (msg: string) => {
    return this.do('info', msg)
  }

  static warning = (msg: string) => {
    return this.do('warning', msg)
  }

  static error = (msg: string) => {
    return this.do('error', msg)
  }
}
