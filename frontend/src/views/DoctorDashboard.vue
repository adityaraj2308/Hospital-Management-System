<template>
  <div>
    <NavBar @tabChange="activeTab = $event" />
    <div class="container-fluid py-4" data-testid="doctor-dashboard">

      <!-- Welcome + Stats -->
      <div class="row g-3 mb-4">
        <div class="col-12">
          <div class="card bg-success text-white">
            <div class="card-body d-flex align-items-center justify-content-between">
              <div>
                <h4 class="mb-1">Welcome, {{ authStore.name }}</h4>
                <p class="mb-0 opacity-75"><i class="bi bi-stethoscope me-1"></i>{{ doctorInfo?.specialization }}</p>
              </div>
              <div class="d-flex gap-3">
                <div class="text-center">
                  <div class="fs-3 fw-bold">{{ dashboard.stats?.today_count || 0 }}</div>
                  <small>Today</small>
                </div>
                <div class="text-center">
                  <div class="fs-3 fw-bold">{{ dashboard.stats?.week_count || 0 }}</div>
                  <small>This Week</small>
                </div>
                <div class="text-center">
                  <div class="fs-3 fw-bold">{{ dashboard.stats?.total_patients || 0 }}</div>
                  <small>Patients</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header bg-white border-0 pt-3">
          <ul class="nav nav-tabs border-0">
            <li class="nav-item" v-for="tab in tabs" :key="tab.key">
              <button :class="['nav-link', activeTab === tab.key ? 'active' : '']"
                      @click="activeTab = tab.key" :data-testid="`doctor-tab-${tab.key}`">
                <i :class="`bi ${tab.icon} me-1`"></i>{{ tab.label }}
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body">

          <!-- TODAY'S APPOINTMENTS -->
          <div v-if="activeTab === 'today'" data-testid="today-appointments">
            <h5 class="mb-3">Today's Appointments</h5>
            <div v-if="!dashboard.today_appointments?.length" class="text-center text-muted py-5">
              <i class="bi bi-calendar-x fs-1 d-block mb-2"></i>
              No appointments scheduled for today
            </div>
            <div class="row g-3" v-else>
              <div class="col-md-6 col-lg-4" v-for="appt in dashboard.today_appointments" :key="appt.id"
                   :data-testid="`today-appt-${appt.id}`">
                <div class="card h-100">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="mb-0">{{ appt.patient_name }}</h6>
                      <span :class="`badge badge-status-${appt.status.toLowerCase()}`">{{ appt.status }}</span>
                    </div>
                    <p class="text-muted small mb-1"><i class="bi bi-clock me-1"></i>{{ appt.time }}</p>
                    <p class="text-muted small mb-2">{{ appt.reason || 'General consultation' }}</p>
                    <div class="d-flex gap-2" v-if="appt.status === 'Booked'">
                      <button class="btn btn-sm btn-success flex-fill"
                              @click="openTreatmentModal(appt)"
                              :data-testid="`complete-appt-${appt.id}`">
                        <i class="bi bi-check2-circle me-1"></i>Complete
                      </button>
                      <button class="btn btn-sm btn-outline-danger"
                              @click="updateStatus(appt, 'Cancelled')"
                              :data-testid="`cancel-appt-${appt.id}`">
                        <i class="bi bi-x"></i>
                      </button>
                    </div>
                    <button v-if="appt.treatment" class="btn btn-sm btn-outline-info w-100"
                            @click="openTreatmentModal(appt)">
                      <i class="bi bi-file-medical me-1"></i>View Treatment
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ALL APPOINTMENTS -->
          <div v-if="activeTab === 'appointments'" data-testid="all-appointments">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">All Appointments</h5>
              <select v-model="apptFilter" class="form-select" style="width:180px" @change="loadAllAppointments">
                <option value="">All Status</option>
                <option>Booked</option><option>Completed</option><option>Cancelled</option>
              </select>
            </div>
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead><tr>
                  <th>Patient</th><th>Date</th><th>Time</th><th>Status</th><th>Reason</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  <tr v-for="a in allAppointments" :key="a.id" :data-testid="`appt-row-${a.id}`">
                    <td>{{ a.patient_name }}</td>
                    <td>{{ a.date }}</td>
                    <td>{{ a.time }}</td>
                    <td><span :class="`badge badge-status-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
                    <td>{{ a.reason || '—' }}</td>
                    <td>
                      <button v-if="a.status !== 'Cancelled'" class="btn btn-sm btn-outline-primary me-1"
                              @click="openTreatmentModal(a)" :data-testid="`treatment-btn-${a.id}`">
                        <i class="bi bi-file-medical"></i>
                      </button>
                      <button v-if="a.status === 'Booked'" class="btn btn-sm btn-outline-danger"
                              @click="updateStatus(a, 'Cancelled')">
                        <i class="bi bi-x-circle"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!allAppointments.length"><td colspan="6" class="text-center text-muted py-4">No appointments</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- MY PATIENTS -->
          <div v-if="activeTab === 'patients'" data-testid="my-patients">
            <h5 class="mb-3">My Patients</h5>
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead><tr><th>Name</th><th>Age</th><th>Gender</th><th>Phone</th><th>Blood Group</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="p in myPatients" :key="p.id" :data-testid="`patient-row-${p.id}`">
                    <td><strong>{{ p.name }}</strong></td>
                    <td>{{ p.age || '—' }}</td>
                    <td>{{ p.gender || '—' }}</td>
                    <td>{{ p.phone || '—' }}</td>
                    <td><span class="badge bg-secondary">{{ p.blood_group || '—' }}</span></td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary" @click="viewPatientHistory(p)"
                              :data-testid="`history-btn-${p.id}`">
                        <i class="bi bi-clock-history me-1"></i>History
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!myPatients.length"><td colspan="6" class="text-center text-muted py-4">No patients assigned yet</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- AVAILABILITY -->
          <div v-if="activeTab === 'availability'" data-testid="availability-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">Set Availability (Next 7 Days)</h5>
              <button class="btn btn-primary btn-sm" @click="saveAvailability" :disabled="savingAvail"
                      data-testid="save-availability-btn">
                <span v-if="savingAvail" class="spinner-border spinner-border-sm me-1"></span>
                Save Availability
              </button>
            </div>
            <div class="row g-3">
              <div class="col-md-4" v-for="slot in availSlots" :key="slot.date" :data-testid="`avail-slot-${slot.date}`">
                <div class="card">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <strong>{{ formatDate(slot.date) }}</strong>
                      <div class="form-check form-switch mb-0">
                        <input class="form-check-input" type="checkbox" v-model="slot.is_available"
                               :id="`avail-${slot.date}`" />
                        <label :for="`avail-${slot.date}`" class="form-check-label small">Available</label>
                      </div>
                    </div>
                    <div v-if="slot.is_available" class="row g-2">
                      <div class="col-6">
                        <label class="form-label small mb-1">Start Time</label>
                        <input type="time" v-model="slot.start_time" class="form-control form-control-sm" />
                      </div>
                      <div class="col-6">
                        <label class="form-label small mb-1">End Time</label>
                        <input type="time" v-model="slot.end_time" class="form-control form-control-sm" />
                      </div>
                      <div class="col-12">
                        <label class="form-label small mb-1">Max Appointments</label>
                        <input type="number" v-model.number="slot.max_appointments" class="form-control form-control-sm" min="1" max="20" />
                      </div>
                    </div>
                    <p v-else class="text-muted small mt-2 mb-0">Not available on this day</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- PROFILE -->
          <div v-if="activeTab === 'profile'" data-testid="doctor-profile">
            <div class="row">
              <div class="col-md-6">
                <h5 class="mb-3">My Profile</h5>
                <form @submit.prevent="saveProfile">
                  <div class="mb-3">
                    <label class="form-label">Phone</label>
                    <input v-model="profileForm.phone" type="text" class="form-control" data-testid="profile-phone" />
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Qualification</label>
                    <input v-model="profileForm.qualification" type="text" class="form-control" data-testid="profile-qual" />
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Bio</label>
                    <textarea v-model="profileForm.bio" class="form-control" rows="3" data-testid="profile-bio"></textarea>
                  </div>
                  <button type="submit" class="btn btn-primary" data-testid="save-profile-btn">Save Changes</button>
                </form>
              </div>
            </div>
          </div>

          <!-- MY STATS (Charts) -->
          <div v-if="activeTab === 'stats'" data-testid="doctor-stats-tab">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="mb-0"><i class="bi bi-bar-chart-line me-2 text-success"></i>My Activity Stats</h5>
            </div>
            <div class="row g-4">
              <!-- Week appointments bar -->
              <div class="col-lg-8">
                <div class="card">
                  <div class="card-header bg-white fw-semibold">
                    <i class="bi bi-graph-up me-2 text-success"></i>Weekly Appointment Schedule
                  </div>
                  <div class="card-body">
                    <canvas ref="weekChartRef" height="220" data-testid="week-chart"></canvas>
                  </div>
                </div>
              </div>
              <!-- Status doughnut -->
              <div class="col-lg-4">
                <div class="card">
                  <div class="card-header bg-white fw-semibold">
                    <i class="bi bi-pie-chart me-2 text-info"></i>Appointment Status
                  </div>
                  <div class="card-body d-flex align-items-center justify-content-center" style="min-height:260px">
                    <canvas ref="docStatusChartRef" data-testid="doc-status-chart"></canvas>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
    <div class="modal fade" id="treatmentModal" tabindex="-1" data-testid="treatment-modal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title"><i class="bi bi-file-medical me-2"></i>Treatment Record</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedAppt">
            <div class="alert alert-light mb-3">
              <strong>{{ selectedAppt.patient_name }}</strong> &mdash;
              {{ selectedAppt.date }} at {{ selectedAppt.time }}
            </div>
            <form @submit.prevent="saveTreatment" id="treatmentForm">
              <div class="mb-3">
                <label class="form-label fw-semibold">Diagnosis *</label>
                <textarea v-model="treatmentForm.diagnosis" class="form-control" rows="3"
                          placeholder="Enter diagnosis..." data-testid="diagnosis-input"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Prescription</label>
                <textarea v-model="treatmentForm.prescription" class="form-control" rows="3"
                          placeholder="Medicines, dosage..." data-testid="prescription-input"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Doctor Notes</label>
                <textarea v-model="treatmentForm.notes" class="form-control" rows="2"
                          placeholder="Additional notes..." data-testid="notes-input"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">Next Visit Date</label>
                <input v-model="treatmentForm.next_visit" type="date" class="form-control"
                       :min="today" data-testid="next-visit-input" />
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="submit" form="treatmentForm" class="btn btn-success" :disabled="saving"
                    data-testid="save-treatment-btn">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ saving ? 'Saving...' : 'Save Treatment' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient History Modal -->
    <div class="modal fade" id="patientHistoryModal" tabindex="-1" data-testid="patient-history-modal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient History: {{ patientHistory?.patient?.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="patientHistory">
            <div class="row g-2 mb-3">
              <div class="col-md-3"><strong>Age:</strong> {{ patientHistory.patient.age || '—' }}</div>
              <div class="col-md-3"><strong>Gender:</strong> {{ patientHistory.patient.gender || '—' }}</div>
              <div class="col-md-3"><strong>Blood Group:</strong> {{ patientHistory.patient.blood_group || '—' }}</div>
              <div class="col-md-3"><strong>Phone:</strong> {{ patientHistory.patient.phone || '—' }}</div>
            </div>
            <div class="accordion" id="historyAccordion">
              <div class="accordion-item" v-for="(a, idx) in patientHistory.history" :key="a.id">
                <h2 class="accordion-header">
                  <button class="accordion-button collapsed" type="button"
                          :data-bs-target="`#collapse-${a.id}`" data-bs-toggle="collapse">
                    {{ a.date }} at {{ a.time }} &mdash;
                    <span :class="`badge ms-2 badge-status-${a.status.toLowerCase()}`">{{ a.status }}</span>
                  </button>
                </h2>
                <div :id="`collapse-${a.id}`" class="accordion-collapse collapse"
                     data-bs-parent="#historyAccordion">
                  <div class="accordion-body">
                    <p><strong>Reason:</strong> {{ a.reason || '—' }}</p>
                    <div v-if="a.treatment">
                      <p><strong>Diagnosis:</strong> {{ a.treatment.diagnosis || '—' }}</p>
                      <p><strong>Prescription:</strong> {{ a.treatment.prescription || '—' }}</p>
                      <p><strong>Notes:</strong> {{ a.treatment.notes || '—' }}</p>
                      <p v-if="a.treatment.next_visit"><strong>Next Visit:</strong> {{ a.treatment.next_visit }}</p>
                    </div>
                    <p v-else class="text-muted">No treatment record</p>
                  </div>
                </div>
              </div>
              <p v-if="!patientHistory.history?.length" class="text-muted text-center py-3">No appointment history</p>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { Modal } from 'bootstrap'
