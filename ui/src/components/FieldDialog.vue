<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { Refresh } from '@element-plus/icons-vue'
import type { IField } from '@/apis/field/types'
import type { FormInstance, FormRules } from 'element-plus'
import type { IFieldCollect } from '@/apis/field-collect/types'
import type { CheckboxValueType } from 'element-plus'
import { cloneDeep } from 'lodash'
import { APIFieldCollect } from '@/apis'

defineProps({
  title: {
    type: String
  },
})
const dialogVisible = defineModel<boolean>("dialogVisible", { required: true, default: false })
const field = defineModel<IField>("field", { default: { fieldName: '', fieldDesc: '', collects: [] } })
const emit = defineEmits<{ submit: [field: IField] }>()

const fieldCollects = reactive<Array<IFieldCollect>>([])
const fieldFormRef = ref<FormInstance>()
const checkAllFieldCollects = ref(false)
const addFieldIndeterminate = ref(false)
const refreshFieldCollectsLoading = ref(false)
const fieldForm = reactive<IField>(cloneDeep(field.value))
const fieldRules = reactive<FormRules<IField>>({
  fieldName: [
    { required: true, message: 'Please input Activity name', trigger: 'blur' },
    { min: 4, message: 'Length should be 3 to 5', trigger: 'blur' }
  ],
  fieldDesc: [
    { required: true, message: 'Please input Activity name', trigger: 'blur' },
    { min: 4, message: 'Length should be 3 to 5', trigger: 'blur' }
  ],
  collects: [{ type: 'array', required: true, message: 'Please input Activity name', trigger: 'blur' },],
})

const handleSelectFieldCollectsCheckAll = (val: CheckboxValueType) => {
  addFieldIndeterminate.value = false
  if (val) {
    fieldForm.collects = fieldCollects.map((e) => e.collectName)
  } else {
    fieldForm.collects = []
  }
}
const resetFieldForm = () => {
  Object.assign(fieldForm, field.value)
}
const refreshFieldCollects = () => {
  refreshFieldCollectsLoading.value = true
  APIFieldCollect.getFieldCollects().then((res) => {
    fieldCollects.splice(0, fieldCollects.length, ...res)
  }).finally(() => refreshFieldCollectsLoading.value = false)
}
const submitFieldForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      emit('submit', cloneDeep(fieldForm))
      resetFieldForm()
    } else {
      console.log('error submit!', fields)
    }
  })
}
watch(dialogVisible, (v) => {
  if (v) {
    Object.assign(fieldForm, field.value)
    refreshFieldCollects()
  }
})
watch(() => fieldForm.collects, (val) => {
  console.log('warch', val)
  if (val?.length === 0) {
    checkAllFieldCollects.value = false
    addFieldIndeterminate.value = false
  } else if (val?.length === fieldCollects.length) {
    checkAllFieldCollects.value = true
    addFieldIndeterminate.value = false
  } else {
    addFieldIndeterminate.value = true
  }
})
</script>
<template>
  <el-dialog v-model="dialogVisible" :title="title" draggable overflow align-center center>
    <el-form ref="fieldFormRef" :model="fieldForm" label-width="100px" :rules="fieldRules">
      <el-form-item :label="$t('fieldName')" prop="fieldName">
        <el-input v-model="fieldForm.fieldName" maxlength="127" show-word-limit />
      </el-form-item>
      <el-form-item :label="$t('fieldDesc')" prop="fieldDesc">
        <el-input v-model="fieldForm.fieldDesc" maxlength="511" show-word-limit type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }" />
      </el-form-item>
      <el-form-item :label="$t('collects')" prop="collects">
        <el-select v-model="fieldForm.collects" filterable multiple collapse-tags collapse-tags-tooltip
          :max-collapse-tags="3" placeholder="Select">
          <template #header>
            <el-row style="display: flex; flex-direction: row; justify-content: space-between;">
              <el-checkbox v-model="checkAllFieldCollects" :indeterminate="addFieldIndeterminate"
                @change="handleSelectFieldCollectsCheckAll">
                All
              </el-checkbox>
              <el-button type="primary" :loading="refreshFieldCollectsLoading" :loading-icon="Refresh" :icon="Refresh"
                link @click="refreshFieldCollects" />
            </el-row>
          </template>
          <el-option v-for="item, i in fieldCollects" :key="i" :label="item.collectName" :value="item.collectName" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">{{ $t('cancel') }}</el-button>
      <el-button @click="resetFieldForm">{{ $t('reset') }}</el-button>
      <el-button type="primary" @click="submitFieldForm(fieldFormRef)">{{ $t('confirm') }}</el-button>
    </template>
  </el-dialog>
</template>
