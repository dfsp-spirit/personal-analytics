// user-manager.js

// You must include settings.js before this script to define SETTINGS.
class UserManager {

    constructor(allow_no_uid = false) {
        // Use parameter if provided, otherwise use SETTINGS, otherwise use default
        this.allow_no_uid = allow_no_uid !== false ?
            allow_no_uid :
            (typeof SETTINGS !== 'undefined' && SETTINGS.ALLOW_NO_UID !== undefined ?
                SETTINGS.ALLOW_NO_UID :
                false);

        this.uid = null;
        this.init();
    }

    init() {
        // Try to get UID from URL first
        this.uid = this.getUIDFromURL();

        // If not in URL, try localStorage as fallback
        if (!this.uid) {
            this.uid = localStorage.getItem('pa_uid');
        }

        // If still no UID and allow_noid is true, use default
        if (!this.uid && this.allow_no_uid) {
            this.uid = 'default';
            console.log('UserManager: No UID found, using "default".');
        }

        // Update all links to include UID (if we have one)
        this.updateNavigationLinks();

        // Persist the UID (even if it's 'default')
        this.persistUID();

        console.log('UserManager initialized with UID:', this.uid, 'allow_no_uid:', this.allow_no_uid);
    }

    getUIDFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('uid');
    }

    updateNavigationLinks() {
        // Only update links if we have a UID
        if (!this.uid) return;

        document.querySelectorAll('a[href^="index.html"], a[href^="stats.html"], a[href^="."]').forEach(link => {
            if (this.uid && !link.href.includes('uid=')) {
                const url = new URL(link.href, window.location.origin);
                url.searchParams.set('uid', this.uid);
                link.href = url.toString();
            }
        });
    }

    getUID() {
        return this.uid;
    }

    isValid() {
        // If allow_noid is true, 'default' is considered valid
        if (this.allow_no_uid) {
            return this.uid && this.uid.length > 0;
        }
        // Strict mode: must have UID and it can't be 'default'
        return this.uid && this.uid.length > 0 && this.uid !== 'default';
    }

    isDefaultUser() {
        return this.uid === 'default';
    }

    enhanceFormData(formData) {
        if (this.uid) {
            formData.uid = this.uid;
        }
        return formData;
    }

    persistUID() {
        if (this.uid) {
            localStorage.setItem('pa_uid', this.uid);
        }
    }

    clear() {
        this.uid = null;
        localStorage.removeItem('pa_uid');
    }
}

// Create global instance for scripts to use
const userManager = new UserManager();
