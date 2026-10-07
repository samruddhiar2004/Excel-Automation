// State
let selectedFiles = [];
let currentSessionId = null;

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const fileListContainer = document.getElementById('file-list-container');
const fileChips = document.getElementById('file-chips');
const selectedFilesCount = document.getElementById('selected-files-count');
const btnClearFiles = document.getElementById('btn-clear-files');
const btnProcess = document.getElementById('btn-process');
const processingLoader = document.getElementById('processing-loader');

const uploadSection = document.getElementById('upload-section');
const resultsSection = document.getElementById('results-section');
const btnReset = document.getElementById('btn-reset');

// Stat Elements
const statFiles = document.getElementById('stat-files');
const statTotal = document.getElementById('stat-total');
const statValid = document.getElementById('stat-valid');
const statInvalid = document.getElementById('stat-invalid');
const statDuplicates = document.getElementById('stat-duplicates');
const processedTimestamp = document.getElementById('processed-timestamp');

// Download buttons
const btnDownloadMaster = document.getElementById('btn-download-master');
const btnDownloadErrors = document.getElementById('btn-download-errors');
const btnDownloadSummary = document.getElementById('btn-download-summary');

// Previews
const tbodyFileBreakdown = document.getElementById('tbody-file-breakdown');
const theadMaster = document.getElementById('thead-master');
const tbodyMaster = document.getElementById('tbody-master');
const tbodyErrors = document.getElementById('tbody-errors');
const masterPreviewCount = document.getElementById('master-preview-count');
const errorsPreviewCount = document.getElementById('errors-preview-count');
const summaryTextBlock = document.getElementById('summary-text-block');

// Config Modal
const btnConfig = document.getElementById('btn-config');
const configModal = document.getElementById('config-modal');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnCancelModal = document.getElementById('btn-cancel-modal');
const btnSaveConfig = document.getElementById('btn-save-config');
const configRequiredCols = document.getElementById('config-required-cols');
const configDuplicateKeys = document.getElementById('config-duplicate-keys');
const configOutputDir = document.getElementById('config-output-dir');

// ================= Drag & Drop Events =================
dropzone.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover'].forEach(eventName => {
  dropzone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(eventName => {
  dropzone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
  });
});

dropzone.addEventListener('drop', (e) => {
  const dt = e.dataTransfer;
  if (dt.files && dt.files.length > 0) {
    handleNewFiles(Array.from(dt.files));
  }
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files.length > 0) {
    handleNewFiles(Array.from(e.target.files));
  }
});

function handleNewFiles(files) {
  const xlsxFiles = files.filter(f => f.name.toLowerCase().endsWith('.xlsx') || f.name.toLowerCase().endsWith('.xls'));
  if (xlsxFiles.length === 0) {
    alert("Please select valid Excel files (.xlsx).");
    return;
  }
  
  // Append non-duplicate files
  xlsxFiles.forEach(file => {
    if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
      selectedFiles.push(file);
    }
  });

  renderFileList();
}

function renderFileList() {
  if (selectedFiles.length === 0) {
    fileListContainer.classList.add('hidden');
    return;
  }

  fileListContainer.classList.remove('hidden');
  selectedFilesCount.textContent = `${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''} selected`;
  fileChips.innerHTML = '';

  selectedFiles.forEach((file, idx) => {
    const chip = document.createElement('div');
    chip.className = 'file-chip';
    const sizeKb = (file.size / 1024).toFixed(1);
    chip.innerHTML = `
      <span>📄 ${file.name} (${sizeKb} KB)</span>
      <span class="remove-file" data-idx="${idx}">&times;</span>
    `;
    fileChips.appendChild(chip);
  });

  // Attach chip remove listeners
  fileChips.querySelectorAll('.remove-file').forEach(el => {
    el.addEventListener('click', (e) => {
      const idx = parseInt(e.target.getAttribute('data-idx'));
      selectedFiles.splice(idx, 1);
      renderFileList();
    });
  });
}

btnClearFiles.addEventListener('click', () => {
  selectedFiles = [];
  fileInput.value = '';
  renderFileList();
});

// ================= File Processing =================
btnProcess.addEventListener('click', async () => {
  if (selectedFiles.length === 0) return;

  const formData = new FormData();
  selectedFiles.forEach(file => {
    formData.append('files', file);
  });

  processingLoader.classList.remove('hidden');
  btnProcess.disabled = true;

  try {
    const res = await fetch('/api/process', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Processing failed');
    }

    const data = await res.json();
    displayResults(data);
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    processingLoader.classList.add('hidden');
    btnProcess.disabled = false;
  }
});

