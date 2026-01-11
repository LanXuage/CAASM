import { readFileSync } from 'fs'
import { MockMethod } from 'vite-plugin-mock'
import type { MockResponseOpt } from './types'
import type { ILoginParam } from '../src/apis/user/types'
import { APIStatusCode } from '../src/utils/http/types'
import CryptoJS from 'crypto-js'

export default [
  {
    url: '/mock/v1/captcha',
    method: 'get',
    rawResponse: (req, resp) => {
      resp.setHeader('Content-Type', 'image/png')
      const data = readFileSync('./mock/captcha.png')
      resp.end(data)
    },
  },
  {
    url: '/mock/v1/user/action/login',
    method: 'post',
    response: (opt: MockResponseOpt<ILoginParam>) => {
      if (opt.body.captcha.toLowerCase() !== '65rhw')
        return {
          code: APIStatusCode.InternalServerError,
          data: 'invalid_captcha',
        }
      if (
        opt.body.username === 'admin' &&
        opt.body.password ===
          CryptoJS.SHA256(
            `${opt.body.s}_${opt.body.captcha}_${opt.body.username}_admin`,
          ).toString()
      )
        return {
          code: APIStatusCode.Ok,
          data: {
            value: 'fakeToken',
            expiryTime: new Date(1742529942900),
          },
        }
      return {
        code: 500,
        data: 'invalid_username_or_password',
      }
    },
  },
  {
    url: '/mock/v1/user',
    method: 'get',
    response: {
      code: 200,
      data: {
        id: 'c0c5e8cfab9a5bdef54a53c43663483e',
        username: 'admin',
        realName: '',
        phone: '',
        email: '',
        userStatus: 0,
        updatedAt: '2024-09-25T22:38:11+08:00',
        createdAt: '2024-09-25T22:38:11+08:00',
      },
    },
  },
  {
    url: '/mock/v1/user/menus',
    method: 'get',
    response: {
      code: 200,
      data: [
        {
          id: '0b26f2bfe640233f0085b6f5b042bd24',
          permName: 'asset_inquiry',
          permDesc: 'asset_inquiry_desc',
          updatedAt: '2024-09-05T20:00:01+08:00',
          createdAt: '2024-09-05T20:00:01+08:00',
          submenus: [
            {
              id: '9fc175c85b90e192674b7e5024e1d90b',
              permName: 'real_time_query',
              permDesc: 'real_time_query_desc',
              updatedAt: '2024-09-05T20:00:06+08:00',
              createdAt: '2024-09-05T20:00:06+08:00',
              submenus: [],
            },
            {
              id: 'aa2fcc6836fa73c3cc21f8ca204742a1',
              permName: 'export_record',
              permDesc: 'export_record_desc',
              updatedAt: '2024-09-05T20:00:07+08:00',
              createdAt: '2024-09-05T20:00:07+08:00',
              submenus: [],
            },
            {
              id: '1f34504f2ec518edd0cd3db1f7f0736f',
              permName: 'query_scenario',
              permDesc: 'query_scenario_desc',
              updatedAt: '2024-09-05T20:00:08+08:00',
              createdAt: '2024-09-05T20:00:08+08:00',
              submenus: [],
            },
            {
              id: 'ea12e71f48e8f6e9ff61234e1fb41453',
              permName: 'standing_book',
              permDesc: 'standing_book_desc',
              updatedAt: '2024-09-05T20:00:09+08:00',
              createdAt: '2024-09-05T20:00:09+08:00',
              submenus: [],
            },
          ],
        },
        {
          id: '7168bea862daf18e91c7143806cced68',
          permName: 'user_permission',
          permDesc: 'user_permission_desc',
          updatedAt: '2024-09-05T20:00:02+08:00',
          createdAt: '2024-09-05T20:00:02+08:00',
          submenus: [
            {
              id: '0eadc11a3ea6d6f89662f973e0711afb',
              permName: 'user_management',
              permDesc: 'user_management_desc',
              updatedAt: '2024-09-05T20:00:10+08:00',
              createdAt: '2024-09-05T20:00:10+08:00',
              submenus: [],
            },
            {
              id: 'c41f9fa8efb7bc5f700cddb21d3774e3',
              permName: 'role_management',
              permDesc: 'role_management_desc',
              updatedAt: '2024-09-05T20:00:11+08:00',
              createdAt: '2024-09-05T20:00:11+08:00',
              submenus: [],
            },
            {
              id: 'bb156cc6a0c6304190ab60d546bfb104',
              permName: 'perm_management',
              permDesc: 'perm_management_desc',
              updatedAt: '2024-09-05T20:00:12+08:00',
              createdAt: '2024-09-05T20:00:12+08:00',
              submenus: [],
            },
          ],
        },
        {
          id: '84313ecfb89e8b7a87531e9788d74cea',
          permName: 'field_model',
          permDesc: 'field_model_desc',
          updatedAt: '2024-09-05T20:00:03+08:00',
          createdAt: '2024-09-05T20:00:03+08:00',
          submenus: [
            {
              id: 'a2ae3f9ff92564fffcf87df6bda4c7bf',
              permName: 'field_management',
              permDesc: 'field_management_desc',
              updatedAt: '2024-09-05T20:00:13+08:00',
              createdAt: '2024-09-05T20:00:13+08:00',
              submenus: [],
            },
            {
              id: '83f638077d97bd078c5efe6c528b00a9',
              permName: 'field_collect',
              permDesc: 'field_collect_desc',
              updatedAt: '2024-09-05T20:00:14+08:00',
              createdAt: '2024-09-05T20:00:14+08:00',
              submenus: [],
            },
            {
              id: 'b05a31e9a360262e02fa1c17c49a41fd',
              permName: 'model_management',
              permDesc: 'model_management_desc',
              updatedAt: '2024-09-05T20:00:15+08:00',
              createdAt: '2024-09-05T20:00:15+08:00',
              submenus: [],
            },
            {
              id: '9391b7fb61ff567fc91f88817918760d',
              permName: 'graph_management',
              permDesc: 'graph_management_desc',
              updatedAt: '2024-09-05T20:00:16+08:00',
              createdAt: '2024-09-05T20:00:16+08:00',
              submenus: [],
            },
          ],
        },
        {
          id: 'cd3a41454f3ac413c965e970707b32a9',
          permName: 'adapter_task',
          permDesc: 'adapter_task_desc',
          updatedAt: '2024-09-05T20:00:04+08:00',
          createdAt: '2024-09-05T20:00:04+08:00',
          submenus: [
            {
              id: '08943ae01d70e6769cfd5d3109edb507',
              permName: 'adapter_management',
              permDesc: 'adapter_management_desc',
              updatedAt: '2024-09-05T20:00:17+08:00',
              createdAt: '2024-09-05T20:00:17+08:00',
              submenus: [],
            },
            {
              id: '93e838305d987e1828bf1443bbfee4f5',
              permName: 'mapping_management',
              permDesc: 'mapping_management_desc',
              updatedAt: '2024-09-05T20:00:18+08:00',
              createdAt: '2024-09-05T20:00:18+08:00',
              submenus: [],
            },
            {
              id: '3791b8766e4725bd07b4c6f853e6017e',
              permName: 'plan_management',
              permDesc: 'plan_management_desc',
              updatedAt: '2024-09-05T20:00:19+08:00',
              createdAt: '2024-09-05T20:00:19+08:00',
              submenus: [],
            },
            {
              id: 'cdd98630e00844249bbe2310474fe47d',
              permName: 'task_management',
              permDesc: 'task_management_desc',
              updatedAt: '2024-09-05T20:00:20+08:00',
              createdAt: '2024-09-05T20:00:20+08:00',
              submenus: [],
            },
          ],
        },
        {
          id: '805ea4ac00fb993ea973babadee075e5',
          permName: 'system_settings',
          permDesc: 'system_settings_desc',
          updatedAt: '2024-09-05T20:00:05+08:00',
          createdAt: '2024-09-05T20:00:05+08:00',
          submenus: [
            {
              id: '7a63c9ec9ccf250f1b699cb24ea23157',
              permName: 'license',
              permDesc: 'license_desc',
              updatedAt: '2024-09-05T20:00:21+08:00',
              createdAt: '2024-09-05T20:00:21+08:00',
              submenus: [],
            },
            {
              id: '317623234281174999944bd607c7ecb5',
              permName: 'about',
              permDesc: 'about_desc',
              updatedAt: '2024-09-05T20:00:22+08:00',
              createdAt: '2024-09-05T20:00:22+08:00',
              submenus: [],
            },
          ],
        },
      ],
    },
  },
] as MockMethod[]
