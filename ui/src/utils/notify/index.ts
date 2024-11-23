import { isNil } from 'lodash'
import { NotifyType, type INotify } from './types'

export class NotifyQueue {
  url: string
  token: string
  webSocket?: WebSocket
  closed: boolean = false
  realClose: boolean = false
  callbacks: Map<
    NotifyType,
    Map<string, Array<(notify: INotify) => Promise<unknown>>>
  > = new Map()

  constructor(url: string, token: string) {
    console.log('url', url)
    this.url = url
    this.token = token
    this.connect()
  }

  register(
    type: NotifyType,
    callback: (notify: INotify) => Promise<unknown>,
    taskId: string = 'default',
  ) {
    let typeCallbacks = this.callbacks.get(type)
    if (typeCallbacks === undefined) {
      typeCallbacks = new Map()
    }
    let taskCallbacks = typeCallbacks.get(taskId)
    if (taskCallbacks === undefined) {
      taskCallbacks = []
    }
    taskCallbacks.push(callback)
    typeCallbacks.set(taskId, taskCallbacks)
    this.callbacks.set(type, typeCallbacks)
  }

  connect() {
    if (this.webSocket === undefined) {
      this.webSocket = new WebSocket(`${this.url}?t=${this.token}`)
    } else if (
      this.webSocket.readyState === WebSocket.CLOSED ||
      this.webSocket.readyState === WebSocket.CLOSING
    ) {
      try {
        this.webSocket.close()
      } catch {}
      this.webSocket = new WebSocket(`${this.url}?t=${this.token}`)
    }
    this.webSocket.onopen = (ev: Event) => {
      console.log('WebSocket started', ev)
    }
    this.webSocket.onclose = (ev: CloseEvent) => {
      console.log('WebSocket closing', ev)
      if (!this.realClose) {
        setTimeout(() => {
          this.connect()
        }, 1000)
      }
    }
    this.webSocket.onerror = (ev: Event) => {
      console.log('WebSocket error', ev)
      if (!this.realClose) {
        setTimeout(() => {
          this.connect()
        }, 1000)
      }
    }
    this.webSocket.onmessage = (ev: MessageEvent<INotify>) => {
      console.log('WebSocket msg', ev)
      const typeCallbacks = this.callbacks.get(ev.data.notifyType)
      if (typeCallbacks !== undefined) {
        const taskId = ev.data.taskId || 'default'
        const taskCallbacks = typeCallbacks.get(taskId)
        if (taskCallbacks !== undefined) {
          for (const callback of taskCallbacks) {
            callback(ev.data).catch(reason => {
              console.log('reason', reason)
            })
          }
          if (
            ev.data.notifyType === NotifyType.notify &&
            taskId !== 'default'
          ) {
            typeCallbacks.set(taskId, [])
            const progressLogCallbacks = this.callbacks.get(
              NotifyType.progressLog,
            )
            if (progressLogCallbacks !== undefined) {
              progressLogCallbacks.set(taskId, [])
            }
          }
        }
      }
    }
  }

  isClose(): boolean {
    if (!this.closed && !isNil(this.webSocket)) {
      try {
        this.webSocket.send('ping')
      } catch {
        this.closed = true
      }
    } else {
      this.closed = true
    }
    return this.closed
  }

  close() {
    this.realClose = true
  }
}
