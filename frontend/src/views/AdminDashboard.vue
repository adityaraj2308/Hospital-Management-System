<template>
  <div>
    <NavBar @tabChange="activeTab = $event" />
    <div class="container-fluid py-4" data-testid="admin-dashboard">

      <!-- Stats Row -->
      <div class="row g-3 mb-4">
        <div class="col-md-3 col-6" v-for="stat in stats" :key="stat.label">
          <div :class="`card stat-card text-white ${stat.color}`" :data-testid="`stat-${stat.key}`">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <div class="stat-value">{{ stat.value }}</div>
                <div class="small opacity-75">{{ stat.label }}</div>
              </div>
              <i :class="`bi ${stat.icon} stat-icon`"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Tabs -->
      <div class="card">
        <div class="card-header bg-white border-0 pt-3">
          <ul class="nav nav-tabs border-0" data-testid="admin-tabs">
            <li class="nav-item" v-for="tab in tabs" :key="tab.key">
              <button :class="['nav-link', activeTab === tab.key ? 'active' : '']"
                      @click="activeTab = tab.key" :data-testid="`tab-${tab.key}`">
                <i :class="`bi ${tab.icon} me-1`"></i>{{ tab.label }}
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body">

          <!-- DOCTORS TAB -->
          <div v-if="activeTab === 'doctors'" data-testid="doctors-tab">
            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
              <h5 class="mb-0">Doctors Management</h5>
              <div class="d-flex gap-2 flex-wrap">
                <div class="input-group" style="width:260px">
                  <span class="input-group-text"><i class="bi bi-search"></i></span>
                  <input v-model="doctorFilter" type="text" class="form-control"
                         placeholder="Search by name or specialization..."
                         data-testid="doctor-filter-input" />
                </div>
                <button class="btn btn-primary btn-sm" @click="openDoctorModal()" data-testid="add-doctor-btn">
                  <i class="bi bi-plus-lg me-1"></i>Add Doctor
                </button>
              </div>
            </div>
            <div class="table-responsive">
              <table class="table table-hover align-middle" data-testid="doctors-table">
                <thead><tr>
                  <th>#</th><th>Name</th><th>Specialization</th><th>Department</th>
                  <th>Phone</th><th>Experience</th><th>Status</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  <tr v-for="doc in filteredDoctors" :key="doc.id" :data-testid="`doctor-row-${doc.id}`">
                    <td>{{ doc.id }}</td>
                    <td><strong>{{ doc.name }}</strong><br><small class="text-muted">@{{ doc.username }}</small></td>
                    <td>{{ doc.specialization }}</td>
                    <td>{{ doc.department || '—' }}</td>
                    <td>{{ doc.phone || '—' }}</td>
                    <td>{{ doc.experience_years }} yrs</td>
                    <td>
                      <span :class="`badge ${doc.is_active ? 'bg-success' : 'bg-danger'}`">
                        {{ doc.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary me-1" @click="openDoctorModal(doc)" :data-testid="`edit-doctor-${doc.id}`">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button :class="`btn btn-sm ${doc.is_active ? 'btn-outline-warning' : 'btn-outline-success'} me-1`"
                              @click="toggleDoctor(doc)" :data-testid="`toggle-doctor-${doc.id}`">
                        <i :class="`bi ${doc.is_active ? 'bi-ban' : 'bi-check2'}`"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!filteredDoctors.length"><td colspan="8" class="text-center text-muted py-4">No doctors found</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- PATIENTS TAB -->
          <div v-if="activeTab === 'patients'" data-testid="patients-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">Patients Management</h5>
              <div class="input-group" style="width:300px">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input v-model="patientSearch" type="text" class="form-control"
                       placeholder="Search by name, ID, phone..." data-testid="patient-search-input"
                       @input="searchPatients" />
              </div>
            </div>
            <div class="table-responsive">
              <table class="table table-hover align-middle" data-testid="patients-table">
                <thead><tr>
                  <th>#</th><th>Name</th><th>Age/Gender</th><th>Phone</th>
                  <th>Blood Group</th><th>Status</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  <tr v-for="p in patients" :key="p.id" :data-testid="`patient-row-${p.id}`">
                    <td>{{ p.id }}</td>
                    <td><strong>{{ p.name }}</strong><br><small class="text-muted">{{ p.email }}</small></td>
                    <td>{{ p.age || '—' }} / {{ p.gender || '—' }}</td>
                    <td>{{ p.phone || '—' }}</td>
                    <td><span class="badge bg-secondary">{{ p.blood_group || '—' }}</span></td>
                    <td><span :class="`badge ${p.is_active ? 'bg-success' : 'bg-danger'}`">{{ p.is_active ? 'Active' : 'Blacklisted' }}</span></td>
                    <td>
                      <button class="btn btn-sm btn-outline-info me-1" @click="viewPatient(p)" :data-testid="`view-patient-${p.id}`">
                        <i class="bi bi-eye"></i>
                      </button>
                      <button :class="`btn btn-sm ${p.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`"
                              @click="togglePatient(p)" :data-testid="`toggle-patient-${p.id}`">
                        <i :class="`bi ${p.is_active ? 'bi-ban' : 'bi-check2'}`"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!patients.length"><td colspan="7" class="text-center text-muted py-4">No patients found</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- APPOINTMENTS TAB -->
          <div v-if="activeTab === 'appointments'" data-testid="appointments-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">All Appointments</h5>
              <select v-model="apptFilter" class="form-select" style="width:180px" data-testid="appt-filter" @change="loadAppointments">
                <option value="">All Status</option>
                <option value="Booked">Booked</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
            <div class="table-responsive">
              <table class="table table-hover align-middle" data-testid="appointments-table">
                <thead><tr>
                  <th>#</th><th>Patient</th><th>Doctor</th><th>Date & Time</th>
                  <th>Status</th><th>Reason</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  <tr v-for="a in appointments" :key="a.id" :data-testid="`appt-row-${a.id}`">
                    <td>{{ a.id }}</td>
                    <td>{{ a.patient_name }}</td>
                    <td>{{ a.doctor_name }}<br><small class="text-muted">{{ a.doctor_specialization }}</small></td>
                    <td>{{ a.date }}<br><small class="text-muted">{{ a.time }}</small></td>
                    <td><span :class="`badge badge-status-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
                    <td>{{ a.reason || '—' }}</td>
                    <td>
                      <button v-if="a.status === 'Booked'" class="btn btn-sm btn-outline-danger"
                              @click="cancelAppointment(a)" :data-testid="`cancel-appt-${a.id}`">
                        <i class="bi bi-x-circle"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!appointments.length"><td colspan="7" class="text-center text-muted py-4">No appointments found</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- DEPARTMENTS TAB -->
          <div v-if="activeTab === 'departments'" data-testid="departments-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="mb-0">Departments / Specializations</h5>
              <button class="btn btn-primary btn-sm" @click="openDeptModal()" data-testid="add-dept-btn">
                <i class="bi bi-plus-lg me-1"></i>Add Department
              </button>
            </div>
            <div class="row g-3">
              <div class="col-md-4" v-for="dept in departments" :key="dept.id" :data-testid="`dept-card-${dept.id}`">
                <div class="card h-100">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 class="fw-bold">{{ dept.name }}</h6>
                        <p class="text-muted small mb-1">{{ dept.description || 'No description' }}</p>
                        <span class="badge bg-primary">{{ dept.doctors_count }} doctors</span>
                      </div>
                      <button class="btn btn-sm btn-outline-secondary" @click="openDeptModal(dept)" :data-testid="`edit-dept-${dept.id}`">
                        <i class="bi bi-pencil"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12 text-center text-muted py-4" v-if="!departments.length">No departments yet</div>
            </div>
          </div>

          <!-- SEARCH TAB -->
          <div v-if="activeTab === 'search'" data-testid="search-tab">
            <div class="row g-3 mb-3">
              <div class="col-md-8">
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-search"></i></span>
                  <input v-model="searchQuery" type="text" class="form-control form-control-lg"
                         placeholder="Search doctors, patients..." data-testid="global-search-input" />
                  <select v-model="searchType" class="form-select" style="max-width:150px">
                    <option value="all">All</option>
                    <option value="doctor">Doctors</option>
                    <option value="patient">Patients</option>
                  </select>
                  <button class="btn btn-primary" @click="doSearch" data-testid="search-btn">Search</button>
                </div>
              </div>
            </div>
            <div v-if="searchResults.doctors?.length" class="mb-4">
              <h6>Doctors ({{ searchResults.doctors.length }})</h6>
              <div class="table-responsive">
                <table class="table table-sm">
                  <thead><tr><th>Name</th><th>Specialization</th><th>Department</th><th>Status</th></tr></thead>
                  <tbody>
                    <tr v-for="d in searchResults.doctors" :key="d.id">
                      <td>{{ d.name }}</td><td>{{ d.specialization }}</td>
                      <td>{{ d.department || '—' }}</td>
                      <td><span :class="`badge ${d.is_active ? 'bg-success' : 'bg-danger'}`">{{ d.is_active ? 'Active' : 'Inactive' }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-if="searchResults.patients?.length">
              <h6>Patients ({{ searchResults.patients.length }})</h6>
              <div class="table-responsive">
                <table class="table table-sm">
                  <thead><tr><th>#</th><th>Name</th><th>Phone</th><th>Email</th><th>Status</th></tr></thead>
                  <tbody>
                    <tr v-for="p in searchResults.patients" :key="p.id">
                      <td>{{ p.id }}</td><td>{{ p.name }}</td><td>{{ p.phone }}</td>
                      <td>{{ p.email }}</td>
                      <td><span :class="`badge ${p.is_active ? 'bg-success' : 'bg-danger'}`">{{ p.is_active ? 'Active' : 'Blacklisted' }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-if="searchDone && !searchResults.doctors?.length && !searchResults.patients?.length" class="text-center text-muted py-4">
              No results found
            </div>
          </div>

          <!-- ANALYTICS TAB -->
          <div v-if="activeTab === 'analytics'" data-testid="analytics-tab">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="mb-0"><i class="bi bi-bar-chart-line me-2 text-primary"></i>Hospital Analytics</h5>
              <button class="btn btn-sm btn-outline-primary" @click="renderCharts" data-testid="refresh-charts-btn">
                <i class="bi bi-arrow-clockwise me-1"></i>Refresh
              </button>
            </div>

            <!-- KPI Strip -->
            <div class="row g-3 mb-4">
              <div class="col-6 col-md-3">
                <div class="p-3 rounded-3 text-center" style="background:linear-gradient(135deg,#0d6efd,#0056b3);color:white">
                  <div class="fs-3 fw-bold">{{ dashboardStats.total_appointments || 0 }}</div>
                  <div class="small opacity-75">Total Appointments</div>
                </div>
              </div>
              <div class="col-6 col-md-3">
                <div class="p-3 rounded-3 text-center" style="background:linear-gradient(135deg,#198754,#0d6640);color:white">
                  <div class="fs-3 fw-bold">{{ dashboardStats.completed || 0 }}</div>
                  <div class="small opacity-75">Completed</div>
                </div>
              </div>
              <div class="col-6 col-md-3">
                <div class="p-3 rounded-3 text-center" style="background:linear-gradient(135deg,#dc3545,#a71d2a);color:white">
                  <div class="fs-3 fw-bold">{{ dashboardStats.cancelled || 0 }}</div>
                  <div class="small opacity-75">Cancelled</div>
                </div>
              </div>
              <div class="col-6 col-md-3">
                <div class="p-3 rounded-3 text-center" style="background:linear-gradient(135deg,#ffc107,#d39e00);color:white">
                  <div class="fs-3 fw-bold">{{ dashboardStats.booked || 0 }}</div>
                  <div class="small opacity-75">Upcoming (Booked)</div>
                </div>
              </div>
            </div>

            <!-- Charts Row 1 -->
            <div class="row g-4 mb-4">
              <!-- Monthly Trends -->
              <div class="col-lg-8">
                <div class="card h-100">
                  <div class="card-header bg-white fw-semibold">
                    <i class="bi bi-graph-up me-2 text-primary"></i>Monthly Appointment Trends
                  </div>
                  <div class="card-body">
                    <div v-if="!chartDataReady" class="d-flex align-items-center justify-content-center" style="height:260px">
                      <div class="text-center text-muted">
                        <div class="spinner-border spinner-border-sm mb-2"></div>
                        <p class="small mb-0">Loading chart data...</p>
                      </div>
                    </div>
                    <canvas v-else ref="appointmentChartRef" height="260" data-testid="appointment-chart"></canvas>
                  </div>
                </div>
              </div>

              <!-- Status Breakdown -->
              <div class="col-lg-4">
                <div class="card h-100">
                  <div class="card-header bg-white fw-semibold">
                    <i class="bi bi-pie-chart me-2 text-success"></i>Appointment Status
                  </div>
                  <div class="card-body d-flex align-items-center justify-content-center">
                    <div v-if="!chartDataReady" class="text-muted text-center">
                      <div class="spinner-border spinner-border-sm"></div>
                    </div>
                    <canvas v-else ref="statusChartRef" data-testid="status-chart"></canvas>
                  </div>
                </div>
              </div>
            </div>

            <!-- Charts Row 2 -->
            <div class="row g-4">
              <!-- Specialization Demand -->
              <div class="col-lg-5">
                <div class="card h-100">
                  <div class="card-header bg-white fw-semibold">
                    <i class="bi bi-building me-2 text-info"></i>Department / Specialization Demand
                  </div>
                  <div class="card-body d-flex align-items-center justify-content-center">
                    <div v-if="!chartDataReady" class="text-muted text-center">
                      <div class="spinner-border spinner-border-sm"></div>
                    </div>
                    <canvas v-else ref="specChartRef" data-testid="spec-chart"></canvas>
                  </div>
                </div>
              </div>

              <!-- Doctor Activity Table -->
              <div class="col-lg-7">
                <div class="card h-100">
                  <div class="card-header bg-white fw-semibold">
                    <i class="bi bi-person-badge me-2 text-warning"></i>Doctor Activity
                  </div>
                  <div class="card-body">
                    <canvas ref="doctorBarChartRef" height="220" data-testid="doctor-chart"></canvas>
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>

    <!-- Doctor Modal -->
    <div class="modal fade" id="doctorModal" tabindex="-1" data-testid="doctor-modal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingDoctor?.id ? 'Edit Doctor' : 'Add New Doctor' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="doctorFormError" class="alert alert-danger py-2 small">{{ doctorFormError }}</div>
            <form @submit.prevent="saveDoctor" id="doctorForm">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Full Name *</label>
                  <input v-model="doctorForm.name" type="text" class="form-control" required data-testid="doctor-name-input" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Specialization *</label>
                  <input v-model="doctorForm.specialization" type="text" class="form-control" required data-testid="doctor-spec-input" />
                </div>
                <template v-if="!editingDoctor?.id">
                  <div class="col-md-6">
                    <label class="form-label">Username *</label>
                    <input v-model="doctorForm.username" type="text" class="form-control" required data-testid="doctor-username-input" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Password *</label>
                    <input v-model="doctorForm.password" type="password" class="form-control" required data-testid="doctor-password-input" />
                  </div>
                </template>
                <div class="col-md-6">
                  <label class="form-label">Email</label>
                  <input v-model="doctorForm.email" type="email" class="form-control" data-testid="doctor-email-input" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Department</label>
                  <select v-model="doctorForm.department_id" class="form-select" data-testid="doctor-dept-select">
                    <option value="">Select Department</option>
                    <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone</label>
                  <input v-model="doctorForm.phone" type="text" class="form-control" data-testid="doctor-phone-input" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Experience (years)</label>
                  <input v-model.number="doctorForm.experience_years" type="number" class="form-control" min="0" data-testid="doctor-exp-input" />
                </div>
                <div class="col-md-12">
                  <label class="form-label">Qualification</label>
                  <input v-model="doctorForm.qualification" type="text" class="form-control" data-testid="doctor-qual-input" />
                </div>
                <div class="col-md-12">
                  <label class="form-label">Bio</label>
                  <textarea v-model="doctorForm.bio" class="form-control" rows="2" data-testid="doctor-bio-input"></textarea>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" form="doctorForm" class="btn btn-primary" :disabled="saving" data-testid="save-doctor-btn">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ saving ? 'Saving...' : 'Save Doctor' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Department Modal -->
    <div class="modal fade" id="deptModal" tabindex="-1" data-testid="dept-modal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingDept?.id ? 'Edit Department' : 'Add Department' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDept" id="deptForm">
              <div class="mb-3">
                <label class="form-label">Department Name *</label>
                <input v-model="deptForm.name" type="text" class="form-control" required data-testid="dept-name-input" />
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="deptForm.description" class="form-control" rows="3" data-testid="dept-desc-input"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" form="deptForm" class="btn btn-primary" :disabled="saving" data-testid="save-dept-btn">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient View Modal -->
    <div class="modal fade" id="patientModal" tabindex="-1" data-testid="patient-view-modal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedPatient">
            <div class="row g-3">
              <div class="col-md-4">
                <div class="text-center p-3 bg-light rounded">
                  <div class="avatar-circle bg-primary text-white mx-auto mb-2" style="width:60px;height:60px;font-size:1.5rem">
                    {{ selectedPatient.name?.charAt(0) }}
                  </div>
                  <h6>{{ selectedPatient.name }}</h6>
                  <p class="text-muted small mb-1">{{ selectedPatient.email }}</p>
                  <span :class="`badge ${selectedPatient.is_active ? 'bg-success' : 'bg-danger'}`">{{ selectedPatient.is_active ? 'Active' : 'Blacklisted' }}</span>
                </div>
              </div>
              <div class="col-md-8">
                <table class="table table-sm">
                  <tr><th>Age</th><td>{{ selectedPatient.age || '—' }}</td></tr>
                  <tr><th>Gender</th><td>{{ selectedPatient.gender || '—' }}</td></tr>
                  <tr><th>Phone</th><td>{{ selectedPatient.phone || '—' }}</td></tr>
                  <tr><th>Blood Group</th><td>{{ selectedPatient.blood_group || '—' }}</td></tr>
                  <tr><th>Address</th><td>{{ selectedPatient.address || '—' }}</td></tr>
                  <tr><th>Emergency Contact</th><td>{{ selectedPatient.emergency_contact || '—' }}</td></tr>
                </table>
              </div>
            </div>
            <h6 class="mt-3">Appointment History</h6>
            <div class="table-responsive" style="max-height:200px;overflow-y:auto">
              <table class="table table-sm">
                <thead><tr><th>Date</th><th>Doctor</th><th>Status</th><th>Diagnosis</th></tr></thead>
                <tbody>
                  <tr v-for="a in selectedPatient.appointments" :key="a.id">
                    <td>{{ a.date }}</td>
                    <td>{{ a.doctor_name }}</td>
                    <td><span :class="`badge badge-status-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
                    <td>{{ a.treatment?.diagnosis?.substring(0,40) || '—' }}</td>
                  </tr>
                  <tr v-if="!selectedPatient.appointments?.length">
                    <td colspan="4" class="text-center text-muted">No appointments</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, computed } from 'vue'
import { Modal } from 'bootstrap'
import { Chart, registerables } from 'chart.js'
import NavBar from '@/components/Navbar.vue'
import api from '@/utils/api.js'

Chart.register(...registerables)

const activeTab = ref('doctors')
const tabs = [
  { key: 'doctors', label: 'Doctors', icon: 'bi-person-badge' },
  { key: 'patients', label: 'Patients', icon: 'bi-people' },
  { key: 'appointments', label: 'Appointments', icon: 'bi-calendar-check' },
  { key: 'departments', label: 'Departments', icon: 'bi-building' },
  { key: 'search', label: 'Search', icon: 'bi-search' },
  { key: 'analytics', label: 'Analytics', icon: 'bi-bar-chart-line' },
]

const dashboardStats = ref({})
const doctors = ref([])
const patients = ref([])
const appointments = ref([])
const departments = ref([])
const apptFilter = ref('')
const patientSearch = ref('')
const doctorFilter = ref('')
const searchQuery = ref('')
const searchType = ref('all')
const searchResults = ref({})
const searchDone = ref(false)

const filteredDoctors = computed(() => {
  const q = doctorFilter.value.toLowerCase().trim()
  if (!q) return doctors.value
  return doctors.value.filter(d =>
    d.name.toLowerCase().includes(q) || (d.specialization || '').toLowerCase().includes(q)
  )
})

const stats = ref([])

// Doctor form
const editingDoctor = ref(null)
const doctorForm = reactive({ name:'', specialization:'', username:'', email:'', password:'', department_id:'', phone:'', experience_years:0, qualification:'', bio:'' })
const doctorFormError = ref('')
const saving = ref(false)
let doctorModal = null

// Dept form
const editingDept = ref(null)
const deptForm = reactive({ name:'', description:'' })
let deptModal = null

// Patient view
const selectedPatient = ref(null)
let patientModal = null

async function loadDashboard() {
  const res = await api.get('/api/admin/dashboard')
  dashboardStats.value = res.data
  stats.value = [
    { key:'doctors', label:'Total Doctors', value: res.data.total_doctors, color:'bg-primary', icon:'bi-person-badge' },
    { key:'patients', label:'Total Patients', value: res.data.total_patients, color:'bg-success', icon:'bi-people' },
    { key:'appointments', label:'Total Appointments', value: res.data.total_appointments, color:'bg-info text-white', icon:'bi-calendar-check' },
    { key:'today', label:"Today's Appointments", value: res.data.today_appointments, color:'bg-warning text-dark', icon:'bi-clock' },
  ]
}

async function loadDoctors() {
  const res = await api.get('/api/admin/doctors')
  doctors.value = res.data
}

async function loadPatients() {
  const res = await api.get('/api/admin/patients')
  patients.value = res.data
}

async function loadAppointments() {
  const params = apptFilter.value ? { status: apptFilter.value } : {}
  const res = await api.get('/api/admin/appointments', { params })
  appointments.value = res.data
}

async function loadDepartments() {
  const res = await api.get('/api/admin/departments')
  departments.value = res.data
}

async function searchPatients() {
  if (patientSearch.value.length < 2) {
    await loadPatients(); return
  }
  const res = await api.get('/api/admin/search', { params: { q: patientSearch.value, type: 'patient' } })
  patients.value = res.data.patients || []
}

async function doSearch() {
  if (!searchQuery.value.trim()) return
  const res = await api.get('/api/admin/search', { params: { q: searchQuery.value, type: searchType.value } })
  searchResults.value = res.data
  searchDone.value = true
}

async function toggleDoctor(doc) {
  if (!confirm(`${doc.is_active ? 'Deactivate' : 'Activate'} Dr. ${doc.name}?`)) return
  await api.put(`/api/admin/doctors/${doc.id}/toggle`)
  await loadDoctors()
}

async function togglePatient(p) {
  if (!confirm(`${p.is_active ? 'Blacklist' : 'Activate'} patient ${p.name}?`)) return
  await api.put(`/api/admin/patients/${p.id}/toggle`)
  await loadPatients()
}

async function cancelAppointment(a) {
  if (!confirm('Cancel this appointment?')) return
  await api.put(`/api/admin/appointments/${a.id}`, { status: 'Cancelled' })
  await loadAppointments()
}

function openDoctorModal(doc = null) {
  editingDoctor.value = doc
  doctorFormError.value = ''
  if (doc) {
    Object.assign(doctorForm, { name: doc.name, specialization: doc.specialization, email: doc.email || '', department_id: doc.department_id || '', phone: doc.phone || '', experience_years: doc.experience_years || 0, qualification: doc.qualification || '', bio: doc.bio || '', username: '', password: '' })
  } else {
    Object.assign(doctorForm, { name:'', specialization:'', username:'', email:'', password:'', department_id:'', phone:'', experience_years:0, qualification:'', bio:'' })
  }
  doctorModal?.show()
}

async function saveDoctor() {
  saving.value = true
  doctorFormError.value = ''

  // JS validation
  if (!doctorForm.name.trim()) { doctorFormError.value = 'Full name is required.'; saving.value = false; return }
  if (!doctorForm.specialization.trim()) { doctorFormError.value = 'Specialization is required.'; saving.value = false; return }
  if (!editingDoctor.value?.id) {
    if (!doctorForm.username.trim()) { doctorFormError.value = 'Username is required.'; saving.value = false; return }
    if (doctorForm.password.length < 6) { doctorFormError.value = 'Password must be at least 6 characters.'; saving.value = false; return }
    if (!doctorForm.email.trim()) { doctorFormError.value = 'Email is required.'; saving.value = false; return }
  }

  try {
    if (editingDoctor.value?.id) {
      await api.put(`/api/admin/doctors/${editingDoctor.value.id}`, doctorForm)
    } else {
      await api.post('/api/admin/doctors', doctorForm)
    }
    doctorModal?.hide()
    await loadDoctors()
    await loadDashboard()
  } catch (e) {
    doctorFormError.value = e.response?.data?.error || 'Save failed'
  } finally {
    saving.value = false
  }
}

function openDeptModal(dept = null) {
  editingDept.value = dept
  if (dept) {
    deptForm.name = dept.name
    deptForm.description = dept.description || ''
  } else {
    deptForm.name = ''
    deptForm.description = ''
  }
  deptModal?.show()
}

async function saveDept() {
  saving.value = true
  try {
    if (editingDept.value?.id) {
      await api.put(`/api/admin/departments/${editingDept.value.id}`, deptForm)
    } else {
      await api.post('/api/admin/departments', deptForm)
    }
    deptModal?.hide()
    await loadDepartments()
  } catch (e) {
    alert(e.response?.data?.error || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function viewPatient(p) {
  const res = await api.get(`/api/admin/patients/${p.id}`)
  selectedPatient.value = res.data
  patientModal?.show()
}

// Chart refs + instances
const appointmentChartRef = ref(null)
const statusChartRef = ref(null)
const specChartRef = ref(null)
const doctorBarChartRef = ref(null)
const chartDataReady = ref(false)
let apptChart = null, statChart = null, specChart = null, docChart = null

const CHART_COLORS = ['#0d6efd','#198754','#dc3545','#ffc107','#0dcaf0','#6f42c1','#fd7e14','#20c997','#e83e8c','#6610f2']

async function renderCharts() {
  chartDataReady.value = false
  try {
    const [statsRes] = await Promise.all([api.get('/api/admin/stats')])
    const { department_stats, monthly_appointments, doctor_activity } = statsRes.data
    chartDataReady.value = true
    await nextTick()

    // 1. Monthly Appointment Trends — Bar chart
    if (apptChart) apptChart.destroy()
    if (appointmentChartRef.value) {
      const labels = monthly_appointments.length
        ? monthly_appointments.map(m => m.month)
        : ['No data yet']
      const data = monthly_appointments.length
        ? monthly_appointments.map(m => m.count)
        : [0]
      apptChart = new Chart(appointmentChartRef.value, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Appointments',
            data,
            backgroundColor: labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length] + 'cc'),
            borderColor: labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
            borderWidth: 2,
            borderRadius: 8,
            borderSkipped: false,
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} appointments` } }
          },
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f0f0f0' } },
            x: { grid: { display: false } }
          }
        }
      })
    }

    // 2. Appointment Status Doughnut
    if (statChart) statChart.destroy()
    if (statusChartRef.value) {
      const booked = dashboardStats.value.booked || 0
      const completed = dashboardStats.value.completed || 0
      const cancelled = dashboardStats.value.cancelled || 0
      statChart = new Chart(statusChartRef.value, {
        type: 'doughnut',
        data: {
          labels: ['Booked', 'Completed', 'Cancelled'],
          datasets: [{
            data: [booked, completed, cancelled],
            backgroundColor: ['#0d6efd', '#198754', '#dc3545'],
            borderWidth: 3,
            borderColor: '#fff',
            hoverOffset: 8
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true } },
            tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } }
          },
          cutout: '65%'
        }
      })
    }

    // 3. Specialization / Department Demand Doughnut
    if (specChart) specChart.destroy()
    if (specChartRef.value) {
      const deptLabels = department_stats.length ? department_stats.map(d => d.name) : ['No departments']
      const deptData  = department_stats.length ? department_stats.map(d => d.count) : [1]
      specChart = new Chart(specChartRef.value, {
        type: 'doughnut',
        data: {
          labels: deptLabels,
          datasets: [{
            data: deptData,
            backgroundColor: CHART_COLORS.slice(0, deptLabels.length),
            borderWidth: 3,
            borderColor: '#fff',
            hoverOffset: 10
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom', labels: { padding: 10, usePointStyle: true, font: { size: 11 } } }
          },
          cutout: '55%'
        }
      })
    }

    // 4. Doctor Activity horizontal bar — real data
    if (docChart) docChart.destroy()
    if (doctorBarChartRef.value) {
      const docNames = doctor_activity.length ? doctor_activity.map(d => d.name) : ['No doctors']
      const docData  = doctor_activity.length ? doctor_activity.map(d => d.count) : [0]
      docChart = new Chart(doctorBarChartRef.value, {
        type: 'bar',
        data: {
          labels: docNames,
          datasets: [{
            label: 'Total Appointments',
            data: docData,
            backgroundColor: CHART_COLORS.slice(0, docNames.length).map(c => c + 'bb'),
            borderColor: CHART_COLORS.slice(0, docNames.length),
            borderWidth: 2,
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f0f0f0' } },
            y: { grid: { display: false } }
          }
        }
      })
    }
  } catch (e) {
    console.error('Chart load error:', e)
  }
}

// Re-render charts when switching to analytics tab
watch(activeTab, async (val) => {
  if (val === 'analytics') {
    await nextTick()
    renderCharts()
  }
})



onMounted(async () => {
  await Promise.all([loadDashboard(), loadDoctors(), loadPatients(), loadAppointments(), loadDepartments()])
  doctorModal = new Modal(document.getElementById('doctorModal'))
  deptModal = new Modal(document.getElementById('deptModal'))
  patientModal = new Modal(document.getElementById('patientModal'))
})
</script>
