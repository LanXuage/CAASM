<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>

<template>
  <el-config-provider :locale="userStore.locale">
    <el-container style="height: 100vh;">
      <el-header v-if="userStore.userState.useHeader">
        <x-menu />
      </el-header>
      <el-aside v-else>
        <x-menu />
      </el-aside>
      <el-main style="display: flex; flex-direction: column;">
        <router-view />
      </el-main>
    </el-container>
  </el-config-provider>
</template>
