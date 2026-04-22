// Dashboard STNK Monitoring - Main JavaScript
let vehiclesData = [];
let statusChart = null;
let daysChart = null;
let dataTable = null;

// Format tanggal untuk tampilan
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Hitung hari menuju jatuh tempo
function calculateDaysToExpiry(expiryDate) {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// Tentukan status berdasarkan hari
function getStatus(days) {
    if (days <= 30) return 'priority';
    if (days <= 90) return 'warning';
    return 'safe';
}

// Tentukan warna status
function getStatusColor(status) {
    switch(status) {
        case 'safe': return 'success';
        case 'warning': return 'warning';
        case 'priority': return 'danger';
        default: return 'secondary';
    }
}

// Tentukan teks status
function getStatusText(status) {
    switch(status) {
        case 'safe': return 'AMAN';
        case 'warning': return 'PERINGATAN';
        case 'priority': return 'PRIORITAS';
        default: return 'TIDAK DIKETAHUI';
    }
}

// Ambil data dari API
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        if (data.success) {
            vehiclesData = data.vehicles;
            updateDashboard(vehiclesData);
            updateLastUpdate(data.timestamp);
        } else {
            console.error('Error fetching data:', data.error);
            showError('Gagal memuat data: ' + data.error);
        }
    } catch (error) {
        console.error('Fetch error:', error);
        showError('Gagal terhubung ke server. Pastikan server berjalan.');
    }
}

// Update dashboard dengan data baru
function updateDashboard(data) {
    // Hitung statistik
    const stats = {
        safe: data.filter(v => v.status === 'safe').length,
        warning: data.filter(v => v.status === 'warning').length,
        priority: data.filter(v => v.status === 'priority').length,
        total: data.length
    };

    // Update summary cards
    document.getElementById('safeCount').textContent = stats.safe;
    document.getElementById('warningCount').textContent = stats.warning;
    document.getElementById('priorityCount').textContent = stats.priority;
    document.getElementById('totalCount').textContent = stats.total;

    // Update tabel
    updateTable(data);

    // Update chart
    updateCharts(stats, data);

    // Update modal dropdown
    updateVehicleSelect(data);
}

// Update tabel DataTables
function updateTable(data) {
    const tableBody = document.getElementById('vehicleTableBody');
    tableBody.innerHTML = '';

    data.forEach(vehicle => {
        const row = document.createElement('tr');
        
        // Tentukan class baris berdasarkan status
        let rowClass = '';
        switch(vehicle.status) {
            case 'priority': rowClass = 'table-danger'; break;
            case 'warning': rowClass = 'table-warning'; break;
            case 'safe': rowClass = 'table-success'; break;
        }
        row.className = rowClass;

        // Format hari dengan warna
        let daysHtml = '';
        if (vehicle.hari_menuju_jatuh_tempo <= 0) {
            daysHtml = `<span class="badge bg-danger">TELAH JATUH TEMPO</span>`;
        } else if (vehicle.hari_menuju_jatuh_tempo <= 30) {
            daysHtml = `<span class="text-danger fw-bold">${vehicle.hari_menuju_jatuh_tempo} hari</span>`;
        } else if (vehicle.hari_menuju_jatuh_tempo <= 90) {
            daysHtml = `<span class="text-warning fw-bold">${vehicle.hari_menuju_jatuh_tempo} hari</span>`;
        } else {
            daysHtml = `<span class="text-success">${vehicle.hari_menuju_jatuh_tempo} hari</span>`;
        }

        row.innerHTML = `
            <td>${vehicle.id}</td>
            <td><strong>${vehicle.merk}</strong></td>
            <td><code>${vehicle.no_polisi}</code></td>
            <td>${vehicle.kategori}</td>
            <td>${formatDate(vehicle.stnk_date)}</td>
            <td>${formatDate(vehicle.pajak_date)}</td>
            <td>${daysHtml}</td>
            <td>
                <span class="status-badge status-${vehicle.status}">
                    ${getStatusText(vehicle.status)}
                </span>
            </td>
            <td>${vehicle.ktp}</td>
            <td>${vehicle.catatan || '-'}</td>
        `;

        tableBody.appendChild(row);
    });

    // Inisialisasi atau refresh DataTables
    if (dataTable) {
        dataTable.destroy();
    }
    
    dataTable = $('#vehicleTable').DataTable({
        pageLength: 10,
        lengthMenu: [5, 10, 25, 50],
        order: [[6, 'asc']], // Urutkan berdasarkan hari menuju jatuh tempo
        columnDefs: [
            { width: '50px', targets: 0 }, // No
            { width: '150px', targets: 2 }, // No Polisi - diperlebar
            { width: '100px', targets: 3 }, // Kategori
            { width: '120px', targets: 4 }, // Tanggal STNK
            { width: '120px', targets: 5 }, // Tanggal Pajak
            { width: '150px', targets: 6 }, // Hari Menuju Jatuh Tempo
            { width: '120px', targets: 7 }, // Status
            { width: '150px', targets: 8 }, // Pemilik
            { width: '200px', targets: 9 }, // Catatan
            { 
                responsivePriority: 1, 
                targets: [0, 1, 2, 3, 6, 7] // Kolom penting untuk mobile
            },
            { 
                responsivePriority: 2, 
                targets: [4, 5] // Kolom tanggal
            },
            { 
                responsivePriority: 3, 
                targets: [8, 9] // Kolom kurang penting (Pemilik, Catatan)
            }
        ],
        responsive: true,
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
        }
    });
}

