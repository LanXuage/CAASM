<script setup lang="ts">
import { computed } from 'vue'
import { ElConfigProvider } from 'element-plus'
import { useUserStore } from './store/user'
import zhCN from 'element-plus/es/locale/lang/zh-cn'
import zhTW from 'element-plus/es/locale/lang/zh-tw'
import en from 'element-plus/es/locale/lang/en'

const userStore = useUserStore()

const langs = new Map([
  ['zh-cn', zhCN],
  ['zh-tw', zhTW],
  ['en', en],
  ['default', zhCN],
])

const lang = computed(() => langs.get(userStore.lang.toLocaleLowerCase()) || langs.get('default'))
</script>

<template>
  <el-config-provider :locale="lang">
    <router-view />
  </el-config-provider>
</template>