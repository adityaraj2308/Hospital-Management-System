import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('hms_token') || null)
  const role = ref(localStorage.getItem('hms_role') || null)
  const username = ref(localStorage.getItem('hms_username') || null)
  const name = ref(localStorage.getItem('hms_name') || null)
  const profileId = ref(localStorage.getItem('hms_profile_id') || null)
  const userId = ref(localStorage.getItem('hms_user_id') || null)

  const isAuthenticated = computed(() => !!token.value)

  function login(data) {
    token.value = data.token
    role.value = data.role
    username.value = data.username
    name.value = data.name
    profileId.value = data.profile_id
    userId.value = data.user_id
    localStorage.setItem('hms_token', data.token)
    localStorage.setItem('hms_role', data.role)
    localStorage.setItem('hms_username', data.username)
    localStorage.setItem('hms_name', data.name)
    localStorage.setItem('hms_profile_id', data.profile_id)
    localStorage.setItem('hms_user_id', data.user_id)
  }

  function logout() {
    token.value = null
    role.value = null
    username.value = null
    name.value = null
    profileId.value = null
    userId.value = null
    localStorage.removeItem('hms_token')
    localStorage.removeItem('hms_role')
    localStorage.removeItem('hms_username')
    localStorage.removeItem('hms_name')
    localStorage.removeItem('hms_profile_id')
    localStorage.removeItem('hms_user_id')
  }

  return { token, role, username, name, profileId, userId, isAuthenticated, login, logout }
})
