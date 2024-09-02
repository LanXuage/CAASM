<script setup lang="ts">
import { useUserStore } from '../../store/user'

const userStore = useUserStore()

function selectLang(cmd: string) {
    console.log('cmd', cmd)
    userStore.setLang(cmd)
}

function selectTheme(cmd: string) {
    console.log('cmd', cmd)
}
</script>

<template>
    <el-row>
        <el-col :xs="24" :sm="24" :md="4" :lg="4" :xl="4">
            CAASM
        </el-col>
        <el-col :xs="24" :sm="24" :md="18" :lg="18" :xl="18">
            <el-row>
                <el-menu mode="horizontal" :ellipsis="false" :router="false">
                    <el-menu-item :disabled="false">
                        <template #title>菜单一</template>
                    </el-menu-item>
                    <el-sub-menu index="lang">
                        <template #title>菜单二</template>
                        <el-menu-item index="zh-CN">简体中文</el-menu-item>
                        <el-menu-item index="en">English</el-menu-item>
                        <el-menu-item index="zh-TW">繁體中文</el-menu-item>
                    </el-sub-menu>
                </el-menu>
            </el-row>
        </el-col>
        <el-col :xs="24" :sm="24" :md="2" :lg="2" :xl="2" style="display: flex;">
            <el-dropdown style="margin: auto;" @command="selectTheme">
                <div class="not-out-line">
                    <svg t="1725165637223" class="icon" viewBox="0 0 1024 1024" version="1.1"
                        xmlns="http://www.w3.org/2000/svg" p-id="11293" width="1.6em" height="1.6em">
                        <path
                            d="M96 512a416 416 0 1 1 832 0 416 416 0 0 1-832 0zM512 32a480 480 0 1 0 0 960 480 480 0 0 0 0-960zM512 832A320 320 0 1 0 512 192v640z"
                            fill="#606266" p-id="11294"></path>
                    </svg>
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="dark">{{ $t('dark_mode') }}</el-dropdown-item>
                        <el-dropdown-item command="light">{{ $t('light_mode') }}</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
            <el-dropdown style="margin: auto;" @command="selectLang">
                <div class="not-out-line">
                    <svg t="1725165765190" class="icon" viewBox="0 0 1107 1024" version="1.1"
                        xmlns="http://www.w3.org/2000/svg" p-id="15752" width="1.6em" height="1.6em">
                        <path
                            d="M36.74259 838.689548L0 742.839314l48.723869-18.371295a851.469579 851.469579 0 0 0 319.50078-213.666147A852.268331 852.268331 0 0 0 553.535101 199.687988l16.374415-49.522621 98.645866 32.74883-16.374415 49.123244a963.694228 963.694228 0 0 1-208.474259 351.450859 958.50234 958.50234 0 0 1-359.438377 239.625585z"
                            fill="#606266" p-id="15753"></path>
                        <path
                            d="M582.290172 791.163807l-43.931358-27.556943A998.439938 998.439938 0 0 1 319.50078 575.101404 990.053042 990.053042 0 0 1 174.926677 359.438378l-22.764431-45.928238 93.054603-45.528861 23.163806 46.327613a866.24649 866.24649 0 0 0 127.400936 192.49922 891.407176 891.407176 0 0 0 197.691108 168.936038l43.931357 27.556942z"
                            fill="#606266" p-id="15754"></path>
                        <path
                            d="M950.115445 878.627145h-182.514821l-39.937597 144.174727h-113.822153l180.118564-562.720749h132.592824l180.917317 562.720749h-117.815913z m-24.361935-87.463338l-16.773791-61.903277c-17.572543-58.308892-32.74883-123.0078-49.522621-183.712948h-2.795632c-14.776911 61.5039-31.151326 125.404056-47.925117 183.712948l-16.77379 61.903277z"
                            fill="#606266" p-id="15755"></path>
                        <path d="M7.188768 105.834633h824.312012v103.837754H7.188768z" fill="#606266" p-id="15756">
                        </path>
                        <path d="M339.469579 0h103.837753v191.700468H339.469579z" fill="#606266" p-id="15757"></path>
                    </svg>
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="zh">简体中文</el-dropdown-item>
                        <el-dropdown-item command="en">English</el-dropdown-item>
                        <el-dropdown-item command="zh-TW">繁體中文</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </el-col>
    </el-row>
</template>

<style>
.el-menu--horizontal>.el-menu-item:nth-child(1) {
    margin-right: auto;
}

.not-out-line:focus-visible {
    outline: unset;
}
</style>