<script lang="ts" setup>
import { Menu } from '../../api/user/types'
import { ROUTES_MAP } from '../../router/constant'
import { ArrowLeft } from '@element-plus/icons-vue'

defineProps({
  menus: {
    type: Array<Menu>,
    default: [],
  },
  backRoute: {
    type: Object,
    default: {}
  },
  title: {
    type: String,
    default: ''
  }
})

function onBack(e: any) {
  console.log('onBack', e)
}
</script>

<template>
  <el-page-header style="width: 100%;" @back="onBack" :icon="ArrowLeft">
    <template #breadcrumb>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="menu, i in menus" :key="i" :to="ROUTES_MAP.get(menu.permName)">{{ $t(menu.permName)
          }}</el-breadcrumb-item>
      </el-breadcrumb>
    </template>
    <template #content>
      <div class="flex items-center">
        <span class="text-large font-600 mr-3"> {{ $t(title) }} </span>
      </div>
    </template>
    <template #extra>
      <slot></slot>
    </template>
  </el-page-header>
</template>