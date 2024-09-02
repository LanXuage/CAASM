import { createApp } from 'vue'
import './style.css'
import pinia from './store'
import router from './router'
import i18n from './lang'
import App from './App.vue'

import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(pinia)
app.use(i18n)
app.use(router)
app.mount('#app')