// common.js - Shared functions across all pages

function updateFooterUserID() {
    const footerElement = document.getElementById('footer-userid');
    if (footerElement && typeof userManager !== 'undefined') {
        const uid = userManager.getUID();
        if (uid) {
            // Show first 6 chars for privacy, full ID on hover
            const displayUID = uid.length > 8 ?
                `${uid.substring(0, 6)}...` :
                uid;
            footerElement.textContent = displayUID;
            footerElement.title = `Full User ID: ${uid}`; // Tooltip with full ID
        } else {
            footerElement.textContent = 'not set';
        }
    }
}

function updateFooterBackendURL() {
    const footerElement = document.getElementById('footer-backend-url');
    if (footerElement && typeof SETTINGS !== 'undefined') {
        footerElement.textContent = SETTINGS.API_BASE_URL;
        footerElement.title = `Backend URL: ${SETTINGS.API_BASE_URL}`; // Tooltip with full URL
    }
}

// Initialize footer when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure UserManager is initialized
    setTimeout(updateFooterUserID, 50);
    setTimeout(updateFooterBackendURL, 50);
});

