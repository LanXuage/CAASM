import { defineStore } from 'pinia'
import type { IUserState, LangType } from './types'
import i18n from '@/langs'
import { NotifyQueue } from '../../utils/notify'
import { APIURL } from '@/apis/common/types'
import { computed, reactive, watch } from 'vue'
import zhCN from 'element-plus/es/locale/lang/zh-cn'
import zhTW from 'element-plus/es/locale/lang/zh-tw'
import en from 'element-plus/es/locale/lang/en'
import type { IMenu, IToken } from '@/apis/user/types'
import router from '@/router'
import type { Language } from 'element-plus/es/locales'
import { isNil } from 'lodash'
import { APIUser } from '@/apis'
import { ElNofify } from '@/utils/el-notify'
import http from '@/utils/http'
import { ROUTES } from '@/router/routes'

const LANG_MAP: Record<LangType | 'default', Language> = {
  'zh-cn': zhCN,
  zh: zhCN,
  'zh-tw': zhTW,
  tw: zhTW,
  en: en,
  default: zhCN,
}

export const useUserStore = defineStore(
  'user',
  () => {
    const userState = reactive<IUserState>({
      lang: 'zh-cn',
      useHeader: true,
      theme: window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light',
    })

    const token = computed(() => {
      if (
        isNil(userState.token) ||
        isNil(userState.token.value) ||
        isNil(userState.token.expiryTime) ||
        userState.token.expiryTime > new Date()
      ) {
        return undefined
      }
      return userState.token.value
    })

    const locale = computed(() => LANG_MAP[userState.lang] || LANG_MAP.default)

    const tryCloseNotifyQueue = () => {
      if (isNil(userState.notifyQueue)) return
      try {
        userState.notifyQueue.close()
      } catch (err) {
        console.warn('尝试关闭通知队列失败', err)
      }
    }

    const checkAndAddRoutes = (path: string, menus: Array<IMenu>): boolean => {
      let hasRoute = false
      for (const menu of menus) {
        const route = ROUTES[menu.permName]
        if (!isNil(route)) {
          router.addRoute(route)
          if (
            route.path === path ||
            (!isNil(route.alias) && route.alias.indexOf(path) > -1)
          )
            hasRoute = true
        }
        if (isNil(menu.submenus)) continue
        hasRoute = checkAndAddRoutes(path, menu.submenus) || hasRoute
      }
      return hasRoute
    }

    const hasRoute = async (path: string) => {
      if (isNil(userState.token)) return
      tryCloseNotifyQueue()
      try {
        userState.notifyQueue = new NotifyQueue(
          http.getUri({ url: APIURL.notify }),
          userState.token.value,
        )
        userState.user = await APIUser.getProfile()
        userState.menus = await APIUser.getMyMenuPerms()
        router.addRoute(ROUTES.overview)
        return (
          checkAndAddRoutes(path, userState.menus) ||
          path === ROUTES.overview.path ||
          (!isNil(ROUTES.overview.alias) &&
            ROUTES.overview.alias.indexOf(path) > -1)
        )
      } catch (msg) {
        ElNofify.error(i18n.global.t(msg as string))
      }
    }

    const setToken = (token: IToken) => {
      userState.token = token
      router.push('/')
    }

    const logoutAndGotoLogin = () => {
      userState.token = undefined
      userState.user = undefined
      tryCloseNotifyQueue()
      userState.notifyQueue = undefined
      router.push('/login')
    }

    watch(
      () => userState.lang,
      (value, old) => {
        if (value !== old) i18n.global.locale.value = value
      },
    )

    watch(
      () => userState.theme,
      (value, old) => {
        if (value !== old) {
          document.documentElement.classList.remove(old)
          document.documentElement.classList.add(value)
        }
      },
    )

    // Init theme
    document.documentElement.classList.add(userState.theme)

    return {
      userState,
      token,
      locale,
      setToken,
      logoutAndGotoLogin,
      hasRoute,
    }
  },
  {
    persist: [
      {
        pick: [
          'userState.token',
          'userState.lang',
          'userState.useHeader',
          'userState.theme',
        ],
        storage: localStorage,
      },
      {
        pick: ['userState'],
        omit: ['userState.notifyQueue'],
        storage: sessionStorage,
      },
    ],
  },
)
