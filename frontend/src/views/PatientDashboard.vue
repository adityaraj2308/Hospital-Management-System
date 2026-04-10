<template>
  <div>
    <NavBar @tabChange="activeTab = $event" />
    <div class="container-fluid py-4" data-testid="patient-dashboard">

      <!-- Welcome Banner -->
      <div class="card bg-primary text-white mb-4">
        <div class="card-body d-flex align-items-center justify-content-between flex-wrap gap-3">
          <div>
            <h4 class="mb-1">Welcome, {{ authStore.name }}</h4>
            <p class="mb-0 opacity-75">Manage your appointments and health records</p>
          </div>
          <div class="d-flex gap-3">
            <div class="text-center">
              <div class="fs-3 fw-bold">{{ dashboard.stats?.upcoming_count || 0 }}</div>
              <small>Upcoming</small>
            </div>
            <div class="text-center">
              <div class="fs-3 fw-bold">{{ dashboard.stats?.total_visits || 0 }}</div>
              <small>Completed</small>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header bg-white border-0 pt-3">
          <ul class="nav nav-tabs border-0">
            <li class="nav-item" v-for="tab in tabs" :key="tab.key">
              <button :class="['nav-link', activeTab === tab.key ? 'active' : '']"
                      @click="activeTab = tab.key" :data-testid="`patient-tab-${tab.key}`">
                <i :class="`bi ${tab.icon} me-1`"></i>{{ tab.label }}
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body">

          <!-- FIND DOCTORS -->
          <div v-if="activeTab === 'doctors'" data-testid="find-doctors">
            <div class="row g-3 mb-3">
              <div class="col-md-4">
                <input v-model="doctorSearch.name" type="text" class="form-control"
                       placeholder="Search by doctor name..." data-testid="doctor-name-search" />
              </div>
              <div class="col-md-4">
                <select v-model="doctorSearch.specialization" class="form-select" data-testid="specialization-filter">
                  <option value="">All Specializations</option>
                  <option v-for="d in departments" :key="d.id" :value="d.name">{{ d.name }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <button class="btn btn-primary w-100" @click="searchDoctors" data-testid="search-doctors-btn">
                  <i class="bi bi-search me-1"></i>Search Doctors
                </button>
              </div>
            </div>

            <div class="row g-3">
              <div class="col-md-6 col-lg-4" v-for="doc in doctors" :key="doc.id" :data-testid="`doctor-card-${doc.id}`">
                <div class="card h-100">
                  <div class="card-body">
                    <div class="d-flex align-items-start gap-3">
                      <div class="avatar-circle bg-success text-white flex-shrink-0">
                        {{ doc.name.charAt(0) }}
                      </div>
                      <div class="flex-grow-1 min-w-0">
                        <h6 class="mb-1">{{ doc.name }}</h6>
                        <span class="badge bg-primary mb-1">{{ doc.specialization }}</span>
                        <p class="text-muted small mb-1">{{ doc.department || 'General' }}</p>
                        <p class="text-muted small mb-0">{{ doc.experience_years }} yrs experience</p>
                      </div>
                    </div>
                    <div class="mt-3" v-if="doc.availability?.length">
                      <p class="small fw-semibold mb-1">Available slots:</p>
                      <div class="d-flex flex-wrap gap-1">
                        <span v-for="a in doc.availability.slice(0,4)" :key="a.date"
                              class="badge bg-light text-dark border small">
                          {{ formatDateShort(a.date) }}
                        </span>
                      </div>
                    </div>
                    <p v-else class="text-muted small mt-2 mb-0">No availability set</p>
                    <button class="btn btn-primary btn-sm w-100 mt-3"
                            @click="openBookingModal(doc)"
                            :disabled="!doc.availability?.length"
                            :data-testid="`book-btn-${doc.id}`">
                      <i class="bi bi-calendar-plus me-1"></i>Book Appointment
                    </button>
                  </div>
                </div>
              </div>
              <div class="col-12 text-center text-muted py-4" v-if="!doctors.length">
                No doctors found. Try a different search.
              </div>
            </div>
          </div>

          <!-- MY APPOINTMENTS -->
          <div v-if="activeTab === 'appointments'" data-testid="my-appointments">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">My Appointments</h5>
              <select v-model="apptFilter" class="form-select" style="width:180px" @change="loadAppointments">
                <option value="">All</option>
                <option>Booked</option><option>Completed</option><option>Cancelled</option>
              </select>
            </div>
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead><tr>
                  <th>Doctor</th><th>Specialization</th><th>Date</th><th>Time</th>
                  <th>Status</th><th>Reason</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  <tr v-for="a in appointments" :key="a.id" :data-testid="`appt-row-${a.id}`">
                    <td>{{ a.doctor_name }}</td>
                    <td>{{ a.doctor_specialization }}</td>
                    <td>{{ a.date }}</td>
                    <td>{{ a.time }}</td>
                    <td><span :class="`badge badge-status-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
                    <td>{{ a.reason || '—' }}</td>
                    <td>
                      <button v-if="a.status === 'Booked'" class="btn btn-sm btn-outline-warning me-1"
                              @click="openRescheduleModal(a)" :data-testid="`reschedule-btn-${a.id}`">
                        <i class="bi bi-calendar-event"></i>
                      </button>
                      <button v-if="a.status === 'Booked'" class="btn btn-sm btn-outline-danger"
                              @click="cancelAppointment(a)" :data-testid="`cancel-btn-${a.id}`">
                        <i class="bi bi-x-circle"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!appointments.length"><td colspan="7" class="text-center text-muted py-4">No appointments</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TREATMENT HISTORY -->
          <div v-if="activeTab === 'history'" data-testid="treatment-history">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">Treatment History</h5>
              <button class="btn btn-outline-success btn-sm" @click="triggerExport"
                      :disabled="exportLoading" data-testid="export-csv-btn">
                <span v-if="exportLoading" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-download me-1"></i>
                {{ exportLoading ? 'Exporting...' : 'Export as CSV' }}
              </button>
            </div>
            <div v-if="exportMessage" :class="`alert alert-${exportMessageType} py-2 small d-flex align-items-center gap-2`" data-testid="export-message">
              <span v-if="exportLoading" class="spinner-border spinner-border-sm flex-shrink-0"></span>
              <i v-else-if="exportMessageType === 'success'" class="bi bi-check-circle-fill flex-shrink-0"></i>
              <i v-else class="bi bi-exclamation-triangle-fill flex-shrink-0"></i>
              {{ exportMessage }}
            </div>

            <!-- Mini chart: visits per month -->
            <div v-if="history.length" class="card mb-3">
              <div class="card-header bg-white fw-semibold small">
                <i class="bi bi-activity me-2 text-primary"></i>Your Visit History Timeline
              </div>
              <div class="card-body py-2">
                <canvas ref="patientHistChartRef" height="80" data-testid="patient-hist-chart"></canvas>
              </div>
            </div>
            <div v-if="!history.length" class="text-center text-muted py-5">
              <i class="bi bi-file-medical fs-1 d-block mb-2"></i>
              No treatment history found
            </div>
            <div class="accordion" id="historyAccordion" v-else>
              <div class="accordion-item" v-for="a in history" :key="a.id"
                   :data-testid="`history-item-${a.id}`">
                <h2 class="accordion-header">
                  <button class="accordion-button collapsed" type="button"
                          :data-bs-target="`#hist-${a.id}`" data-bs-toggle="collapse">
                    <span class="me-2">{{ a.date }}</span>
                    <strong class="me-2">Dr. {{ a.doctor_name }}</strong>
                    <span class="badge bg-info">{{ a.doctor_specialization }}</span>
                  </button>
                </h2>
                <div :id="`hist-${a.id}`" class="accordion-collapse collapse" data-bs-parent="#historyAccordion">
                  <div class="accordion-body">
                    <div class="row g-3" v-if="a.treatment">
                      <div class="col-md-4">
                        <div class="p-3 bg-light rounded">
                          <h6 class="text-primary">Diagnosis</h6>
                          <p class="mb-0">{{ a.treatment.diagnosis || '—' }}</p>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="p-3 bg-light rounded">
                          <h6 class="text-success">Prescription</h6>
                          <p class="mb-0" style="white-space:pre-wrap">{{ a.treatment.prescription || '—' }}</p>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="p-3 bg-light rounded">
                          <h6 class="text-warning">Doctor Notes</h6>
                          <p class="mb-0">{{ a.treatment.notes || '—' }}</p>
                          <p class="mb-0 mt-2 text-muted small" v-if="a.treatment.next_visit">
                            Next visit: <strong>{{ a.treatment.next_visit }}</strong>
                          </p>
                        </div>
                      </div>
                    </div>
                    <p v-else class="text-muted mb-0">No treatment details available</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- DEPARTMENTS -->
          <div v-if="activeTab === 'departments'" data-testid="departments-tab">
            <h5 class="mb-3">Available Specializations</h5>
            <div class="row g-3">
              <div class="col-md-4 col-sm-6" v-for="dept in departments" :key="dept.id"
                   :data-testid="`dept-card-${dept.id}`">
                <div class="card h-100 text-center p-3">
                  <div class="fs-1 mb-2">
                    <i :class="`bi ${getDeptIcon(dept.name)} text-primary`"></i>
                  </div>
                  <h6 class="fw-bold">{{ dept.name }}</h6>
                  <p class="text-muted small mb-2">{{ dept.description || 'Specialized medical care' }}</p>
                  <span class="badge bg-secondary">{{ dept.doctors_count }} doctor(s)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- PROFILE -->
          <div v-if="activeTab === 'profile'" data-testid="patient-profile">
            <div class="row">
              <div class="col-md-6">
                <h5 class="mb-3">My Profile</h5>
                <div v-if="profileSuccess" class="alert alert-success py-2 small">Profile updated!</div>
                <form @submit.prevent="saveProfile">
                  <div class="row g-2">
                    <div class="col-12">
                      <label class="form-label">Full Name</label>
                      <input v-model="profileForm.name" type="text" class="form-control" required data-testid="profile-name" />
                    </div>
                    <div class="col-6">
                      <label class="form-label">Age</label>
                      <input v-model.number="profileForm.age" type="number" class="form-control" min="1" max="120" data-testid="profile-age" />
                    </div>
                    <div class="col-6">
                      <label class="form-label">Gender</label>
                      <select v-model="profileForm.gender" class="form-select" data-testid="profile-gender">
                        <option value="">Select</option>
                        <option>Male</option><option>Female</option><option>Other</option>
                      </select>
                    </div>
                    <div class="col-6">
                      <label class="form-label">Phone</label>
                      <input v-model="profileForm.phone" type="text" class="form-control" data-testid="profile-phone" />
                    </div>
                    <div class="col-6">
                      <label class="form-label">Blood Group</label>
                      <select v-model="profileForm.blood_group" class="form-select" data-testid="profile-blood">
                        <option value="">Select</option>
                        <option v-for="bg in bloodGroups" :key="bg">{{ bg }}</option>
                      </select>
                    </div>
                    <div class="col-12">
                      <label class="form-label">Address</label>
                      <textarea v-model="profileForm.address" class="form-control" rows="2" data-testid="profile-address"></textarea>
                    </div>
                    <div class="col-12">
                      <label class="form-label">Emergency Contact</label>
                      <input v-model="profileForm.emergency_contact" type="text" class="form-control" data-testid="profile-emergency" />
                    </div>
                  </div>
                  <button type="submit" class="btn btn-primary mt-3" data-testid="save-profile-btn">Save Changes</button>
                </form>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Book Appointment Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1" data-testid="booking-modal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title"><i class="bi bi-calendar-plus me-2"></i>Book Appointment</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="bookingDoc">
            <div class="alert alert-light mb-3">
              <strong>{{ bookingDoc.name }}</strong> &mdash; {{ bookingDoc.specialization }}
            </div>
            <div v-if="bookingError" class="alert alert-danger py-2 small">{{ bookingError }}</div>
            <form @submit.prevent="confirmBooking" id="bookingForm">
              <div class="mb-3">
                <label class="form-label">Select Date *</label>
                <select v-model="bookingForm.date" class="form-select" required
                        @change="loadTimeSlots" data-testid="booking-date">
                  <option value="">Choose available date</option>
                  <option v-for="a in bookingDoc.availability" :key="a.date"
                          :value="a.date">
                    {{ formatDateShort(a.date) }} ({{ a.slots_remaining || a.max_appointments }} slots)
                  </option>
                </select>
              </div>
              <div class="mb-3" v-if="bookingForm.date">
                <label class="form-label">Select Time *</label>
                <select v-model="bookingForm.time" class="form-select" required data-testid="booking-time">
                  <option value="">Choose time</option>
                  <option v-for="t in timeSlots" :key="t" :value="t">{{ t }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Reason for Visit</label>
                <textarea v-model="bookingForm.reason" class="form-control" rows="2"
                          placeholder="Describe your symptoms or reason..." data-testid="booking-reason"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" form="bookingForm" class="btn btn-primary" :disabled="booking"
                    data-testid="confirm-booking-btn">
              <span v-if="booking" class="spinner-border spinner-border-sm me-1"></span>
              {{ booking ? 'Booking...' : 'Confirm Booking' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div class="modal fade" id="rescheduleModal" tabindex="-1" data-testid="reschedule-modal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reschedule Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="reschedAppt">
            <div class="alert alert-light mb-3">
              <strong>Dr. {{ reschedAppt.doctor_name }}</strong> &mdash; Current: {{ reschedAppt.date }} {{ reschedAppt.time }}
            </div>
            <div v-if="reschedError" class="alert alert-danger py-2 small">{{ reschedError }}</div>
            <form @submit.prevent="confirmReschedule" id="reschedForm">
              <div class="mb-3">
                <label class="form-label">New Date</label>
                <input v-model="reschedForm.date" type="date" class="form-control"
                       :min="today" required data-testid="resched-date" />
              </div>
              <div class="mb-3">
                <label class="form-label">New Time</label>
                <select v-model="reschedForm.time" class="form-select" required data-testid="resched-time">
                  <option value="">Choose time</option>
                  <option v-for="t in timeSlots" :key="t" :value="t">{{ t }}</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" form="reschedForm" class="btn btn-warning" data-testid="confirm-reschedule-btn">
              Reschedule
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { Modal } from 'bootstrap'
import { Chart, registerables } from 'chart.js'
import NavBar from '@/components/Navbar.vue'
import { useAuthStore } from '@/store/auth.js'
import api from '@/utils/api.js'

Chart.register(...registerables)

const authStore = useAuthStore()
const activeTab = ref('doctors')
const tabs = [
  { key: 'doctors', label: 'Find Doctors', icon: 'bi-search' },
  { key: 'appointments', label: 'My Appointments', icon: 'bi-calendar-check' },
  { key: 'history', label: 'Treatment History', icon: 'bi-file-medical' },
  { key: 'departments', label: 'Departments', icon: 'bi-building' },
  { key: 'profile', label: 'My Profile', icon: 'bi-person-circle' },
]

const dashboard = ref({ upcoming_appointments: [], recent_history: [], stats: {} })
const doctors = ref([])
const departments = ref([])
const appointments = ref([])
const history = ref([])
const apptFilter = ref('')
const exportLoading = ref(false)
const exportMessage = ref('')
const exportMessageType = ref('success')
const profileSuccess = ref(false)

const doctorSearch = reactive({ name: '', specialization: '' })
const profileForm = reactive({ name: '', age: '', gender: '', phone: '', address: '', blood_group: '', emergency_contact: '' })
const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

const today = new Date().toISOString().split('T')[0]

// Booking
const bookingDoc = ref(null)
const bookingForm = reactive({ date: '', time: '', reason: '' })
const bookingError = ref('')
const booking = ref(false)
const timeSlots = ref([])
let bookingModal = null

// Reschedule
const reschedAppt = ref(null)
const reschedForm = reactive({ date: '', time: '' })
const reschedError = ref('')
let reschedModal = null

function generateTimeSlots(start = '09:00', end = '17:00', interval = 30) {
  const slots = []
  let [h, m] = start.split(':').map(Number)
  const [eh, em] = end.split(':').map(Number)
  while (h < eh || (h === eh && m < em)) {
    slots.push(`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`)
    m += interval
    if (m >= 60) { h++; m -= 60 }
  }
  return slots
}

function loadTimeSlots() {
  if (!bookingForm.date || !bookingDoc.value) return
  const avail = bookingDoc.value.availability?.find(a => a.date === bookingForm.date)
  if (avail) {
    timeSlots.value = generateTimeSlots(avail.start_time, avail.end_time)
  } else {
    timeSlots.value = generateTimeSlots()
  }
}

function formatDateShort(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })
}

function getDeptIcon(name) {
  const icons = {
    Cardiology: 'bi-heart-pulse', Neurology: 'bi-brain', Orthopedics: 'bi-person-walking',
    Pediatrics: 'bi-emoji-smile', Dermatology: 'bi-person', 'General Medicine': 'bi-clipboard2-pulse',
    Gynecology: 'bi-gender-female', ENT: 'bi-ear'
  }
  return icons[name] || 'bi-hospital'
}

async function loadDashboard() {
  const res = await api.get('/api/patient/dashboard')
  dashboard.value = res.data
  if (res.data.patient) {
    Object.assign(profileForm, {
      name: res.data.patient.name || '',
      age: res.data.patient.age || '',
      gender: res.data.patient.gender || '',
      phone: res.data.patient.phone || '',
      address: res.data.patient.address || '',
      blood_group: res.data.patient.blood_group || '',
      emergency_contact: res.data.patient.emergency_contact || ''
    })
  }
}

async function loadDepartments() {
  const res = await api.get('/api/patient/departments')
  departments.value = res.data
}

async function searchDoctors() {
  const res = await api.get('/api/patient/doctors', { params: doctorSearch })
  doctors.value = res.data
}

async function loadAppointments() {
  const params = apptFilter.value ? { status: apptFilter.value } : {}
  const res = await api.get('/api/patient/appointments', { params })
  appointments.value = res.data
}

async function loadHistory() {
  const res = await api.get('/api/patient/history')
  history.value = res.data
}

function openBookingModal(doc) {
  bookingDoc.value = doc
  bookingForm.date = ''
  bookingForm.time = ''
  bookingForm.reason = ''
  bookingError.value = ''
  timeSlots.value = []
  bookingModal?.show()
}

async function confirmBooking() {
  booking.value = true
  bookingError.value = ''

  // JS validation
  if (!bookingForm.date) { bookingError.value = 'Please select an appointment date.'; booking.value = false; return }
  if (!bookingForm.time) { bookingError.value = 'Please select a time slot.'; booking.value = false; return }
  const today = new Date().toISOString().split('T')[0]
  if (bookingForm.date < today) { bookingError.value = 'Cannot book an appointment in the past.'; booking.value = false; return }

  try {
    await api.post('/api/patient/appointments', {
      doctor_id: bookingDoc.value.id,
      date: bookingForm.date,
      time: bookingForm.time,
      reason: bookingForm.reason
    })
    bookingModal?.hide()
    await Promise.all([loadDashboard(), loadAppointments()])
    activeTab.value = 'appointments'
  } catch (e) {
    bookingError.value = e.response?.data?.error || 'Booking failed'
  } finally {
    booking.value = false
  }
}

function openRescheduleModal(appt) {
  reschedAppt.value = appt
  reschedForm.date = appt.date
  reschedForm.time = appt.time
  reschedError.value = ''
  timeSlots.value = generateTimeSlots()
  reschedModal?.show()
}

async function confirmReschedule() {
  reschedError.value = ''

  // JS validation
  const today = new Date().toISOString().split('T')[0]
  if (!reschedForm.date) { reschedError.value = 'Please select a new date.'; return }
  if (reschedForm.date < today) { reschedError.value = 'Cannot reschedule to a past date.'; return }
  if (!reschedForm.time) { reschedError.value = 'Please select a new time slot.'; return }

  try {
    await api.put(`/api/patient/appointments/${reschedAppt.value.id}`, {
      action: 'reschedule', date: reschedForm.date, time: reschedForm.time
    })
    reschedModal?.hide()
    await loadAppointments()
  } catch (e) {
    reschedError.value = e.response?.data?.error || 'Reschedule failed'
  }
}

async function cancelAppointment(appt) {
  if (!confirm('Cancel this appointment?')) return
  await api.delete(`/api/patient/appointments/${appt.id}`)
  await loadAppointments()
}

async function triggerExport() {
  exportLoading.value = true
  exportMessage.value = ''

  try {
    const response = await api.post('/api/patient/export-csv', {}, {
      responseType: 'blob'
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'patient_history.csv')
    document.body.appendChild(link)
    link.click()

    exportMessage.value = 'CSV downloaded successfully!'
    exportMessageType.value = 'success'
  } catch (e) {
    exportMessage.value = 'Download failed. Try again.'
    exportMessageType.value = 'danger'
  } finally {
    exportLoading.value = false
  }
}

async function pollExportStatus(taskId) {
  const maxAttempts = 30  // 30 × 2s = 60s max wait
  let attempts = 0

  const check = async () => {
    attempts++
    try {
      const res = await api.get(`/api/patient/export-status/${taskId}`)
      const { state } = res.data
      if (state === 'SUCCESS') {
        exportMessage.value = 'Export complete! Your treatment history CSV has been sent to your email.'
        exportMessageType.value = 'success'
        exportLoading.value = false
      } else if (state === 'FAILURE') {
        exportMessage.value = 'Export failed. Please try again.'
        exportMessageType.value = 'danger'
        exportLoading.value = false
      } else if (attempts < maxAttempts) {
        exportMessage.value = `Processing... (${attempts * 2}s elapsed)`
        setTimeout(check, 2000)
      } else {
        exportMessage.value = 'Export is taking longer than expected. Check your email in a few minutes.'
        exportMessageType.value = 'warning'
        exportLoading.value = false
      }
    } catch {
      exportMessage.value = 'Export queued. You will receive an email when ready.'
      exportMessageType.value = 'success'
      exportLoading.value = false
    }
  }

  setTimeout(check, 2000)
}

async function saveProfile() {
  profileSuccess.value = false
  try {
    await api.put('/api/patient/profile', profileForm)
    profileSuccess.value = true
    setTimeout(() => profileSuccess.value = false, 3000)
    await loadDashboard()
  } catch (e) {
    alert(e.response?.data?.error || 'Update failed')
  }
}

// Patient history chart
const patientHistChartRef = ref(null)
let patientHistChart = null

async function renderPatientChart() {
  await nextTick()
  if (!history.value.length || !patientHistChartRef.value) return
  if (patientHistChart) patientHistChart.destroy()

  // Group visits by month
  const monthMap = {}
  history.value.forEach(a => {
    if (a.date) {
      const m = a.date.substring(0, 7)
      monthMap[m] = (monthMap[m] || 0) + 1
    }
  })
  const sortedMonths = Object.keys(monthMap).sort()
  
  patientHistChart = new Chart(patientHistChartRef.value, {
    type: 'line',
    data: {
      labels: sortedMonths.length ? sortedMonths : ['No visits'],
      datasets: [{
        label: 'Visits',
        data: sortedMonths.map(m => monthMap[m]),
        backgroundColor: '#0d6efd22',
        borderColor: '#0d6efd',
        borderWidth: 2,
        pointRadius: 5,
        pointBackgroundColor: '#0d6efd',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1 } },
        x: { grid: { display: false } }
      }
    }
  })
}

watch(activeTab, async (val) => {
  if (val === 'history') {
    await nextTick()
    renderPatientChart()
  }
})


async function loadDoctors() {
  const res = await api.get('/api/patient/doctors', { params: {} })
  doctors.value = res.data
}

onMounted(async () => {
  await Promise.all([loadDashboard(), loadDepartments(), loadDoctors(), loadAppointments(), loadHistory()])
  bookingModal = new Modal(document.getElementById('bookingModal'))
  reschedModal = new Modal(document.getElementById('rescheduleModal'))
})
</script>
