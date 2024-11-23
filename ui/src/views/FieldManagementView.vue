<script setup lang="ts">
import type { CheckboxValueType, Column, FormRules, Action } from 'element-plus'
import { ElButton, ElButtonGroup, ElCheckbox, ElMessage, ElMessageBox } from 'element-plus'
import { h, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SortBy, SortState } from 'element-plus'
import { Edit, Delete, CirclePlus, Download, Upload, UploadFilled, Loading } from '@element-plus/icons-vue'
import { APIURL, type IBulkForm } from '@/apis/common/types'
import { APIField } from '@/apis'
import { useResizeObserver } from '@vueuse/core'
import HTTP from '@/utils/http'
import { useUserStore } from '@/stores/user'
import { type INotify, NotifyType } from '@/utils/notify/types'
import FieldDialog from '@/components/FieldDialog.vue'
import type { IField } from '@/apis/field/types'

const { t } = useI18n()

const userStore = useUserStore()

const data = reactive<Array<IField>>([])
const addFieldDialogVisible = ref(false)
const editFieldDialogVisible = ref(false)
const importBulkFieldsDialogVisible = ref(false)
const isIndeterminate = ref(false)
const allSelected = ref<CheckboxValueType>(false)
const editFieldForm = reactive<IField>({ fieldName: '', fieldDesc: '', collects: [] });


const editField = (rowData: IField) => {
  console.log('editField', rowData)
  Object.assign(editFieldForm, rowData)
  editFieldDialogVisible.value = true
}
const deleteField = (vid: string) => {
  console.log('deleteField', vid)
  ElMessageBox.confirm(t('confirm_del_field'))
    .then(() => {
      APIField.delField(vid).then((res) => {
        console.log('delete success', res)
        ElMessage.success(t('delete_success'))
        for (const i in data) {
          if (data[i].id === vid) {
            data.splice(Number(i), 1)
          }
        }
      }).catch((msg) => {
        ElMessage.error(t(msg))
      })
    })
    .catch((msg) => {
      ElMessage.warning(t(msg))
    })
}
const columns = reactive<Array<Column>>([
  {
    key: 'selection',
    cellRenderer: ({ rowData }) => h(ElCheckbox, {
      modelValue: rowData.checked, onChange: (value: CheckboxValueType) => {
        rowData.checked = value
        allSelected.value = data.every((v) => v.checked)
        isIndeterminate.value = !allSelected.value && data.some((v) => v.checked)
      }
    }),
    headerCellRenderer: () => h(ElCheckbox, {
      modelValue: allSelected.value, indeterminate: isIndeterminate.value,
      onChange: (value: CheckboxValueType) => {
        if (isIndeterminate.value) {
          isIndeterminate.value = false
        }
        allSelected.value = value
        data.forEach((v) => v.checked = value)
      }
    }),
    width: 50,
  },
  {
    key: 'fieldName',
    dataKey: 'fieldName',
    title: t('fieldName'),
    width: 150,
    sortable: true
  },
  {
    key: 'fieldDesc',
    dataKey: 'fieldDesc',
    title: t('fieldDesc'),
    width: 150,
    sortable: true
  },
  {
    key: 'collects',
    dataKey: 'collects',
    title: t('collects'),
    width: 150,
    sortable: true
  },
  {
    key: 'updatedAt',
    dataKey: 'updatedAt',
    title: t('updatedAt'),
    width: 150,
    sortable: true
  },
  {
    key: 'createdAt',
    dataKey: 'createdAt',
    title: t('createdAt'),
    width: 150,
    sortable: true
  },
  {
    key: 'operations',
    dataKey: 'id',
    title: t('operations'),
    cellRenderer: ({ cellData, rowData }) => h(ElButtonGroup, () => [
      h(ElButton, { type: 'primary', icon: Edit, onClick: () => editField(rowData) }),
      h(ElButton, { type: 'danger', icon: Delete, onClick: () => deleteField(cellData) }),
    ]),
    width: 200,
    align: 'center',
  },
])
const sortState = reactive<SortState>({
  // 'fieldName': TableV2SortOrder.DESC,
  // 'fieldDesc': TableV2SortOrder.ASC,
  // 'updatedAt': TableV2SortOrder.ASC,
  // 'createdAt': TableV2SortOrder.ASC,
})
const xTableContainer = ref()
const bulkFields = reactive<IBulkForm>({ fileLists: [] })
const buikFieldsRules = reactive<FormRules<IBulkForm>>({
  fileLists: [
    { required: true, message: 'Please input Activity name', trigger: 'blur' },
    { min: 1, message: 'Length should be 1 more', trigger: 'blur' }
  ],
})

const onSort = ({ key, order }: SortBy) => {
  sortState[key] = order
  console.log('sortState', sortState)
  data.splice(0, data.length, ...data.reverse())
}

const showAddFieldDialog = () => {
  addFieldDialogVisible.value = true
}

const refreshFields = () => {
  APIField.getFields().then((res) => {
    data.push(...res)
  }).catch((msg) => {
    ElMessage.error(t(msg))
  })
}

