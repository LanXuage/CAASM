import { createRouter, createWebHashHistory } from 'vue-router'

import LayoutView from '../views/layout/index.vue'
import LoginSubView from '../views/subviews/login/index.vue'
import { useUserStore } from '../store/user'
import { ROUTES_MAP } from './constant'

const layoutChildren = [
    {
        path: '/login',
        name: 'login',
        component: LoginSubView,
    }
]

for (const [_, value] of ROUTES_MAP) {
    layoutChildren.push(value)
}

const routes = [
    {
        path: '/',
        name: 'layout',
        component: LayoutView,
        redirect: '/overview',
        children: layoutChildren
    },
]



const router = createRouter({
    history: createWebHashHistory(),
    routes,
})


router.beforeEach((to, from) => {
    console.log(to, from)
    const userStore = useUserStore()
    console.log('user', userStore.user)
    if (to.path !== '/login' && userStore.token === '') {
        return '/login'
    } else if (to.path === '/login' && userStore.token !== '') {
        return from
    }
})

export default router