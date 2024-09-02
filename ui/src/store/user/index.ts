import { defineStore } from 'pinia'
import { UserState } from './types'
import i18n from '../../lang'

export const useUserStore = defineStore('user', {
    state: (): UserState => ({
        user: undefined,
        token: undefined,
        lang: 'zh-CN',
        useHeader: true,
    }),
    actions: {
        setLang(lang: string) {
            this.lang = lang
            i18n.global.locale.value = lang.toLowerCase() as any
        },
    },
    persist: {
        paths: ['token', 'lang'],
        storage: localStorage
    },
})