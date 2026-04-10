<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center"
       style="background: linear-gradient(135deg, #0d6efd 0%, #0056b3 100%)">
    <div class="card shadow-lg" style="width:420px; max-width:95vw">
      <div class="card-body p-4">
        <!-- Logo / Header -->
        <div class="text-center mb-4">
          <div class="d-inline-flex align-items-center justify-content-center rounded-circle bg-primary bg-opacity-10 mb-3"
               style="width:64px;height:64px">
            <i class="bi bi-hospital fs-2 text-primary"></i>
          </div>
          <h3 class="fw-bold mb-0">HMS Portal</h3>
          <p class="text-muted small">Hospital Management System</p>
        </div>

        <div v-if="error" class="alert alert-danger py-2 small" data-testid="login-error">{{ error }}</div>

        <form @submit.prevent="handleLogin" data-testid="login-form">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-person"></i></span>
              <input v-model="form.username" type="text" class="form-control"
                     placeholder="Enter username" required
                     data-testid="login-username" autocomplete="username" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-lock"></i></span>
              <input v-model="form.password" :type="showPw ? 'text' : 'password'"
                     class="form-control" placeholder="Enter password" required
                     data-testid="login-password" autocomplete="current-password" />
              <button type="button" class="btn btn-outline-secondary"
                      @click="showPw = !showPw">
                <i :class="showPw ? 'bi-eye-slash' : 'bi-eye'" class="bi"></i>
              </button>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100 py-2 mt-2" :disabled="loading"
                  data-testid="login-submit-btn">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <hr class="my-3" />

        <!-- Demo credentials -->
        <div class="mb-3">
          <p class="text-muted small text-center mb-2">Quick Login (Demo)</p>
          <div class="d-flex gap-2 flex-wrap justify-content-center">
            <button class="btn btn-sm btn-outline-primary" @click="quickLogin('admin','Admin@123')" data-testid="demo-admin-btn">
              <i class="bi bi-shield-check me-1"></i>Admin
            </button>
            <button class="btn btn-sm btn-outline-success" @click="quickLogin('dr.sharma','Doctor@123')" data-testid="demo-doctor-btn">
              <i class="bi bi-person-badge me-1"></i>Doctor
            </button>
            <button class="btn btn-sm btn-outline-info" @click="quickLogin('patient1','Patient@123')" data-testid="demo-patient-btn">
              <i class="bi bi-person me-1"></i>Patient
            </button>
          </div>
        </div>

        <p class="text-center text-muted small mb-0">
          New patient?
          <router-link to="/register" class="text-primary fw-semibold" data-testid="register-link">Register here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import api from '@/utils/api.js'

const router = useRouter()
const authStore = useAuthStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPw = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/api/auth/login', form)
    authStore.login(res.data)
    router.push(`/${res.data.role}`)
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}

function quickLogin(u, p) {
  form.username = u
  form.password = p
  handleLogin()
}
</script>
