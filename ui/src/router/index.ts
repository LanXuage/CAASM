import { createRouter, createWebHashHistory } from 'vue-router'

import LayoutView from '../views/layout/index.vue'
import LoginSubView from '../views/subviews/login/index.vue'
import { useUserStore } from '../store/user'

const routes = [
    {
        path: '/',
        name: 'home',
        component: LayoutView,
        children: [
            {
                path: '/login',
                name: 'login',
                component: LoginSubView,
            },
        ]
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})


router.beforeEach((to, from) => {
    console.log(to, from)
    const userStore = useUserStore()
    if (to.path !== '/login' && userStore.token === undefined) {
        return '/login'
    } else if (to.path === '/login' && userStore.token !== undefined) {
        return '/'
    }
})

export default router