import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import { createApp } from 'vue'

import App from './App.vue'
import pinia from './stores'
import i18n from './langs'
import router from './router'

const app = createApp(App)

app.use(pinia)
app.use(i18n)
app.use(router)

app.mount('#app')