import { Chart, registerables } from 'chart.js'
import NavBar from '@/components/Navbar.vue'
import { useAuthStore } from '@/store/auth.js'
import api from '@/utils/api.js'

Chart.register(...registerables)

const authStore = useAuthStore()
const activeTab = ref('today')
const tabs = [
  { key: 'today', label: 'Today', icon: 'bi-calendar-day' },
  { key: 'appointments', label: 'All Appointments', icon: 'bi-calendar-check' },
  { key: 'patients', label: 'My Patients', icon: 'bi-people' },
  { key: 'availability', label: 'Availability', icon: 'bi-clock' },
  { key: 'profile', label: 'Profile', icon: 'bi-person-circle' },
  { key: 'stats', label: 'My Stats', icon: 'bi-bar-chart-line' },
]

const dashboard = ref({ today_appointments: [], week_appointments: [], stats: {} })
const doctorInfo = computed(() => dashboard.value.doctor)
const allAppointments = ref([])
const myPatients = ref([])
const apptFilter = ref('')
const savingAvail = ref(false)
const saving = ref(false)
const today = new Date().toISOString().split('T')[0]

const selectedAppt = ref(null)
const treatmentForm = reactive({ diagnosis: '', prescription: '', notes: '', next_visit: '' })
let treatmentModal = null

