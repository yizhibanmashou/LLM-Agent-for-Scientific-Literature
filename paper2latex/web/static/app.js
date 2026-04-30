// paper2latex Web Interface - JavaScript

let currentJobId = null;

// DOM Elements
const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');

const pdfInput = document.getElementById('pdf-input');
const uploadBtn = document.getElementById('upload-btn');
const convertBtn = document.getElementById('convert-btn');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');

const fileTree = document.getElementById('file-tree');
const fileContent = document.getElementById('file-content');
const currentFileSpan = document.getElementById('current-file');
const compileBtn = document.getElementById('compile-btn');
const pdfViewer = document.getElementById('pdf-viewer');

const downloadBtn = document.getElementById('download-btn');
const newConversionBtn = document.getElementById('new-conversion-btn');

// Upload button click
uploadBtn.addEventListener('click', () => {
    pdfInput.click();
});

// File selected
pdfInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.style.display = 'inline-flex';
        convertBtn.style.display = 'inline-block';
    }
});

// Convert button click
convertBtn.addEventListener('click', async () => {
    const file = pdfInput.files[0];
    if (!file) return;

    // Show progress
    uploadSection.style.display = 'none';
    progressSection.style.display = 'block';

    // Get selected engine and token
    const engine = document.querySelector('input[name="engine"]:checked').value;
    const token = document.getElementById('paddle-token').value;

    // Upload and convert
    const formData = new FormData();
    formData.append('file', file);
    formData.append('engine', engine);
    if (token) {
        formData.append('token', token);
    }

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Conversion failed');
        }

        const data = await response.json();
        currentJobId = data.job_id;

        // Load results
        await loadResults(data);

        // Show results
        progressSection.style.display = 'none';
        resultsSection.style.display = 'block';

    } catch (error) {
        alert('Error: ' + error.message);
        progressSection.style.display = 'none';
        uploadSection.style.display = 'block';
    }
});

// Load conversion results
async function loadResults(data) {
    // Update stats
    if (data.summary) {
        document.getElementById('stat-pages').textContent = data.summary.pages || '-';
        document.getElementById('stat-sections').textContent = data.summary.sections || '-';
        document.getElementById('stat-citations').textContent = data.summary.citations_in_text || '-';
        document.getElementById('stat-bib').textContent = data.summary.bib_entries || '-';
        document.getElementById('stat-formulas').textContent = data.summary.formulas_total || '-';
        document.getElementById('stat-figures').textContent = data.summary.figures_extracted || '-';
    }

    // Load original PDF in left panel
    const originalPdfUrl = `/api/job/${currentJobId}/file/original.pdf`;
    const leftPdfViewer = document.getElementById('original-pdf-viewer');
    leftPdfViewer.innerHTML = `<iframe src="${originalPdfUrl}" style="width: 100%; height: 100%; border: none;"></iframe>`;

    // Load file tree
    await loadFileTree();
}

// Load file tree
async function loadFileTree() {
    try {
        const response = await fetch(`/api/job/${currentJobId}/files`);
        const data = await response.json();

        fileTree.innerHTML = '';
        renderFileTree(data.files, fileTree);

    } catch (error) {
        console.error('Error loading file tree:', error);
    }
}

// Render file tree
function renderFileTree(files, container, level = 0) {
    files.forEach(file => {
        // Container for file item (and potential children)
        const wrapper = document.createElement('div');

        // The item line itself
        const item = document.createElement('div');
        item.className = 'file-item';
        item.style.paddingLeft = `${level * 15 + 10}px`;

        // Caret for directories
        const caret = document.createElement('i');
        if (file.type === 'directory' && file.children && file.children.length > 0) {
            caret.className = 'fas fa-caret-right caret';
        } else {
            caret.className = 'fas fa-caret-right caret';
            caret.style.visibility = 'hidden';
        }
        item.appendChild(caret);

        // Icon
        const icon = document.createElement('i');
        icon.className = file.type === 'directory' ? 'fas fa-folder folder-icon' : 'fas fa-file file-icon';
        item.appendChild(icon);

        // Name
        const name = document.createElement('span');
        name.textContent = file.name;
        item.appendChild(name);

        // Children container
        let childrenContainer = null;
        if (file.type === 'directory' && file.children) {
            childrenContainer = document.createElement('div');
            childrenContainer.className = 'nested';
            renderFileTree(file.children, childrenContainer, level + 1);
        }

        // Click handler
        item.addEventListener('click', (e) => {
            e.stopPropagation();

            if (file.type === 'directory') {
                // Toggle collapse
                if (childrenContainer) {
                    childrenContainer.classList.toggle('active-folder');
                    caret.classList.toggle('caret-down');
                    icon.className = childrenContainer.classList.contains('active-folder')
                        ? 'fas fa-folder-open folder-icon'
                        : 'fas fa-folder folder-icon';
                }
            } else {
                // Open file
                loadFile(file.path, file.name);
                // Highlight active
                document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
            }
        });

        wrapper.appendChild(item);
        if (childrenContainer) {
            wrapper.appendChild(childrenContainer);
        }

        container.appendChild(wrapper);

        // Auto-expand latex directory if at root
        if (level === 0 && file.name === 'latex' && childrenContainer) {
            childrenContainer.classList.add('active-folder');
            caret.classList.add('caret-down');
            icon.className = 'fas fa-folder-open folder-icon';
        }
    });
}

