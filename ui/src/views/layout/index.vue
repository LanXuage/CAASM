<script setup lang="ts">
import { ref } from 'vue'
import { ElContainer, ElHeader, ElAside, ElMain } from 'element-plus'
import XMenu from '../../components/x-menu/index.vue'
import { useUserStore } from '../../store/user';

const userStore = useUserStore()

const useHeader = ref<boolean>(userStore.useHeader)
</script>

<template>
    <el-container class="x-layout-content" style="height: 100vh;">
        <el-header style="background-color: #282828;" v-if="useHeader">
            <x-menu />
        </el-header>
        <el-aside v-else>
            <x-menu />
        </el-aside>
        <el-main style="display: flex; flex-direction: column;">
            <router-view />
        </el-main>
    </el-container>
</template>