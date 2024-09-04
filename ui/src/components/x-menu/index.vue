<script setup lang="ts">
import { useUserStore } from '../../store/user'
import { computed } from 'vue';
import { User } from '../../api/user/types';
import { UserApi } from '../../api';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const userStore = useUserStore()
const router = useRouter()

const token = computed<string | undefined>(() => userStore.token)
const user = computed<User | undefined>(() => userStore.user)

function selectLang(lang: string) {
    console.log('lang', lang)
    userStore.setLang(lang)
}

function selectTheme(theme: string) {
    console.log('theme', theme)
}

const userOpts = new Map([['logout', () => UserApi.logout().then((res) => {
    console.log('logout', res)
    userStore.user = undefined
    userStore.token = undefined
    router.push('/login')
}).catch((msg) => ElMessage.error(msg))]])

function selectUserOpt(opt: string) {
    const func = userOpts.get(opt)
    if (func) func()
}

</script>

<template>
    <el-row>
        <el-col :xs="24" :sm="24" :md="4" :lg="4" :xl="4">
            CAASM
        </el-col>
        <el-col :xs="24" :sm="24" :md="token ? 16 : 18" :lg="token ? 16 : 18" :xl="token ? 16 : 18">
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
        <el-col :xs="24" :sm="24" :md="token ? 4 : 2" :lg="token ? 4 : 2" :xl="token ? 4 : 2" style="display: flex;">
            <el-dropdown v-if="token" style="margin: auto;" @command="selectUserOpt">
                <div class="not-out-line">
                    <svg t="1725273259614" class="icon" viewBox="0 0 1024 1024" version="1.1"
                        xmlns="http://www.w3.org/2000/svg" p-id="10938" width="1.6em" height="1.6em">
                        <path
                            d="M512.010745 1022.082324c-282.335297 0-511.220241-228.798986-511.220241-511.036046C0.790504 228.798986 229.675448 0 512.010745 0c282.312784 0 511.198751 228.798986 511.198751 511.046279C1023.208473 793.285385 794.322505 1022.082324 512.010745 1022.082324zM512.010745 95.826486c-229.385341 0-415.371242 185.884594-415.371242 415.220816 0 107.22714 41.021276 204.6551 107.802238 278.339286 60.140729-29.092595 38.062897-4.88424 116.77254-37.274952 80.539314-33.089629 99.610672-44.639686 99.610672-44.639686l0.776689-76.29464c0 0-30.169113-22.890336-39.543621-94.683453-18.895349 5.426593-25.108864-21.988804-26.237571-39.429011-1.001817-16.863063-10.926864-69.487607 12.105712-64.739467-4.714372-35.144428-8.094352-66.844407-6.417153-83.633792 5.763261-58.938344 62.97324-120.518864 151.105486-125.017318 103.665011 4.486174 144.737452 66.028832 150.500713 124.9682 1.680269 16.800641-2.028193 48.511877-6.739495 83.594907 23.025413-4.686742 13.028735 47.861054 11.901051 64.726164-1.028423 17.440208-7.394411 44.756343-26.208918 39.34203-9.42158 71.79107-39.593763 94.498234-39.593763 94.498234l0.725524 75.924203c0 0 19.070334 10.788717 99.609649 43.892673 78.70862 32.387641 56.605206 9.609869 116.77561 38.765909 66.75231-73.686233 107.772562-171.101913 107.772562-278.339286C927.356404 281.712103 741.398132 95.826486 512.010745 95.826486z"
                            p-id="10939" fill="#606266"></path>
                    </svg>
                    <br />
                    {{ user?.username }}
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="profile">{{ $t('profile') }}</el-dropdown-item>
                        <el-dropdown-item command="settings">{{ $t('settings') }}</el-dropdown-item>
                        <el-dropdown-item command="logout">{{ $t('logout') }}</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
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