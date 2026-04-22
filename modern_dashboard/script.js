// Modern Dashboard JavaScript - TIDAL Style
let vehicleData = [];
let statusChart = null;
let daysChart = null;
let dataTable = null;

// API Configuration
const API_BASE = window.location.origin;
const REFRESH_INTERVAL = 30000; // 30 seconds

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 STNK Modern Dashboard Initializing...');
    
    // Initialize DataTable
    initDataTable();
    
    // Load initial data
    fetchData();
    
    // Setup auto-refresh
    setInterval(fetchData, REFRESH_INTERVAL);
    
    // Setup update modal
    setupUpdateModal();
    
    // Setup theme toggle
    setupThemeToggle();
    
    console.log('✅ Dashboard initialized');
});

// Initialize DataTable
function initDataTable() {
    dataTable = $('#vehicleTable').DataTable({
        responsive: true,
        pageLength: 10,
        lengthMenu: [10, 25, 50, 100],
        order: [[0, 'asc']],
        language: {
            search: "Cari:",
            lengthMenu: "Tampilkan _MENU_ data",
            info: "Menampilkan _START_ sampai _END_ dari _TOTAL_ data",
            paginate: {
                first: "Pertama",
                last: "Terakhir",
                next: "Berikutnya",
                previous: "Sebelumnya"
            }
        },
        columnDefs: [
            { width: '50px', targets: 0 }, // No
            { width: '150px', targets: 2 }, // No Polisi
            { width: '100px', targets: 3 }, // Kategori
            { width: '120px', targets: 4 }, // STNK
            { width: '120px', targets: 5 }, // Pajak
            { width: '120px', targets: 6 }, // Status
            { width: '100px', targets: 7 }, // Hari Tersisa
            { responsivePriority: 1, targets: [0, 1, 2, 6, 7] }, // Priority columns for mobile
            { responsivePriority: 2, targets: [3, 4, 5] },
            { responsivePriority: 3, targets: [8, 9] } // Hide on mobile
        ]
    });
}

