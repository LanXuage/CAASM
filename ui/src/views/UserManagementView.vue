<script setup lang="ts">
import { h, reactive, ref } from 'vue'
import { ElButton, ElButtonGroup, ElCheckbox, ElMessage, ElMessageBox, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption } from 'element-plus'
import { Edit, Delete, CirclePlus } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import type { Column, CheckboxValueType } from 'element-plus'
import { APIUser } from '@/apis'
import type { IUser, IUserCreate, IUserUpdate } from '@/apis/user/types'
import XHeader from '@/components/XHeader.vue'

const { t } = useI18n()
const data = reactive<Array<IUser & { checked?: boolean }>>([])
const dialogVisible = ref(false)
const editMode = ref(false)
const editUserId = ref('')
const form = reactive<IUserCreate & { id?: string }>({
  username: '', password: '', realName: '', phone: '', email: '', userStatus: 1,
})
const statusDialogVisible = ref(false)
const statusUserId = ref('')
const statusForm = reactive({ userStatus: 1 })

const columns: Array<Column> = [
  { key: 'username', dataKey: 'username', title: t('username'), width: 120, sortable: true },
  { key: 'realName', dataKey: 'realName', title: t('realName'), width: 120, sortable: true },
  { key: 'phone', dataKey: 'phone', title: t('phone'), width: 130 },
  { key: 'email', dataKey: 'email', title: t('email'), width: 180 },
  { key: 'userStatus', dataKey: 'userStatus', title: t('userStatus'), width: 100,
    cellRenderer: ({ cellData }) => h('span', cellData === 1 ? t('active') : t('disabled')),
  },
  { key: 'operations', dataKey: 'id', title: t('operations'), width: 260, align: 'center',
    cellRenderer: ({ cellData, rowData }) => h(ElButtonGroup, () => [
      h(ElButton, { type: 'primary', icon: Edit, size: 'small', onClick: () => openEdit(rowData) }),
      h(ElButton, { size: 'small', onClick: () => openStatus(rowData) }, t('status')),
      h(ElButton, { type: 'danger', icon: Delete, size: 'small', onClick: () => delUser(cellData) }),
    ]),
  },
]

const refresh = () => {
  data.splice(0, data.length)
  APIUser.getUsers().then(res => data.push(...res)).catch(m => ElMessage.error(t(m)))
}

const openAdd = () => {
  editMode.value = false
  Object.assign(form, { username: '', password: '', realName: '', phone: '', email: '', userStatus: 1 })
  dialogVisible.value = true
}

const openEdit = (row: IUser) => {
  editMode.value = true
  editUserId.value = row.id
  Object.assign(form, { username: row.username, realName: row.realName, phone: row.phone, email: row.email, userStatus: row.userStatus })
  dialogVisible.value = true
}

const submitForm = () => {
  const apiCall = editMode.value
    ? APIUser.updateUser(editUserId.value, form as IUserUpdate)
    : APIUser.createUser(form as IUserCreate)
  apiCall.then(() => {
    ElMessage.success(t(editMode.value ? 'edit_success' : 'add_success'))
    dialogVisible.value = false
    refresh()
  }).catch(m => ElMessage.error(t(m)))
}

const delUser = (id: string) => {
  ElMessageBox.confirm(t('confirm_del')).then(() => {
    APIUser.deleteUser(id).then(() => { ElMessage.success(t('delete_success')); refresh() }).catch(m => ElMessage.error(t(m)))
  }).catch(() => {})
}

const openStatus = (row: IUser) => {
  statusUserId.value = row.id
  statusForm.userStatus = row.userStatus === 1 ? 2 : 1
  statusDialogVisible.value = true
}

const submitStatus = () => {
  APIUser.changeUserStatus(statusUserId.value, { userStatus: statusForm.userStatus }).then(() => {
    ElMessage.success(t('status_updated'))
    statusDialogVisible.value = false
    refresh()
  }).catch(m => ElMessage.error(t(m)))
}

refresh()
</script>

<template>
  <el-row><x-header title="user_management">
    <el-button type="primary" :icon="CirclePlus" @click="openAdd">{{ $t('add_user') }}</el-button>
  </x-header></el-row>
  <el-row style="flex:1">
    <el-auto-resizer>
      <template #default="{ height, width }">
        <el-table-v2 :columns="columns" :data="data" :width="width" :height="height" fixed />
      </template>
    </el-auto-resizer>
  </el-row>

  <!-- Add/Edit Dialog -->
  <el-dialog v-model="dialogVisible" :title="$t(editMode ? 'edit_user' : 'add_user')" draggable>
    <el-form :model="form" label-width="100px">
      <el-form-item :label="$t('username')"><el-input v-model="form.username" :disabled="editMode" /></el-form-item>
      <el-form-item v-if="!editMode" :label="$t('password')"><el-input v-model="form.password" type="password" /></el-form-item>
      <el-form-item :label="$t('realName')"><el-input v-model="form.realName" /></el-form-item>
      <el-form-item :label="$t('phone')"><el-input v-model="form.phone" /></el-form-item>
      <el-form-item :label="$t('email')"><el-input v-model="form.email" /></el-form-item>
      <el-form-item :label="$t('userStatus')">
        <el-select v-model="form.userStatus"><el-option :value="1" :label="$t('active')" /><el-option :value="2" :label="$t('disabled')" /></el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">{{ $t('cancel') }}</el-button>
      <el-button type="primary" @click="submitForm">{{ $t('confirm') }}</el-button>
    </template>
  </el-dialog>

  <!-- Status Dialog -->
  <el-dialog v-model="statusDialogVisible" :title="$t('change_status')" width="400px">
    <p>{{ $t('confirm_change_status') }}</p>
    <template #footer>
      <el-button @click="statusDialogVisible = false">{{ $t('cancel') }}</el-button>
      <el-button type="primary" @click="submitStatus">{{ $t('confirm') }}</el-button>
    </template>
  </el-dialog>
</template>