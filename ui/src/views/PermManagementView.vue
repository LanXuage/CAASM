<script setup lang="ts">
import { h, reactive, ref } from 'vue'
import { ElButton, ElButtonGroup, ElMessage, ElMessageBox, ElDialog, ElForm, ElFormItem, ElInput } from 'element-plus'
import { Edit, Delete, CirclePlus } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import type { Column } from 'element-plus'
import { APIPerm } from '@/apis'
import type { IPerm, IPermCreate } from '@/apis/perm/types'
import XHeader from '@/components/XHeader.vue'

const { t } = useI18n()
const data = reactive<Array<IPerm>>([])
const dialogVisible = ref(false)
const editMode = ref(false)
const editPermId = ref('')
const form = reactive<IPermCreate>({ permName: '', permDesc: '' })

const columns: Array<Column> = [
  { key: 'permName', dataKey: 'permName', title: t('permName'), width: 200, sortable: true },
  { key: 'permDesc', dataKey: 'permDesc', title: t('permDesc'), width: 300, sortable: true },
  { key: 'updatedAt', dataKey: 'updatedAt', title: t('updatedAt'), width: 180 },
  { key: 'operations', dataKey: 'id', title: t('operations'), width: 200, align: 'center',
    cellRenderer: ({ cellData, rowData }) => h(ElButtonGroup, () => [
      h(ElButton, { type: 'primary', icon: Edit, size: 'small', onClick: () => openEdit(rowData) }),
      h(ElButton, { type: 'danger', icon: Delete, size: 'small', onClick: () => delPerm(cellData) }),
    ]),
  },
]

const refresh = () => {
  data.splice(0, data.length)
  APIPerm.getPerms().then(res => data.push(...res)).catch(m => ElMessage.error(t(m)))
}

const openAdd = () => {
  editMode.value = false
  form.permName = ''; form.permDesc = ''
  dialogVisible.value = true
}

const openEdit = (row: IPerm) => {
  editMode.value = true; editPermId.value = row.id
  form.permName = row.permName; form.permDesc = row.permDesc
  dialogVisible.value = true
}

const submitForm = () => {
  const call = editMode.value
    ? APIPerm.updatePerm(editPermId.value, form)
    : APIPerm.createPerm(form)
  call.then(() => {
    ElMessage.success(t(editMode.value ? 'edit_success' : 'add_success'))
    dialogVisible.value = false; refresh()
  }).catch(m => ElMessage.error(t(m)))
}

const delPerm = (id: string) => {
  ElMessageBox.confirm(t('confirm_del')).then(() => {
    APIPerm.deletePerm(id).then(() => { ElMessage.success(t('delete_success')); refresh() }).catch(m => ElMessage.error(t(m)))
  }).catch(() => {})
}

refresh()
</script>

<template>
  <el-row><x-header title="perm_management">
    <el-button type="primary" :icon="CirclePlus" @click="openAdd">{{ $t('add_perm') }}</el-button>
  </x-header></el-row>
  <el-row style="flex:1">
    <el-auto-resizer>
      <template #default="{ height, width }">
        <el-table-v2 :columns="columns" :data="data" :width="width" :height="height" fixed />
      </template>
    </el-auto-resizer>
  </el-row>

  <el-dialog v-model="dialogVisible" :title="$t(editMode ? 'edit_perm' : 'add_perm')" draggable>
    <el-form :model="form" label-width="100px">
      <el-form-item :label="$t('permName')"><el-input v-model="form.permName" /></el-form-item>
      <el-form-item :label="$t('permDesc')"><el-input v-model="form.permDesc" type="textarea" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">{{ $t('cancel') }}</el-button>
      <el-button type="primary" @click="submitForm">{{ $t('confirm') }}</el-button>
    </template>
  </el-dialog>
</template>