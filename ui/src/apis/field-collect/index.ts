import HTTP from '../../utils/http'
import { APIURL, type IFieldCollect } from './types'

export default class FieldCollect {
  static getFieldCollects = () =>
    HTTP.get<Array<IFieldCollect>>(APIURL.getFieldCollects)
}
