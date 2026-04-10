<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center"
       style="background: linear-gradient(135deg, #0d6efd 0%, #0056b3 100%)">
    <div class="card shadow-lg" style="width:480px; max-width:95vw">
      <div class="card-body p-4">
        <div class="text-center mb-3">
          <i class="bi bi-person-plus fs-1 text-primary"></i>
          <h4 class="fw-bold mt-2">Patient Registration</h4>
          <p class="text-muted small">Create your HMS patient account</p>
        </div>

        <div v-if="error" class="alert alert-danger py-2 small" data-testid="register-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2 small" data-testid="register-success">
          {{ success }} <router-link to="/login">Login here</router-link>
        </div>

        <form @submit.prevent="handleRegister" data-testid="register-form" novalidate>
          <div class="row g-2">
            <div class="col-6">
              <label class="form-label">Full Name *</label>
              <input v-model="form.name" type="text" :class="['form-control', errors.name ? 'is-invalid' : '']"
                     placeholder="Rahul Kumar" data-testid="reg-name" @input="clearError('name')" />
              <div class="invalid-feedback">{{ errors.name }}</div>
            </div>
            <div class="col-6">
              <label class="form-label">Username *</label>
              <input v-model="form.username" type="text" :class="['form-control', errors.username ? 'is-invalid' : '']"
                     placeholder="rahul123" data-testid="reg-username" @input="clearError('username')" />
              <div class="invalid-feedback">{{ errors.username }}</div>
            </div>
            <div class="col-12">
              <label class="form-label">Email *</label>
              <input v-model="form.email" type="email" :class="['form-control', errors.email ? 'is-invalid' : '']"
                     placeholder="rahul@email.com" data-testid="reg-email" @input="clearError('email')" />
              <div class="invalid-feedback">{{ errors.email }}</div>
            </div>
            <div class="col-6">
              <label class="form-label">Password *</label>
              <input v-model="form.password" type="password" :class="['form-control', errors.password ? 'is-invalid' : '']"
                     placeholder="Min 6 characters" data-testid="reg-password" @input="clearError('password')" />
              <div class="invalid-feedback">{{ errors.password }}</div>
            </div>
            <div class="col-6">
              <label class="form-label">Confirm Password *</label>
              <input v-model="form.confirmPassword" type="password"
                     :class="['form-control', errors.confirmPassword ? 'is-invalid' : '']"
                     placeholder="Repeat password" data-testid="reg-confirm-password"
                     @input="clearError('confirmPassword')" />
              <div class="invalid-feedback">{{ errors.confirmPassword }}</div>
            </div>
            <div class="col-6">
              <label class="form-label">Phone</label>
              <input v-model="form.phone" type="tel" :class="['form-control', errors.phone ? 'is-invalid' : '']"
                     placeholder="9876543210" data-testid="reg-phone" @input="clearError('phone')" />
              <div class="invalid-feedback">{{ errors.phone }}</div>
            </div>
            <div class="col-6">
              <label class="form-label">Age</label>
              <input v-model.number="form.age" type="number" class="form-control"
                     min="1" max="120" placeholder="25" data-testid="reg-age" />
            </div>
            <div class="col-6">
              <label class="form-label">Gender</label>
              <select v-model="form.gender" class="form-select" data-testid="reg-gender">
                <option value="">Select</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
            <div class="col-6">
              <label class="form-label">Blood Group</label>
              <select v-model="form.blood_group" class="form-select" data-testid="reg-blood">
                <option value="">Select</option>
                <option v-for="bg in bloodGroups" :key="bg">{{ bg }}</option>
              </select>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100 mt-3 py-2" :disabled="loading"
                  data-testid="register-submit-btn">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Registering...' : 'Create Account' }}
          </button>
        </form>

        <p class="text-center text-muted small mt-3 mb-0">
          Already have an account?
          <router-link to="/login" class="text-primary fw-semibold">Sign In</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/utils/api.js'

const form = reactive({
  name: '', username: '', email: '', password: '', confirmPassword: '',
  phone: '', age: '', gender: '', blood_group: ''
})
const errors = reactive({})
const loading = ref(false)
const error = ref('')
const success = ref('')
const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

function clearError(field) {
  delete errors[field]
}

function validate() {
  const e = {}
  if (!form.name.trim()) e.name = 'Full name is required.'
  if (!form.username.trim()) e.username = 'Username is required.'
  else if (form.username.length < 3) e.username = 'Username must be at least 3 characters.'
  else if (!/^[a-zA-Z0-9._]+$/.test(form.username)) e.username = 'Username: only letters, numbers, dots, underscores.'
  if (!form.email.trim()) e.email = 'Email is required.'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Enter a valid email address.'
  if (!form.password) e.password = 'Password is required.'
  else if (form.password.length < 6) e.password = 'Password must be at least 6 characters.'
  if (!form.confirmPassword) e.confirmPassword = 'Please confirm your password.'
  else if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match.'
  if (form.phone && !/^[0-9+\-\s]{7,15}$/.test(form.phone)) e.phone = 'Enter a valid phone number.'
  Object.assign(errors, e)
  return Object.keys(e).length === 0
}

async function handleRegister() {
  error.value = ''
  success.value = ''
  if (!validate()) return
  loading.value = true
  try {
    const { confirmPassword, ...payload } = form
    await api.post('/api/auth/register', payload)
    success.value = 'Registration successful!'
    Object.keys(form).forEach(k => form[k] = '')
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>
