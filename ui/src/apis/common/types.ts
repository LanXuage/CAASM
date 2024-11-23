import type { UploadUserFile } from 'element-plus'

export enum APIURL {
  captcha = '/captcha',
  upload = '/upload',
  notify = '/notify',
}

export enum BulkMethod {
  DELETE = 'DELETE',
  POST = 'POST',
  PUT = 'PUT',
}

export interface IBulkForm {
  fileLists: Array<UploadUserFile>
}