const patientHistory = ref(null)
let patientHistoryModal = null

const profileForm = reactive({ phone: '', qualification: '', bio: '' })

const availSlots = ref([])

function generateAvailSlots() {
  const slots = []
  for (let i = 0; i < 7; i++) {
    const d = new Date()
    d.setDate(d.getDate() + i)
    slots.push({
      date: d.toISOString().split('T')[0],
      is_available: d.getDay() !== 0,  // Not Sunday
      start_time: '09:00',
      end_time: '17:00',
      max_appointments: 10
    })
  }
  return slots
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })
}

async function loadDashboard() {
  const res = await api.get('/api/doctor/dashboard')
  dashboard.value = res.data
  if (res.data.doctor) {
    profileForm.phone = res.data.doctor.phone || ''
    profileForm.qualification = res.data.doctor.qualification || ''
    profileForm.bio = res.data.doctor.bio || ''
  }
}

async function loadAllAppointments() {
  const params = apptFilter.value ? { status: apptFilter.value } : {}
  const res = await api.get('/api/doctor/appointments', { params })
  allAppointments.value = res.data
}

async function loadMyPatients() {
  const res = await api.get('/api/doctor/patients')
  myPatients.value = res.data
}

async function loadAvailability() {
  try {
    const res = await api.get('/api/doctor/availability')
    if (res.data.length) {
      availSlots.value = generateAvailSlots().map(slot => {
        const existing = res.data.find(a => a.date === slot.date)
        return existing ? { ...slot, ...existing } : slot
      })
    } else {
      availSlots.value = generateAvailSlots()
    }
  } catch {
    availSlots.value = generateAvailSlots()
  }
}