function displayResults(data) {
  currentSessionId = data.session_id;

  // Set KPI stats
  statFiles.textContent = data.files_processed.toLocaleString();
  statTotal.textContent = data.total_records.toLocaleString();
  statValid.textContent = data.valid_records.toLocaleString();
  statInvalid.textContent = data.invalid_records.toLocaleString();
  statDuplicates.textContent = data.duplicate_records.toLocaleString();
  processedTimestamp.textContent = `Processed at: ${data.processed_at}`;

  // Download links
  btnDownloadMaster.href = `/api/download/${data.session_id}/master`;
  btnDownloadErrors.href = `/api/download/${data.session_id}/errors`;
  btnDownloadSummary.href = `/api/download/${data.session_id}/summary`;

  // Render File Breakdown
  tbodyFileBreakdown.innerHTML = '';
  data.file_stats.forEach(stat => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${stat.file_name}</strong></td>
      <td>${stat.rows_detected}</td>
      <td style="color: var(--success); font-weight:600;">${stat.valid}</td>
      <td style="color: var(--error); font-weight:600;">${stat.invalid}</td>
      <td style="color: var(--warning); font-weight:600;">${stat.duplicates}</td>
      <td><span class="badge-error badge-error-${stat.status === 'Success' ? 'duplicate' : 'missing'}">${stat.status}</span></td>
    `;
    tbodyFileBreakdown.appendChild(tr);
  });

  // Render Master Preview
  theadMaster.innerHTML = '';
  tbodyMaster.innerHTML = '';
  if (data.master_preview && data.master_preview.length > 0) {
    const headers = Object.keys(data.master_preview[0]);
    const headerTr = document.createElement('tr');
    headers.forEach(h => {
      const th = document.createElement('th');
      th.textContent = h;
      headerTr.appendChild(th);
    });
    theadMaster.appendChild(headerTr);

    data.master_preview.forEach(row => {
      const tr = document.createElement('tr');
      headers.forEach(h => {
        const td = document.createElement('td');
        td.textContent = row[h] !== null && row[h] !== undefined ? row[h] : '';
        tr.appendChild(td);
      });
      tbodyMaster.appendChild(tr);
    });
    masterPreviewCount.textContent = `Previewing first ${data.master_preview.length} of ${data.valid_records.toLocaleString()} valid records`;
  } else {
    masterPreviewCount.textContent = `No valid records found in this run`;
  }

  // Render Error Preview
  tbodyErrors.innerHTML = '';
  if (data.errors_preview && data.errors_preview.length > 0) {
    data.errors_preview.forEach(err => {
      const tr = document.createElement('tr');
      let badgeClass = 'badge-error-invalid';
      if (err['Error Type'] === 'Missing Field') badgeClass = 'badge-error-missing';
      if (err['Error Type'] === 'Duplicate') badgeClass = 'badge-error-duplicate';
      if (err['Error Type'] === 'Structural Error') badgeClass = 'badge-error-structural';

      tr.innerHTML = `
        <td>${err['File']}</td>
        <td><strong>${err['Row']}</strong></td>
        <td><span class="badge-error ${badgeClass}">${err['Error Type']}</span></td>
        <td><code>${err['Field']}</code></td>
        <td>${err['Description']}</td>
        <td>${err['Raw Value']}</td>
      `;
      tbodyErrors.appendChild(tr);
    });
    errorsPreviewCount.textContent = `Previewing first ${data.errors_preview.length} of ${(data.invalid_records + data.duplicate_records).toLocaleString()} problem records`;
  } else {
    errorsPreviewCount.textContent = `Zero errors or duplicates detected!`;
  }

  // Render Summary Log
  summaryTextBlock.textContent = data.summary_text;

  // Toggle sections
  uploadSection.classList.add('hidden');
  resultsSection.classList.remove('hidden');
}

btnReset.addEventListener('click', () => {
  resultsSection.classList.add('hidden');
  uploadSection.classList.remove('hidden');
  selectedFiles = [];
  fileInput.value = '';
  renderFileList();
});

// ================= Tabs Switching =================
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    const targetId = btn.getAttribute('data-tab');
    document.getElementById(targetId).classList.add('active');
  });
});

// ================= Config Modal Logic =================
btnConfig.addEventListener('click', async () => {
  try {
    const res = await fetch('/api/config');
    const config = await res.json();
    configRequiredCols.value = (config.required_columns || []).join(', ');
    configDuplicateKeys.value = (config.duplicate_keys || []).join(', ');
    configOutputDir.value = config.output_dir || 'output';
    configModal.classList.remove('hidden');
  } catch (e) {
    alert('Failed to load active configuration.');
  }
});

function closeModal() {
  configModal.classList.add('hidden');
}

btnCloseModal.addEventListener('click', closeModal);
btnCancelModal.addEventListener('click', closeModal);

btnSaveConfig.addEventListener('click', async () => {
  const reqCols = configRequiredCols.value.split(',').map(s => s.trim()).filter(Boolean);
  const dupKeys = configDuplicateKeys.value.split(',').map(s => s.trim()).filter(Boolean);
  const outDir = configOutputDir.value.trim() || 'output';

  try {
    const getRes = await fetch('/api/config');
    const current = await getRes.json();
    current.required_columns = reqCols;
    current.duplicate_keys = dupKeys;
    current.output_dir = outDir;

    const res = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(current)
    });

    if (res.ok) {
      closeModal();
      alert('Configuration updated successfully!');
    } else {
      alert('Failed to update configuration.');
    }
  } catch (e) {
    alert(`Error saving config: ${e.message}`);
  }
});
