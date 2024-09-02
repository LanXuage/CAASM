<script setup lang="ts">
import { ref } from 'vue'
import { ElContainer, ElHeader, ElAside, ElMain } from 'element-plus'
import XMenu from '../../components/x-menu/index.vue'
import { useUserStore } from '../../store/user';

const userStore = useUserStore()

const useHeader = ref<boolean>(userStore.useHeader)
</script>

<template>
    <el-container class="x-layout-content">
        <el-header v-if="useHeader">
            <x-menu />
        </el-header>
        <el-aside v-else>
            <x-menu />
        </el-aside>
        <el-main>
            <router-view />
        </el-main>
    </el-container>
</template>