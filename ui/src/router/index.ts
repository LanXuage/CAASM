import { createRouter, createWebHashHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'
import { isNil } from 'lodash'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/50x',
      name: '50x',
      component: LoginView,
    },
    {
      path: '/404',
      name: '404',
      component: LoginView,
    },
  ],
})

router.beforeEach(async (to, from) => {
  console.log(to, from)
  const userStore = useUserStore()
  if (isNil(userStore.token) && to.path !== '/login') return '/login'
  if (!isNil(userStore.token) && to.path === '/login') return from
  if (isNil(to.name)) {
    if (await userStore.hasRoute(to.path)) return to
    if (to.path !== '/') return '/404'
  }
})

export default router