// Fetch data from API
async function fetchData() {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/data`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        vehicleData = data;
        
        updateDashboard(data);
        updateCharts(data);
        updateStats(data);
        updateLastUpdate();
        
        showLoading(false);
        
    } catch (error) {
        console.error('Error fetching data:', error);
        showError('Gagal memuat data. Silakan refresh halaman.');
        showLoading(false);
    }
}

// Update dashboard table
function updateDashboard(data) {
    const tableBody = document.getElementById('vehicleTableBody');
    tableBody.innerHTML = '';
    
    data.forEach((vehicle, index) => {
        const row = document.createElement('tr');
        row.className = getStatusRowClass(vehicle.status);
        
        // Format dates
        const stnkDate = formatDate(vehicle.stnk_date);
        const pajakDate = formatDate(vehicle.pajak_date);
        
        // Create status badge
        const statusBadge = createStatusBadge(vehicle.status, vehicle.days_to_expiry);
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${vehicle.merk}</strong></td>
            <td><span class="license-plate">${vehicle.no_polisi}</span></td>
            <td>${vehicle.kategori}</td>
            <td>${stnkDate}</td>
            <td>${pajakDate}</td>
            <td>${statusBadge}</td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="me-2">${vehicle.days_to_expiry}</span>
                    <div class="progress flex-grow-1" style="height: 6px;">
                        <div class="progress-bar ${getProgressBarClass(vehicle.status)}" 
                             style="width: ${getProgressWidth(vehicle.days_to_expiry)}%">
                        </div>
                    </div>
                </div>
            </td>
            <td>${vehicle.ktp || '-'}</td>
            <td>${vehicle.catatan || '-'}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Refresh DataTable
    if (dataTable) {
        dataTable.clear();
        dataTable.rows.add($('#vehicleTableBody tr'));
        dataTable.draw();
    }
}

// Update charts
function updateCharts(data) {
    updateStatusChart(data);
    updateDaysChart(data);
}

// Update status distribution chart
function updateStatusChart(data) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    // Count by status
    const counts = {
        safe: data.filter(v => v.status === 'safe').length,
        warning: data.filter(v => v.status === 'warning').length,
        priority: data.filter(v => v.status === 'priority').length
    };
    
    // Destroy existing chart
    if (statusChart) {
        statusChart.destroy();
    }
    
    // Create new chart
    statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Aman', 'Perhatian', 'Prioritas'],
            datasets: [{
                data: [counts.safe, counts.warning, counts.priority],
                backgroundColor: [
                    'rgba(67, 233, 123, 0.8)',
                    'rgba(250, 112, 154, 0.8)',
                    'rgba(255, 8, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(67, 233, 123, 1)',
                    'rgba(250, 112, 154, 1)',
                    'rgba(255, 8, 68, 1)'
                ],
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    borderColor: '#475569',
                    borderWidth: 1
                }
            },
            cutout: '70%',
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });
}

// Update days to expiry chart
function updateDaysChart(data) {
    const ctx = document.getElementById('daysChart').getContext('2d');
    
    // Sort by days to expiry (ascending)
    const sortedData = [...data].sort((a, b) => a.days_to_expiry - b.days_to_expiry);
    const labels = sortedData.map(v => v.no_polisi);
    const daysData = sortedData.map(v => v.days_to_expiry);
    const colors = sortedData.map(v => getStatusColor(v.status));
    
    // Destroy existing chart
    if (daysChart) {
        daysChart.destroy();
    }
    
    // Create new chart
    daysChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Hari Tersisa',
                data: daysData,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    borderColor: '#475569',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const vehicle = sortedData[context.dataIndex];
                            return [
                                `Hari tersisa: ${context.raw}`,
                                `Status: ${getStatusText(vehicle.status)}`,
                                `STNK: ${formatDate(vehicle.stnk_date)}`,
                                `Pajak: ${formatDate(vehicle.pajak_date)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#94a3b8',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    title: {
                        display: true,
                        text: 'Hari',
                        color: '#94a3b8'
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Update statistics
function updateStats(data) {
    const safeCount = data.filter(v => v.status === 'safe').length;
    const warningCount = data.filter(v => v.status === 'warning').length;
    const priorityCount = data.filter(v => v.status === 'priority').length;
    
    // Animate count up
    animateCount('safeCount', safeCount);
    animateCount('warningCount', warningCount);
    animateCount('priorityCount', priorityCount);
}

// Animate number counting
function animateCount(elementId, target) {
    const element = document.getElementById(elementId);
    const current = parseInt(element.textContent) || 0;
    const increment = target > current ? 1 : -1;
    let currentValue = current;
    
    const timer = setInterval(() => {
        currentValue += increment;
        element.textContent = currentValue;
        
        if (currentValue === target) {
            clearInterval(timer);
        }
    }, 30);
}

// Update last update time
function updateLastUpdate() {
    const now = new Date();
    const formatted = now.toLocaleString('id-ID', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Asia/Jakarta'
    });
    
    document.getElementById('lastUpdate').textContent = `Terakhir diperbarui: ${formatted}`;
}

// Setup update modal
function setupUpdateModal() {
    const modal = document.getElementById('updateModal');
    
    modal.addEventListener('show.bs.modal', function() {
        populateVehicleSelect();
    });
    
    // Handle vehicle selection change
    document.getElementById('vehicleSelect').addEventListener('change', function() {
        const vehicleId = this.value;
        if (vehicleId) {
            const vehicle = vehicleData.find(v => v.id == vehicleId);
            if (vehicle) {
                updateCurrentInfo(vehicle);
            }
        }
    });
}

// Populate vehicle select dropdown
function populateVehicleSelect() {
    const select = document.getElementById('vehicleSelect');
    select.innerHTML = '<option value="">Pilih kendaraan...</option>';
    
    vehicleData.forEach(vehicle => {
        const option = document.createElement('option');
        option.value = vehicle.id;
        option.textContent = `${vehicle.no_polisi} - ${vehicle.merk}`;
        select.appendChild(option);
    });
}

// Update current info in modal
function updateCurrentInfo(vehicle) {
    const infoDiv = document.getElementById('currentInfo');
    const stnkDate = formatDate(vehicle.stnk_date);
    const pajakDate = formatDate(vehicle.pajak_date);
    const statusBadge = createStatusBadge(vehicle.status, vehicle.days_to_expiry);
    
    infoDiv.innerHTML = `
        <div class="row">
            <div class="col-6">
                <small class="text-muted">No Polisi</small>
                <div><strong>${vehicle.no_polisi}</strong></div>
            </div>
            <div class="col-6">
                <small class="text-muted">Merk</small>
                <div>${vehicle.merk}</div>
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-6">
                <small class="text-muted">STNK Saat Ini</small>
                <div>${stnkDate}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Pajak Saat Ini</small>
                <div>${pajakDate}</div>
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-12">
                <small class="text-muted">Status</small>
                <div>${statusBadge} (${vehicle.days_to_expiry} hari tersisa)</div>
            </div>
        </div>
    `;
}

// Submit update form
async function submitUpdate() {
    const vehicleId = document.getElementById('vehicleSelect').value;
    const newStnkDate = document.getElementById('newStnkDate').value;
    const newPajakDate = document.getElementById('newPajakDate').value;
    const updateNote = document.getElementById('updateNote').value;
    
    // Validation
    if (!vehicleId || !newStnkDate || !newPajakDate) {
        alert('Harap lengkapi semua field yang wajib diisi!');
        return;
    }
    
    // Show loading
    const button = document.querySelector('#updateModal .btn-update');
    const buttonText = document.getElementById('updateButtonText');
    const spinner = document.getElementById('updateSpinner');
    
    button.disabled = true;
    buttonText.textContent = 'Memproses...';
    spinner.classList.remove('d-none');
    
    try {
        const response = await fetch(`${API_BASE}/api/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: parseInt(vehicleId),
                stnk_date: newStnkDate,
                pajak_date: newPajakDate,
                note: updateNote
            })
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error);
        }
        
        const result = await response.json();
        
        // Show success message
        showSuccessToast('Data berhasil diperbarui! Backup telah dibuat.');
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('updateModal')).hide();
        
        // Reset form
        document.getElementById('updateForm').reset();
        document.getElementById('currentInfo').innerHTML = '<small class="text-muted">Pilih kendaraan untuk melihat info</small>';
        
        // Refresh data
        setTimeout(fetchData, 1000);
        
    } catch (error) {
        console.error('Update error:', error);
        alert(`Gagal memperbarui data: ${error.message}`);
    } finally {
        // Reset button
        button.disabled = false;
        buttonText.textContent = 'Update Data';
        spinner.classList.add('d-none');
    }
}

// Setup theme toggle
function setupThemeToggle() {
    const themeToggle = document.createElement('button');
    themeToggle.className = 'btn btn-outline-secondary position-fixed bottom-3 end-3 rounded-circle';
    themeToggle.innerHTML = '<i class="bi bi-moon-stars"></i>';
    themeToggle.style.zIndex = '1000';
    themeToggle.style.width = '50px';
    themeToggle.style.height = '50px';
    themeToggle.title = 'Toggle theme';
    
    themeToggle.addEventListener('click', function() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-bs-theme', newTheme);
        this.innerHTML = newTheme === 'dark' ? '<i class="bi bi-moon-stars"></i>' : '<i class="bi bi-sun"></i>';
        
        // Save preference
        localStorage.setItem('dashboard-theme', newTheme);
    });
    
    document.body.appendChild(themeToggle);
    
    // Load saved theme
    const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    themeToggle.innerHTML = savedTheme === 'dark' ? '<i class="bi bi-moon-stars"></i>' : '<i class="bi bi-sun"></i>';
}

// Export data
function exportData() {
    // Create CSV content
    let csv = 'No,Merk,No Polisi,Kategori,STNK,Pajak,Status,Hari Tersisa,Pemilik,Catatan\n';
    
    vehicleData.forEach((vehicle, index) => {
        const row = [
            index + 1,
            `"${vehicle.merk}"`,
            vehicle.no_polisi,
            vehicle.kategori,
            formatDate(vehicle.stnk_date),
            formatDate(vehicle.pajak_date),
            getStatusText(vehicle.status),
            vehicle.days_to_expiry,
            `"${vehicle.ktp || ''}"`,
            `"${vehicle.catatan || ''}"`
        ];
        
        csv += row.join(',') + '\n';
    });
    
    // Create download link
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `stnk_data_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showSuccessToast('Data berhasil diexport ke CSV');
}

// Refresh data manually
function refreshData() {
    fetchData();
    showSuccessToast('Data diperbarui');
}

// Helper functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

function getStatusText(status) {
    const texts = {
        'safe': 'Aman',
        'warning': 'Perhatian',
        'priority': 'Prioritas'
    };
    return texts[status] || status;
}

function createStatusBadge(status, days) {
    const text = getStatusText(status);
    const icon = status === 'safe' ? 'bi-check-circle' : 
                 status === 'warning' ? 'bi-exclamation-triangle' : 
                 'bi-exclamation-octagon';
    
    return `<span class="badge-status ${status}">
                <i class="bi ${icon}"></i>
                ${text}
            </span>`;
}

function getStatusRowClass(status) {
    return `status-${status}`;
}

function getProgressBarClass(status) {
    const classes = {
        'safe': 'bg-success',
        'warning': 'bg-warning',
        'priority': 'bg-danger'
    };
    return classes[status] || '';
}

function getProgressWidth(days) {
    if (days >= 365) return 100;
    if (days <= 0) return 0;
    return Math.min(100, Math.max(0, (days / 365) * 100));
}

function getStatusColor(status) {
    const colors = {
        'safe': 'rgba(67, 233, 123, 0.8)',
        'warning': 'rgba(250, 112, 154, 0.8)',
        'priority': 'rgba(255, 8, 68, 0.8)'
    };
    return colors[status] || 'rgba(148, 163, 184, 0.8)';
}

function showLoading(show) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (!loadingOverlay && show) {
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        overlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
                <p class="mt-3 text-light">Memuat data...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    } else if (loadingOverlay && !show) {
        loadingOverlay.remove();
    }
}

function showError(message) {
    const errorToast = document.createElement('div');
    errorToast.className = 'toast align-items-center text-bg-danger border-0';
    errorToast.setAttribute('role', 'alert');
    errorToast.setAttribute('aria-live', 'assertive');
    errorToast.setAttribute('aria-atomic', 'true');
    
    errorToast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-exclamation-triangle me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.querySelector('.toast-container');
    container.appendChild(errorToast);
    
    const toast = new bootstrap.Toast(errorToast);
    toast.show();
    
    // Remove after hide
    errorToast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function showSuccessToast(message) {
    const toastBody = document.querySelector('#successToast .toast-body');
    toastBody.textContent = message;
    
    const toast = new bootstrap.Toast(document.getElementById('successToast'));
    toast.show();
}

// Add loading overlay styles
const style = document.createElement('style');
style.textContent = `
    .status-safe { border-left: 4px solid #43e97b; }
    .status-warning { border-left: 4px solid #fa709a; }
    .status-priority { border-left: 4px solid #ff0844; }
    
    .status-safe:hover { background: rgba(67, 233, 123, 0.05) !important; }
    .status-warning:hover { background: rgba(250, 112, 154, 0.05) !important; }
    .status-priority:hover { background: rgba(255, 8, 68, 0.05) !important; }
    
    /* Light theme adjustments */
    [data-bs-theme="light"] {
        --dark-bg: #f8fafc;
        --card-bg: #ffffff;
        --sidebar-bg: #f1f5f9;
    }
    
    [data-bs-theme="light"] body {
        color: #334155;
    }
    
    [data-bs-theme="light"] .sidebar {
        box-shadow: 5px 0 15px rgba(0, 0, 0, 0.1);
    }
    
    [data-bs-theme="light"] .nav-link {
        color: #64748b;
    }
    
    [data-bs-theme="light"] .nav-link:hover,
    [data-bs-theme="light"] .nav-link.active {
        background: rgba(102, 126, 234, 0.1);
        color: #4f46e5;
    }
    
    [data-bs-theme="light"] .stat-card,
    [data-bs-theme="light"] .charts-container,
    [data-bs-theme="light"] .table-container {
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    [data-bs-theme="light"] .form-control,
    [data-bs-theme="light"] .form-select {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        color: #334155;
    }
    
    [data-bs-theme="light"] .dataTables_wrapper .dataTables_length select,
    [data-bs-theme="light"] .dataTables_wrapper .dataTables_filter input {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        color: #334155;
    }
    
    [data-bs-theme="light"] .license-plate {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border: 2px solid #cbd5e1;
        color: #0f172a;
    }
`;
document.head.appendChild(style);