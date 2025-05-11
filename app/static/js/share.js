// Image preview handler - shows selected image before upload
document.getElementById('shareImageUpload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('shareImagePreview').src = e.target.result;
            document.getElementById('shareImagePreview').style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

// Mock email share function - will connect to real email API later
function shareViaEmail() {
    const colleague = document.getElementById('colleagueSelect').value;
    if (colleague) {
        alert(`Sharing via Email to ${colleague} (Mock action)`);
    } else {
        alert('Please select a colleague.');
    }
}

// Google Docs integration - needs OAuth setup still
function shareToGoogleDocs() {
    alert('Sharing to Google Docs (Mock action)');
}

// For Slack/Teams - will add proper API calls in sprint 3
function shareViaInstantMessage() {
    alert('Sharing via Instant Message (Mock action)');
}