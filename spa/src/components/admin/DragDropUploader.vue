<template>
  <div class="uploader-wrapper">
    <div 
      class="drop-zone" 
      :class="{ 'is-dragover': isDragover }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input 
        type="file" 
        ref="fileInput" 
        class="hidden-input" 
        @change="onFileChange" 
        :accept="accept"
      />
      <div v-if="!uploading && !uploadSuccess" class="drop-content">
        <i class="fas fa-cloud-upload-alt text-4xl mb-4 text-purple-400"></i>
        <p class="text-lg font-bold">Drag & Drop</p>
        <p class="text-sm text-purple-200/60 mt-2">or click to browse files</p>
      </div>

      <div v-if="uploading" class="upload-progress w-full px-8">
        <p class="mb-4 text-sm font-bold text-center">Uploading... {{ Math.round(progress) }}%</p>
        <div class="h-2 w-full bg-white/10 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300" 
            :style="{ width: progress + '%' }"
          ></div>
        </div>
      </div>

      <div v-if="uploadSuccess" class="upload-success text-green-400">
        <i class="fas fa-check-circle text-4xl mb-4"></i>
        <p class="font-bold">Upload Complete!</p>
        <button @click.stop="reset" class="mt-4 text-xs underline text-purple-300 hover:text-white">Upload Another</button>
      </div>
    </div>
    
    <div v-if="error" class="text-red-400 text-sm mt-2 text-center">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  accept: {
    type: String,
    default: '*/*'
  },
  endpoint: {
    type: String,
    default: '/api/admin/upload/signed-url'
  }
})

const emit = defineEmits(['upload-success', 'upload-error', 'upload-start'])

const isDragover = ref(false)
const fileInput = ref(null)
const uploading = ref(false)
const progress = ref(0)
const uploadSuccess = ref(false)
const error = ref('')

const triggerFileInput = () => {
  if (!uploading.value) {
    fileInput.value.click()
  }
}

const onDragOver = () => {
  if (!uploading.value) isDragover.value = true
}

const onDragLeave = () => {
  isDragover.value = false
}

const onDrop = (e) => {
  isDragover.value = false
  if (uploading.value) return
  
  const files = e.dataTransfer.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const onFileChange = (e) => {
  const files = e.target.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const reset = () => {
  uploading.value = false
  progress.value = 0
  uploadSuccess.value = false
  error.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleFile = async (file) => {
  error.value = ''
  uploading.value = true
  progress.value = 0
  emit('upload-start', file)

  try {
    // 1. Get signed URL from backend
    // Clean filename mapping spec characters
    const cleanFilename = file.name.replace(/[^a-zA-Z0-9.-]/g, '_')
    // Append timestamp to ensure uniqueness
    const filename = `${Date.now()}_${cleanFilename}`
    
    const signedUrlRes = await fetch(props.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` // if using JWT
      },
      body: JSON.stringify({
        filename: filename,
        content_type: file.type
      })
    })

    if (!signedUrlRes.ok) {
      throw new Error('Failed to get upload URL')
    }

    const { signed_url, public_url } = await signedUrlRes.json()

    // 2. Upload directly to GCS using XMLHttpRequest for progress
    await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('PUT', signed_url, true)
      xhr.setRequestHeader('Content-Type', file.type)

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          progress.value = (e.loaded / e.total) * 100
        }
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve()
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`))
        }
      }

      xhr.onerror = () => reject(new Error('Network error during upload'))
      xhr.send(file)
    })

    uploadSuccess.value = true
    emit('upload-success', { file, public_url, filename })

  } catch (err) {
    console.error('Upload Error:', err)
    error.value = err.message || 'An error occurred during upload'
    emit('upload-error', err)
  } finally {
    uploading.value = false
  }
}

defineExpose({
  handleFile,
  reset
})
</script>

<style scoped>
.uploader-wrapper {
  width: 100%;
}

.drop-zone {
  width: 100%;
  min-height: 200px;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.02);
  position: relative;
  overflow: hidden;
}

.drop-zone:hover, .drop-zone.is-dragover {
  border-color: rgba(168, 85, 247, 0.6);
  background: rgba(168, 85, 247, 0.05);
}

.hidden-input {
  display: none;
}

.drop-content {
  text-align: center;
  pointer-events: none;
}

.upload-progress, .upload-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 2rem;
}
</style>
