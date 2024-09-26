import httpClient from '../../utils/request'
import { FieldCollect } from './types'

enum URL {
    getFieldCollects = '/field-collects'
}

export const getFieldCollects = () => httpClient.get<Array<FieldCollect>>({ url: URL.getFieldCollects })
