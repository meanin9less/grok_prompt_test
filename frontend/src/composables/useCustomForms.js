import { ref } from 'vue'

const STORAGE_KEY = 'custom_forms'

export function useCustomForms() {
  const forms = ref([])
  const currentFormId = ref(null)

  // localStorage에서 폼 로드
  const loadForms = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      forms.value = stored ? JSON.parse(stored) : []
    } catch (error) {
      console.error('Error loading forms:', error)
      forms.value = []
    }
  }

  // localStorage에 폼 저장
  const saveForms = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(forms.value))
    } catch (error) {
      console.error('Error saving forms:', error)
    }
  }

  // 새 폼 생성
  const createForm = (name) => {
    const formId = `form-${Date.now()}`
    const newForm = {
      id: formId,
      name,
      fields: [],
      createdAt: new Date().toISOString()
    }
    forms.value.push(newForm)
    saveForms()
    return formId
  }

  // 폼에 필드 추가
  const addFieldToForm = (formId, fieldName) => {
    const form = forms.value.find(f => f.id === formId)
    if (!form) return false

    const fieldId = `field-${Date.now()}`
    form.fields.push({
      id: fieldId,
      name: fieldName,
      type: 'text',
      value: ''
    })
    saveForms()
    return true
  }

  // 폼에서 필드 삭제
  const removeFieldFromForm = (formId, fieldId) => {
    const form = forms.value.find(f => f.id === formId)
    if (!form) return false

    form.fields = form.fields.filter(f => f.id !== fieldId)
    saveForms()
    return true
  }

  // 폼의 필드 값 업데이트
  const updateFieldValue = (formId, fieldId, value) => {
    const form = forms.value.find(f => f.id === formId)
    if (!form) return false

    const field = form.fields.find(f => f.id === fieldId)
    if (!field) return false

    field.value = value
    saveForms()
    return true
  }

  // 폼 삭제
  const deleteForm = (formId) => {
    forms.value = forms.value.filter(f => f.id !== formId)
    if (currentFormId.value === formId) {
      currentFormId.value = null
    }
    saveForms()
    return true
  }

  // 폼 이름 수정
  const updateFormName = (formId, newName) => {
    const form = forms.value.find(f => f.id === formId)
    if (!form) return false

    form.name = newName
    saveForms()
    return true
  }

  // 폼 조회
  const getForm = (formId) => {
    return forms.value.find(f => f.id === formId)
  }

  // 초기화
  loadForms()

  return {
    // 폼 관리
    forms,
    currentFormId,
    loadForms,
    createForm,
    deleteForm,
    updateFormName,
    getForm,
    addFieldToForm,
    removeFieldFromForm,
    updateFieldValue
  }
}
