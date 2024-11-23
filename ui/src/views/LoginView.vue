<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ILoginParam } from '@/apis/user/types'
import { useI18n } from 'vue-i18n'
import { APIUser } from '@/apis'
import { cloneDeep, isNil } from 'lodash'
import CryptoJs from 'crypto-js'
import { useUserStore } from '@/stores/user'
import http from '@/utils/http'
import { APIURL } from '@/apis/common/types'
import { ElNofify } from '@/utils/el-notify'

const { t } = useI18n()
const userStore = useUserStore()


const loginFormRef = ref<FormInstance>()
const loginForm = reactive<ILoginParam>({
  username: '',
  password: '',
  captcha: '',
  s: Math.random().toString(21).slice(-10)
})
const captcha = ref<string>(http.getUri({ url: APIURL.captcha, params: { s: loginForm.s } }))


const rules = computed<FormRules<ILoginParam>>(() => ({
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


const refreshCaptcha = () => {
  loginForm.s = Math.random().toString(21).slice(-10)
  captcha.value = http.getUri({ url: APIURL.captcha, params: { s: loginForm.s } })
}

const submitForm = async (formEl: FormInstance | undefined) => {
  if (isNil(formEl)) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      console.log('submit!')
      const loginParam: ILoginParam = cloneDeep(loginForm)
      loginParam.password = CryptoJs.SHA256(`${loginForm.s}_${loginForm.captcha}_${loginForm.username}_${loginForm.password}`).toString()
      APIUser.login(loginParam).then(token => {
        ElNofify.success(t('login_success'))
        userStore.setToken(token)
      }).catch((msg: string) => {
        console.log(msg)
        loginForm.captcha = ''
        refreshCaptcha()
      })
    } else {
      console.log('error submit!', fields)
    }
  })
}

const resetForm = (formEl: FormInstance | undefined) => {
  if (isNil(formEl)) return
  formEl.resetFields()
}
</script>

<template>
  <el-form ref="loginFormRef" style="max-width: 400px; margin: 20px auto;" :model="loginForm" :rules="rules"
    label-width="80px" :hide-required-asterisk="true">
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
    <el-form-item style="margin-top: 25px;">
      <el-button type="primary" @click="submitForm(loginFormRef)">
        {{ $t('login') }}
      </el-button>
      <el-button @click="resetForm(loginFormRef)">{{ $t('reset') }}</el-button>
    </el-form-item>
  </el-form>
</template>
