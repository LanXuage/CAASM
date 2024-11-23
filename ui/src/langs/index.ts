import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN.json'
import en from './en.json'
import zhTW from './zh-TW.json'

const zh = {
  ...zhCN,
}

const tw = {
  ...zhTW,
}

const i18n = createI18n({
  locale: 'zh-cn',
  legacy: false,
  globalInjection: true,
  messages: {
    'zh-cn': zh,
    zh: zh,
    'zh-tw': tw,
    tw: tw,
    en: {
      ...en,
    },
  },
})

export default i18n