const submitAddField = (field: IField) => {
  APIField.addField(field).then((res) => {
    console.log('res', res)
    ElMessage.success(t('add_field_success'))
    data.push(res)
    addFieldDialogVisible.value = false
  }).catch((msg) => {
    ElMessage.error(t(msg))
  })
}

const submitEditField = (field: IField) => {
  APIField.modifyField(field).then((res) => {
    console.log('res', res)
    ElMessage.success(t('edit_field_success'))
    for (const i in data) {
      if (data[i].id === res.id) {
        data.splice(Number(i), 1, res)
      }
    }
    editFieldDialogVisible.value = false
  }).catch((msg) => {
    ElMessage.error(t(msg))
  })
}
const deleteBulkFields = () => {
  const ids = data.filter((v) => v.checked).map((v) => v.id)
  if (ids.length < 1) {
    ElMessage.warning(t('nothing_selected'))
    return
  }
  ElMessageBox.confirm(t('confirm_del_fields'))
    .then(() => {
      ElMessageBox.alert('', 'message...', {
        center: true,
        icon: Loading,
        confirmButtonText: t('background'),
        callback: (action: Action) => {
          console.log('action', action)
          ElMessage.success(t('add_background_success'))
        },
      })
      APIField.delBulkFields(ids).then((taskId) => {
        console.log('taskId', taskId)
        if (userStore.userState.notifyQueue !== undefined) {
          userStore.userState.notifyQueue.register(NotifyType.notify, async (notify: INotify) => {
            console.log('notify', notify)
            ElMessageBox.close()
            ElMessage.success(t('delete_fields_success'))
            isIndeterminate.value = false
            allSelected.value = false
            let i = 0
            while (i < data.length) {
              if (data[i].checked) {
                data.splice(Number(i), 1)
              } else {
                i += 1
              }
            }
          }, taskId)
        }

      }).catch((msg) => {
        ElMessage.error(t(msg))
        ElMessageBox.close()
      })
    })
    .catch((msg) => {
      ElMessage.warning(t(msg))
    })

}

const submitBulkFields = () => {
  console.log('bulkFiles', bulkFields.fileLists)
  const hasUploading = bulkFields.fileLists.some((v) => v.status != 'success')
  if (hasUploading) {
    ElMessage.warning(t('file_uploading'))
    return
  }
  // const hasUploadFailed = bulkFields.fileLists.some((v) => v.response.code != 200)
  // if (hasUploadFailed) {
  //   ElMessage.error(t('upload_failed'))
  //   return
  // }
  APIField.addBulkFields(bulkFields.fileLists.map((v) => v.name)).then((res) => {
    console.log('taskId', res)
  }).catch((msg) => {
    ElMessage.error(t(msg))
  })
}

refreshFields()
useResizeObserver(xTableContainer, (entries) => {
  const columnLength = entries[0].contentRect.width / (columns.length - 1) - 10
  columns.forEach((e) => {
    if (e.key !== 'selection') {
      e.width = columnLength
    }
  })
})
</script>

<template>
  <el-row>
    <x-header title="field_management">
      <div class="flex items-center">
        <el-button-group>
          <el-button type="primary" :icon="CirclePlus" @click="showAddFieldDialog">{{ $t('add_field')
            }}</el-button>
          <el-button type="primary" @click="importBulkFieldsDialogVisible = true" :icon="Download">{{
            $t('bulk_import')
            }}</el-button>
          <el-button type="primary" :icon="Upload">{{ $t('bulk_export') }}</el-button>
          <el-button type="danger" @click="deleteBulkFields" :icon="Delete">{{ $t('bulk_delete')
            }}</el-button>
        </el-button-group>
      </div>
    </x-header>
  </el-row>
  <el-row style="flex: 1;" ref="xTableContainer">
    <el-auto-resizer>
      <template #default="{ height, width }">
        <el-table-v2 @column-sort="onSort" v-model:sort-state="sortState" :columns="columns" :data="data" :width="width"
          :height="height" fixed />
      </template>
    </el-auto-resizer>
  </el-row>
  <field-dialog :title="$t('add_field')" v-model:dialog-visible="addFieldDialogVisible" @submit="submitAddField" />
  <field-dialog :title="$t('edit_field')" v-model:dialog-visible="editFieldDialogVisible" v-model:field="editFieldForm"
    @submit="submitEditField" />
  <el-dialog v-model="importBulkFieldsDialogVisible" :title="$t('bulk_import')" draggable overflow align-center center>
    <el-form ref="bulkFieldsFormRef" :model="bulkFields" label-width="100px" :rules="buikFieldsRules">
      <el-form-item :label="$t('file_lists')" prop="fileLists">
        <el-upload drag v-model:file-list="bulkFields.fileLists" :action="HTTP.getUri({ url: APIURL.upload })"
          :headers="HTTP.getHeaders()" multiple>
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            Drop file here or <em>click to upload</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              compressed/excel/csv files with a size less than 500mb
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="importBulkFieldsDialogVisible = false">{{ $t('cancel') }}</el-button>
      <el-button type="primary" @click="submitBulkFields">{{ $t('confirm') }}</el-button>
    </template>
  </el-dialog>
</template>
