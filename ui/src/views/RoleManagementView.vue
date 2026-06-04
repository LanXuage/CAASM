<script setup lang="ts">
import { h, reactive, ref } from 'vue'
import { ElButton, ElButtonGroup, ElMessage, ElMessageBox, ElDialog, ElForm, ElFormItem, ElInput } from 'element-plus'
import { Edit, Delete, CirclePlus, Link, Connection } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import type { Column } from 'element-plus'
import { APIRole } from '@/apis'
import type { IRole, IRoleCreate } from '@/apis/role/types'
import XHeader from '@/components/XHeader.vue'

const { t } = useI18n()
const data = reactive<Array<IRole>>([])
const dialogVisible = ref(false)
const editMode = ref(false)
const editRoleId = ref('')
const form = reactive<IRoleCreate>({ roleName: '', roleDesc: '' })

const columns: Array<Column> = [
  { key: 'roleName', dataKey: 'roleName', title: t('roleName'), width: 150, sortable: true },
  { key: 'roleDesc', dataKey: 'roleDesc', title: t('roleDesc'), width: 250, sortable: true },
  { key: 'updatedAt', dataKey: 'updatedAt', title: t('updatedAt'), width: 180 },
  { key: 'operations', dataKey: 'id', title: t('operations'), width: 200, align: 'center',
    cellRenderer: ({ cellData, rowData }) => h(ElButtonGroup, () => [
      h(ElButton, { type: 'primary', icon: Edit, size: 'small', onClick: () => openEdit(rowData) }),
      h(ElButton, { type: 'danger', icon: Delete, size: 'small', onClick: () => delRole(cellData) }),
    ]),
  },
]

const refresh = () => {
  data.splice(0, data.length)
  APIRole.getRoles().then(res => data.push(...res)).catch(m => ElMessage.error(t(m)))
}

const openAdd = () => {
  editMode.value = false
  form.roleName = ''; form.roleDesc = ''
  dialogVisible.value = true
}

const openEdit = (row: IRole) => {
  editMode.value = true; editRoleId.value = row.id
  form.roleName = row.roleName; form.roleDesc = row.roleDesc
  dialogVisible.value = true
}

const submitForm = () => {
  const call = editMode.value
    ? APIRole.updateRole(editRoleId.value, form)
    : APIRole.createRole(form)
  call.then(() => {
    ElMessage.success(t(editMode.value ? 'edit_success' : 'add_success'))
    dialogVisible.value = false; refresh()
  }).catch(m => ElMessage.error(t(m)))
}

const delRole = (id: string) => {
  ElMessageBox.confirm(t('confirm_del')).then(() => {
    APIRole.deleteRole(id).then(() => { ElMessage.success(t('delete_success')); refresh() }).catch(m => ElMessage.error(t(m)))
  }).catch(() => {})
}

refresh()
</script>

<template>
  <el-row><x-header title="role_management">
    <el-button type="primary" :icon="CirclePlus" @click="openAdd">{{ $t('add_role') }}</el-button>
  </x-header></el-row>
  <el-row style="flex:1">
    <el-auto-resizer>
      <template #default="{ height, width }">
        <el-table-v2 :columns="columns" :data="data" :width="width" :height="height" fixed />
      </template>
    </el-auto-resizer>
  </el-row>

  <el-dialog v-model="dialogVisible" :title="$t(editMode ? 'edit_role' : 'add_role')" draggable>
    <el-form :model="form" label-width="100px">
      <el-form-item :label="$t('roleName')"><el-input v-model="form.roleName" /></el-form-item>
      <el-form-item :label="$t('roleDesc')"><el-input v-model="form.roleDesc" type="textarea" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">{{ $t('cancel') }}</el-button>
      <el-button type="primary" @click="submitForm">{{ $t('confirm') }}</el-button>
    </template>
  </el-dialog>
</template>