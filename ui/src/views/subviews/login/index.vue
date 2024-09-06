<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { ComponentSize, FormInstance, FormRules, ElMessage } from 'element-plus'
import { LoginParam } from '../../../api/user/types'
import { useI18n } from 'vue-i18n'
import { commonApi, UserApi } from '../../../api'
import { cloneDeep } from 'lodash'
import CryptoJs from 'crypto-js'
import { useUserStore } from '../../../store/user'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const userStore = useUserStore()
const router = useRouter()

const formSize = ref<ComponentSize>('default')
const loginFormRef = ref<FormInstance>()
const loginForm = reactive<LoginParam>({
    username: '',
    password: '',
    captcha: '',
    s: Math.random().toString(36).slice(-10)
})
const rules = computed<FormRules<LoginParam>>(() => ({
    username: [
        { required: true, message: t('uname_required_tip'), trigger: 'blur' },
        { min: 4, max: 12, message: t('len_tip'), trigger: 'blur' },
    ],
    password: [
        { required: true, message: t('passwd_required_tip'), trigger: 'blur' },
        { min: 4, max: 12, message: t('len_tip'), trigger: 'blur' },
    ],
    captcha: [
        { required: true, message: t('captcha_required_tip'), trigger: 'blur' },
    ],
}))

const captcha = ref<string>('')

const refreshCaptcha = () => {
    commonApi.getCaptcha(loginForm.s).then((res) => {
        captcha.value = `data:image/png;base64,${res}`
    })
}

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
        if (valid) {
            console.log('submit!')
            const loginParam = cloneDeep(loginForm)
            loginParam.password = CryptoJs.SHA256(`${loginForm.s}_${loginForm.captcha}_${loginForm.username}_${loginForm.password}`).toString()
            UserApi.login(loginParam).then((token) => {
                userStore.token = token
                console.log('router', router.currentRoute.value.redirectedFrom?.path)
                router.push('/')
            }).catch((msg) => {
                ElMessage.error(t(msg))
                loginForm.captcha = ''
                refreshCaptcha()
            })
        } else {
            console.log('error submit!', fields)
        }
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}

refreshCaptcha()

</script>

<template>
    <el-form ref="loginFormRef" style="max-width: 400px; margin: 20px auto;" :model="loginForm" :rules="rules"
        label-width="auto" :size="formSize" :hide-required-asterisk="true">
        <el-form-item :label="$t('uname')" prop="username">
            <el-input v-model="loginForm.username" />
        </el-form-item>
        <el-form-item :label="$t('passwd')" prop="password">
            <el-input v-model="loginForm.password" :show-password="true" />
        </el-form-item>
        <el-row>
            <el-col :span="14" style="margin: auto;">
                <el-form-item style="margin: auto;" :label="$t('captcha')" prop="captcha">
                    <el-input v-model="loginForm.captcha" />
                </el-form-item>
            </el-col>
            <el-col :span="10" style="padding: 5px;">
                <el-image style="border-radius: 5px;" @click="refreshCaptcha" :src="captcha" />
            </el-col>
        </el-row>
        <el-form-item>
            <el-button type="primary" @click="submitForm(loginFormRef)">
                {{ $t('login') }}
            </el-button>
            <el-button @click="resetForm(loginFormRef)">{{ $t('reset') }}</el-button>
        </el-form-item>
    </el-form>
</template>