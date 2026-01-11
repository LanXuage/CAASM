import { Recordable } from 'vite-plugin-mock'

export interface MockResponseOpt<T = Recordable, D = Recordable> {
  url: Recordable
  body: T
  query: D
  headers: Recordable
}
