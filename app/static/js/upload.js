// Word count and character count
const newsContent = document.getElementById('newsContent');
const wordCount = document.getElementById('wordCount');

newsContent.addEventListener('input', function() {
    const text = this.value.trim();
    const words = text.split(/\s+/).filter(word => word.length > 0).length;
    const characters = text.length;
    wordCount.textContent = `${words} words, ${characters} characters`;
});

document.getElementById('clearBtn').addEventListener('click', function() {
    newsContent.value = '';
    wordCount.textContent = '0 words, 0 characters';
});

document.getElementById('analyzeBtn').addEventListener('click', function(event) {
    const form = document.getElementById('uploadForm');
    if (!form.checkValidity()) {
        event.preventDefault();
        form.classList.add('was-validated');
        return;
    }
    const formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData,
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        const status = document.getElementById('uploadStatus');
        if (data.success) {
            status.classList.remove('alert-danger');
            status.classList.add('alert-success');
            status.textContent = data.message;
            status.style.display = 'block';
            loadUploadHistory();
        } else {
            status.classList.remove('alert-success');
            status.classList.add('alert-danger');
            status.textContent = data.error;
            status.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('uploadStatus').textContent = 'An unexpected error occurred.';
    });
});

document.getElementById('uploadFileBtn').addEventListener('click', function(event) {
    const form = document.getElementById('fileUploadForm');
    if (!form.checkValidity()) {
        event.preventDefault();
        form.classList.add('was-validated');
        return;
    }
    const formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData,
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        const status = document.getElementById('uploadStatus');
        if (data.success) {
            status.classList.remove('alert-danger');
            status.classList.add('alert-success');
            status.textContent = data.message;
            status.style.display = 'block';
            loadUploadHistory();
        } else {
            status.classList.remove('alert-success');
            status.classList.add('alert-danger');
            status.textContent = data.error;
            status.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('uploadStatus').textContent = 'An unexpected error occurred.';
    });
});

function loadUploadHistory() {
    fetch('/upload/list', {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        const history = document.getElementById('uploadHistory');
        history.innerHTML = '';
        if (data.success) {
            data.uploads.forEach(upload => {
                const item = document.createElement('a');
                item.classList.add('list-group-item', 'list-group-item-action');
                item.href = '#';
                item.textContent = `${upload.filename} - ${upload.created_at} (Preview: ${upload.preview})`;
                history.appendChild(item);
            });
        } else {
            history.innerHTML = '<p class="text-danger">Failed to load history.</p>';
        }
        document.getElementById('loadingHistory').style.display = 'none';
    })
    .catch(error => console.error('Error:', error));
}

window.addEventListener('load', loadUploadHistory);