// Update charts
function updateCharts(stats, data) {
    // Status Distribution Chart (Pie)
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    
    if (statusChart) {
        statusChart.destroy();
    }
    
    statusChart = new Chart(statusCtx, {
        type: 'pie',
        data: {
            labels: ['AMAN', 'PERINGATAN', 'PRIORITAS'],
            datasets: [{
                data: [stats.safe, stats.warning, stats.priority],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                borderColor: [
                    'rgb(40, 167, 69)',
                    'rgb(255, 193, 7)',
                    'rgb(220, 53, 69)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    // Days to Expiry Chart (Bar)
    const daysCtx = document.getElementById('daysChart').getContext('2d');
    const vehicleNames = data.map(v => v.merk.substring(0, 15) + (v.merk.length > 15 ? '...' : ''));
    const daysData = data.map(v => v.hari_menuju_jatuh_tempo);
    const backgroundColors = data.map(v => {
        switch(v.status) {
            case 'safe': return 'rgba(40, 167, 69, 0.7)';
            case 'warning': return 'rgba(255, 193, 7, 0.7)';
            case 'priority': return 'rgba(220, 53, 69, 0.7)';
            default: return 'rgba(108, 117, 125, 0.7)';
        }
    });

    if (daysChart) {
        daysChart.destroy();
    }

    daysChart = new Chart(daysCtx, {
        type: 'bar',
        data: {
            labels: vehicleNames,
            datasets: [{
                label: 'Hari Menuju Jatuh Tempo',
                data: daysData,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hari'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + ' hari';
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} hari`;
                        }
                    }
                }
            }
        }
    });
}

// Update dropdown di modal
function updateVehicleSelect(data) {
    const select = document.getElementById('vehicleSelect');
    select.innerHTML = '<option value="">Pilih kendaraan...</option>';
    
    data.forEach(vehicle => {
        const option = document.createElement('option');
        option.value = vehicle.id;
        option.textContent = `${vehicle.merk} (${vehicle.no_polisi}) - ${getStatusText(vehicle.status)}`;
        select.appendChild(option);
    });
}

// Update timestamp terakhir
function updateLastUpdate(timestamp) {
    const date = new Date(timestamp);
    const formatted = date.toLocaleString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('lastUpdate').textContent = formatted;
}

// Submit update form
async function submitUpdate() {
    const vehicleId = document.getElementById('vehicleSelect').value;
    const newStnkDate = document.getElementById('newStnkDate').value;
    const newPajakDate = document.getElementById('newPajakDate').value;
    const updateNote = document.getElementById('updateNote').value;

    if (!vehicleId || !newStnkDate || !newPajakDate) {
        showError('Harap isi semua field yang wajib diisi.');
        return;
    }

    try {
        const response = await fetch('/api/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                vehicleId: parseInt(vehicleId),
                newStnkDate,
                newPajakDate,
                note: updateNote
            })
        });

        const result = await response.json();
        
        if (result.success) {
            showSuccess('Data berhasil diupdate!');
            // Tutup modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('updateModal'));
            modal.hide();
            // Reset form
            document.getElementById('updateForm').reset();
            // Refresh data
            setTimeout(fetchData, 1000);
        } else {
            showError('Gagal update data: ' + result.error);
        }
    } catch (error) {
        console.error('Update error:', error);
        showError('Gagal mengirim update ke server.');
    }
}

// Export ke Excel (simulasi)
function exportToExcel() {
    showInfo('Fitur export Excel akan segera tersedia...');
    // Implementasi export Excel bisa ditambahkan nanti
}

// Refresh data
function refreshData() {
    fetchData();
    showInfo('Memperbarui data...');
}

// Notifikasi
function showError(message) {
    showNotification(message, 'danger');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showInfo(message) {
    showNotification(message, 'info');
}

function showNotification(message, type) {
    // Buat elemen notifikasi
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-hide setelah 5 detik
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Set tahun di footer
document.getElementById('currentYear').textContent = new Date().getFullYear();

// Inisialisasi saat halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    // Load data pertama kali
    fetchData();
    
    // Auto-refresh setiap 60 detik
    setInterval(fetchData, 60000);
    
    // Set tanggal default di modal ke hari ini
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('newStnkDate').value = today;
    document.getElementById('newPajakDate').value = today;
    
    // Event listener untuk modal show
    const updateModal = document.getElementById('updateModal');
    updateModal.addEventListener('show.bs.modal', function() {
        // Pre-fill dengan tanggal 1 tahun dari sekarang
        const nextYear = new Date();
        nextYear.setFullYear(nextYear.getFullYear() + 1);
        const nextYearStr = nextYear.toISOString().split('T')[0];
        
        document.getElementById('newStnkDate').value = nextYearStr;
        document.getElementById('newPajakDate').value = nextYearStr;
    });
});

// ============================================
// FUNGSI TAMBAH KENDARAAN BARU
// ============================================

function submitAddVehicle() {
    const merk = document.getElementById('addMerk').value.trim();
    const noPolisi = document.getElementById('addNoPolisi').value.trim();
    const kategori = document.getElementById('addKategori').value;
    const pemilik = document.getElementById('addPemilik').value.trim();
    const stnkDate = document.getElementById('addStnkDate').value;
    const pajakDate = document.getElementById('addPajakDate').value;
    const catatan = document.getElementById('addCatatan').value.trim();

    // Validasi
    if (!merk || !noPolisi || !kategori || !stnkDate || !pajakDate) {
        alert('Harap isi semua field yang wajib diisi (*)');
        return;
    }

    // Konfirmasi
    if (!confirm(`Tambahkan kendaraan baru?\nMerk: ${merk}\nNo Polisi: ${noPolisi}`)) {
        return;
    }

    // Hitung hari menuju jatuh tempo
    const today = new Date();
    const pajakDateObj = new Date(pajakDate);
    const daysToExpiry = Math.ceil((pajakDateObj - today) / (1000 * 60 * 60 * 24));
    
    // Tentukan status
    let status = 'AMAN';
    let statusColor = 'success';
    if (daysToExpiry <= 30) {
        status = 'PERINGATAN';
        statusColor = 'warning';
    }
    if (daysToExpiry <= 15) {
        status = 'PRIORITAS';
        statusColor = 'danger';
    }
    if (daysToExpiry < 0) {
        status = 'TERLAMBAT';
        statusColor = 'dark';
    }

    // Format tanggal untuk display
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        return date.toLocaleDateString('id-ID', options);
    };

    // Buat object kendaraan baru
    const newVehicle = {
        id: Date.now(), // ID unik berdasarkan timestamp
        merk: merk,
        no_polisi: noPolisi,
        kategori: kategori,
        pemilik: pemilik || '-',
        tanggal_stnk: stnkDate,
        tanggal_pajak: pajakDate,
        catatan: catatan || '-',
        hari_menuju_jatuh_tempo: daysToExpiry,
        status: status,
        status_color: statusColor,
        display_stnk: formatDate(stnkDate),
        display_pajak: formatDate(pajakDate)
    };

    // Kirim data ke server
    fetch('/api/add-vehicle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(newVehicle)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reset form
            document.getElementById('addVehicleForm').reset();
            
            // Tutup modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addVehicleModal'));
            modal.hide();
            
            // Tampilkan notifikasi sukses
            showNotification('success', 'Kendaraan berhasil ditambahkan!');
            
            // Refresh data table
            setTimeout(() => {
                if (typeof loadData === 'function') {
                    loadData();
                }
                if (typeof updateCharts === 'function') {
                    updateCharts();
                }
            }, 500);
        } else {
            alert('Gagal menambahkan kendaraan: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Terjadi kesalahan saat menambahkan kendaraan');
    });
}

// ============================================
// FUNGSI HAPUS KENDARAAN
// ============================================

function deleteVehicle(vehicleId, plate, merk) {
    if (!confirm(`Hapus kendaraan ini?\nMerk: ${merk}\nNo Polisi: ${plate}\n\nData akan dihapus permanen!`)) {
        return;
    }
    
    fetch(`/api/delete-vehicle/${vehicleId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('success', 'Kendaraan berhasil dihapus!');
            
            // Refresh data table
            setTimeout(() => {
                if (typeof loadData === 'function') {
                    loadData();
                }
                if (typeof updateCharts === 'function') {
                    updateCharts();
                }
            }, 500);
        } else {
            alert('Gagal menghapus kendaraan: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Terjadi kesalahan saat menghapus kendaraan');
    });
}

// Fungsi untuk menampilkan notifikasi
function showNotification(type, message) {
    // Buat elemen notifikasi
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <strong>${type === 'success' ? '✓' : '⚠'}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Tambahkan ke body
    document.body.appendChild(notification);
    
    // Auto-hide setelah 3 detik
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Reset form ketika modal ditutup
document.addEventListener('DOMContentLoaded', function() {
    const addVehicleModal = document.getElementById('addVehicleModal');
    if (addVehicleModal) {
        addVehicleModal.addEventListener('hidden.bs.modal', function() {
            document.getElementById('addVehicleForm').reset();
        });
    }
    
    // Event delegation untuk button hapus
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-btn')) {
            const button = e.target.closest('.delete-btn');
            const vehicleId = button.getAttribute('data-id');
            const plate = button.getAttribute('data-plate');
            const merk = button.getAttribute('data-merk');
            
            deleteVehicle(vehicleId, plate, merk);
        }
    });
});
