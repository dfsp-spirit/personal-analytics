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


// common.js - Backend error banner with custom messages

function showErrorBanner(message = 'Backend connection failed') {
    // Remove existing banner if any
    const existingBanner = document.getElementById('backend-error-banner');
    if (existingBanner) {
        existingBanner.remove();
    }

    const banner = document.createElement('div');
    banner.id = 'backend-error-banner';
    banner.innerHTML = `
        <div class="backend-error-banner">
            ⚠️ ${message}
            <button class="banner-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // Insert at the top of the body
    document.body.insertBefore(banner, document.body.firstChild);

    // Auto-remove after 8 seconds
    setTimeout(() => {
        if (banner.parentElement) {
            banner.remove();
        }
    }, 8000);
}

// CSS for the banner (add to styles.css)
const backendErrorCSS = `
.backend-error-banner {
    background: #fff3cd;
    color: #856404;
    padding: 12px 40px 12px 20px;
    border: 1px solid #ffeaa7;
    border-radius: 4px;
    margin: 10px;
    text-align: center;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: relative;
}

.banner-close {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #856404;
    padding: 0 5px;
}

.banner-close:hover {
    color: #000;
}
`;

// Add CSS to page
if (!document.querySelector('#backend-error-styles')) {
    const styleSheet = document.createElement("style");
    styleSheet.id = 'backend-error-styles';
    styleSheet.textContent = backendErrorCSS;
    document.head.appendChild(styleSheet);
}

