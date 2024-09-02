import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN.json'
import en from './en.json'
import zhTW from './zh-TW.json'

const i18n = createI18n({
    locale: 'zh-cn',
    legacy: false,
    globalInjection: true,
    messages: {
        'zh-cn': {
            ...zhCN
        },
        'en': {
            ...en
        },
        'zh-tw': {
            ...zhTW
        },
        'yue': {

        }
    }
})

export default i18n