async function saveAvailability() {
  savingAvail.value = true
  try {
    await api.post('/api/doctor/availability', { availability: availSlots.value })
    alert('Availability saved successfully!')
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to save')
  } finally {
    savingAvail.value = false
  }
}

async function updateStatus(appt, status) {
  if (!confirm(`Mark appointment as ${status}?`)) return
  await api.put(`/api/doctor/appointments/${appt.id}/status`, { status })
  await loadDashboard()
  await loadAllAppointments()
}

function openTreatmentModal(appt) {
  selectedAppt.value = appt
  const t = appt.treatment
  treatmentForm.diagnosis = t?.diagnosis || ''
  treatmentForm.prescription = t?.prescription || ''
  treatmentForm.notes = t?.notes || ''
  treatmentForm.next_visit = t?.next_visit || ''
  treatmentModal?.show()
}

async function saveTreatment() {
  saving.value = true
  try {
    await api.post(`/api/doctor/appointments/${selectedAppt.value.id}/treatment`, treatmentForm)
    treatmentModal?.hide()
    await loadDashboard()
    await loadAllAppointments()
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to save treatment')
  } finally {
    saving.value = false
  }
}

async function viewPatientHistory(p) {
  const res = await api.get(`/api/doctor/patients/${p.id}/history`)
  patientHistory.value = res.data
  patientHistoryModal?.show()
}

