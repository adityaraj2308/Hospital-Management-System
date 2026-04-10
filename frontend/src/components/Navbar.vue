<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top shadow-sm" data-testid="navbar">
    <div class="container-fluid">

      <!-- Brand -->
      <a class="navbar-brand fw-bold" href="#">
        <i class="bi bi-hospital me-2"></i>HMS
        <small class="ms-1 opacity-75 d-none d-md-inline" style="font-size:0.65rem;font-weight:400">Hospital Management</small>
      </a>

      <!-- Hamburger -->
      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMain"
              aria-controls="navMain" aria-expanded="false">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navMain">

        <!-- Nav links by role -->
        <ul class="navbar-nav me-auto gap-1" v-if="authStore.role === 'admin'">
          <li class="nav-item" v-for="link in adminLinks" :key="link.tab">
            <button class="nav-link btn btn-link text-white" @click="go(link.tab)"
                    :data-testid="`nav-${link.tab}`">
              <i :class="`bi ${link.icon} me-1`"></i>{{ link.label }}
            </button>
          </li>
        </ul>

        <ul class="navbar-nav me-auto gap-1" v-else-if="authStore.role === 'doctor'">
          <li class="nav-item" v-for="link in doctorLinks" :key="link.tab">
            <button class="nav-link btn btn-link text-white" @click="go(link.tab)"
                    :data-testid="`nav-${link.tab}`">
              <i :class="`bi ${link.icon} me-1`"></i>{{ link.label }}
            </button>
          </li>
        </ul>

        <ul class="navbar-nav me-auto gap-1" v-else-if="authStore.role === 'patient'">
          <li class="nav-item" v-for="link in patientLinks" :key="link.tab">
            <button class="nav-link btn btn-link text-white" @click="go(link.tab)"
                    :data-testid="`nav-${link.tab}`">
              <i :class="`bi ${link.icon} me-1`"></i>{{ link.label }}
            </button>
          </li>
        </ul>

        <!-- Right side: user info + profile + logout (always visible) -->
        <div class="navbar-nav ms-auto align-items-lg-center gap-2 mt-3 mt-lg-0 pb-2 pb-lg-0 border-top border-top-lg-0 pt-3 pt-lg-0"
             style="border-color:rgba(255,255,255,0.2) !important">

          <!-- User info -->
          <div class="d-flex align-items-center gap-2 me-2">
            <div class="avatar-circle bg-white text-primary flex-shrink-0"
                 style="width:36px;height:36px;font-size:1rem;font-weight:700;display:flex;align-items:center;justify-content:center;border-radius:50%">
              {{ authStore.name?.charAt(0)?.toUpperCase() }}
            </div>
            <div>
              <div class="text-white fw-semibold small lh-1">{{ authStore.name }}</div>
              <span :class="`badge mt-1 ${roleBadgeClass}`">{{ authStore.role }}</span>
            </div>
          </div>

          <!-- Profile button (not shown for admin — no profile editing needed) -->
          <button v-if="authStore.role !== 'admin'" class="btn btn-outline-light btn-sm"
                  @click="go('profile')" data-testid="profile-btn">
            <i class="bi bi-person-circle me-1"></i>Profile
          </button>

          <!-- Logout — always visible -->
          <button class="btn btn-light btn-sm fw-semibold text-danger" @click="logout"
                  data-testid="logout-btn">
            <i class="bi bi-box-arrow-right me-1"></i>Logout
          </button>
        </div>

      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'

const router = useRouter()
const authStore = useAuthStore()
const emit = defineEmits(['tabChange'])

const adminLinks = [
  { tab: 'doctors',      label: 'Doctors',      icon: 'bi-person-badge' },
  { tab: 'patients',     label: 'Patients',     icon: 'bi-people' },
  { tab: 'appointments', label: 'Appointments', icon: 'bi-calendar-check' },
  { tab: 'departments',  label: 'Departments',  icon: 'bi-building' },
  { tab: 'search',       label: 'Search',       icon: 'bi-search' },
  { tab: 'analytics',    label: 'Analytics',    icon: 'bi-bar-chart-line' },
]

const doctorLinks = [
  { tab: 'today',        label: 'Today',        icon: 'bi-calendar-day' },
  { tab: 'appointments', label: 'Appointments', icon: 'bi-calendar-check' },
  { tab: 'patients',     label: 'My Patients',  icon: 'bi-people' },
  { tab: 'availability', label: 'Availability', icon: 'bi-clock' },
  { tab: 'stats',        label: 'My Stats',     icon: 'bi-bar-chart-line' },
]

const patientLinks = [
  { tab: 'doctors',      label: 'Find Doctors', icon: 'bi-search' },
  { tab: 'appointments', label: 'Appointments', icon: 'bi-calendar-check' },
  { tab: 'history',      label: 'History',      icon: 'bi-file-medical' },
  { tab: 'departments',  label: 'Departments',  icon: 'bi-building' },
]

const roleBadgeClass = computed(() => ({
  admin:   'bg-warning text-dark',
  doctor:  'bg-success',
  patient: 'bg-info text-dark',
}[authStore.role] || 'bg-secondary'))

function go(tab) {
  emit('tabChange', tab)
  // Close mobile menu after navigation
  const menu = document.getElementById('navMain')
  if (menu?.classList.contains('show')) {
    const toggler = document.querySelector('.navbar-toggler')
    toggler?.click()
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>