// Load file content
async function loadFile(path, name) {
    try {
        const fileExt = name.split('.').pop().toLowerCase();
        const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico'];

        // Handle images
        if (imageExts.includes(fileExt)) {
            currentFileSpan.textContent = name;
            const imageUrl = `/api/job/${currentJobId}/file/${path}`;
            fileContent.innerHTML = `
                <div class="image-preview" style="text-align: center; padding: 20px;">
                    <img src="${imageUrl}" style="max-width: 100%; max-height: 500px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
                    <p style="margin-top: 10px; color: #888;">${name}</p>
                </div>`;
            return;
        }

        // Handle PDF (in file viewer)
        if (fileExt === 'pdf') {
            currentFileSpan.textContent = name;
            const pdfUrl = `/api/job/${currentJobId}/file/${path}`;
            fileContent.innerHTML = `<iframe src="${pdfUrl}" style="width: 100%; height: 600px; border: none;"></iframe>`;
            return;
        }

        // Handle Text Files
        const response = await fetch(`/api/job/${currentJobId}/file/${path}`);

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        currentFileSpan.textContent = name;

        // Display content with simple highlighting
        fileContent.innerHTML = `<pre>${escapeHtml(data.content)}</pre>`;

    } catch (error) {
        console.error('Error loading file:', error);
        fileContent.innerHTML = `<div class="placeholder"><i class="fas fa-exclamation-circle"></i><p>Error loading file: ${error.message}</p></div>`;
    }
}

// Compile LaTeX
compileBtn.addEventListener('click', async () => {
    compileBtn.disabled = true;
    compileBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Compiling...';

    try {
        const response = await fetch(`/api/job/${currentJobId}/compile`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.status === 'success') {
            compileBtn.innerHTML = '<i class="fas fa-check"></i> Compiled!';

            // Refresh file tree to show new log files or PDF
            await loadFileTree();

            // Re-enable button after 2 seconds
            setTimeout(() => {
                compileBtn.innerHTML = '<i class="fas fa-play"></i> Compile';
                compileBtn.disabled = false;
            }, 2000);
        } else {
            alert('Compilation failed. Check log in file viewer.');
            console.error(data.log);

            // Show log in file viewer
            currentFileSpan.textContent = "Compilation Log";
            fileContent.innerHTML = `<pre style="color: #ff6b6b;">${escapeHtml(data.log)}</pre>`;

            compileBtn.innerHTML = '<i class="fas fa-times"></i> Failed';
            setTimeout(() => {
                compileBtn.innerHTML = '<i class="fas fa-play"></i> Compile';
                compileBtn.disabled = false;
            }, 2000);
        }

    } catch (error) {
        alert('Error: ' + error.message);
        compileBtn.innerHTML = '<i class="fas fa-play"></i> Compile';
        compileBtn.disabled = false;
    }
});

// Refresh File Tree
document.getElementById('refresh-btn').addEventListener('click', loadFileTree);

// Download LaTeX
downloadBtn.addEventListener('click', () => {
    window.location.href = `/api/job/${currentJobId}/download`;
});

// New conversion
newConversionBtn.addEventListener('click', () => {
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';

    // Reset form
    pdfInput.value = '';
    fileInfo.style.display = 'none';
    convertBtn.style.display = 'none';
    currentJobId = null;
});

// Helper functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Toggle token input based on engine selection
const engineRadios = document.getElementsByName('engine');
const paddleTokenSection = document.getElementById('paddle-token-section');

if (engineRadios && paddleTokenSection) {
    engineRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            paddleTokenSection.style.display = e.target.value === 'paddle' ? 'block' : 'none';
        });
    });
}