async function saveProfile() {
  try {
    await api.put('/api/doctor/profile', profileForm)
    alert('Profile updated!')
  } catch (e) {
    alert(e.response?.data?.error || 'Update failed')
  }
}

// Chart refs
const weekChartRef = ref(null)
const docStatusChartRef = ref(null)
let weekChart = null, docStatusChart = null

async function renderDocCharts() {
  await nextTick()
  const appts = allAppointments.value
  if (!appts.length) return

  // Weekly schedule - count by weekday
  const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
  const dayCounts = new Array(7).fill(0)
  appts.forEach(a => {
    if (a.date) {
      const d = new Date(a.date).getDay()
      const idx = d === 0 ? 6 : d - 1
      dayCounts[idx]++
    }
  })
  if (weekChart) weekChart.destroy()
  if (weekChartRef.value) {
    weekChart = new Chart(weekChartRef.value, {
      type: 'bar',
      data: {
        labels: days,
        datasets: [{
          label: 'Appointments',
          data: dayCounts,
          backgroundColor: ['#0d6efd','#198754','#dc3545','#ffc107','#0dcaf0','#6f42c1','#fd7e14'],
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } }, x: { grid: { display: false } } }
      }
    })
  }

  // Status breakdown
  const booked   = appts.filter(a => a.status === 'Booked').length
  const completed = appts.filter(a => a.status === 'Completed').length
  const cancelled = appts.filter(a => a.status === 'Cancelled').length
  if (docStatusChart) docStatusChart.destroy()
  if (docStatusChartRef.value) {
    docStatusChart = new Chart(docStatusChartRef.value, {
      type: 'doughnut',
      data: {
        labels: ['Booked','Completed','Cancelled'],
        datasets: [{ data: [booked, completed, cancelled],
          backgroundColor: ['#0d6efd','#198754','#dc3545'],
          borderWidth: 3, borderColor: '#fff', hoverOffset: 8 }]
      },
      options: { responsive: true, cutout: '65%',
        plugins: { legend: { position: 'bottom', labels: { padding: 10, usePointStyle: true } } }
      }
    })
  }
}

watch(activeTab, async (val) => {
  if (val === 'stats') renderDocCharts()
})

onMounted(async () => {
  await Promise.all([loadDashboard(), loadAllAppointments(), loadMyPatients(), loadAvailability()])
  treatmentModal = new Modal(document.getElementById('treatmentModal'))
  patientHistoryModal = new Modal(document.getElementById('patientHistoryModal'))
})
</script>
