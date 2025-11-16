/**
 * HomeOS API Client Library
 * Handles all server communication with authentication and translation support
 */

class HomeOSAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.currentUser = null;
        this.language = localStorage.getItem('homeos_language') || 'ru';
        this.translations = {};
        this.tg = window.Telegram?.WebApp;
        
        // Initialize Telegram WebApp if available
        if (this.tg) {
            this.tg.ready();
            this.tg.expand();
            this.tg.enableClosingConfirmation();
        }
    }

    /**
     * Load translations for current language
     */
    async loadTranslations() {
        try {
            const response = await fetch(`${this.baseURL}/api/translations/${this.language}`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                this.translations = await response.json();
            }
        } catch (error) {
            console.error('Failed to load translations:', error);
        }
    }

    /**
     * Get translated text
     */
    t(key) {
        return this.translations[key] || key;
    }

    /**
     * Set language
     */
    async setLanguage(lang) {
        this.language = lang;
        localStorage.setItem('homeos_language', lang);
        await this.loadTranslations();
    }

    /**
     * Authenticate with Telegram
     */
    async authenticateWithTelegram() {
        if (!this.tg) {
            throw new Error('Telegram WebApp not available');
        }

        try {
            const initData = this.tg.initData;
            
            if (!initData) {
                throw new Error('No Telegram init data available');
            }

            const response = await fetch(`${this.baseURL}/api/auth/telegram`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ initData })
            });

            if (!response.ok) {
                throw new Error('Authentication failed');
            }

            const data = await response.json();
            
            if (data.success) {
                this.currentUser = data.user;
                return data.user;
            }

            throw new Error(data.error || 'Authentication failed');
        } catch (error) {
            console.error('Telegram auth error:', error);
            throw error;
        }
    }

    /**
     * Check authentication status
     */
    async checkAuth() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/check`, {
                credentials: 'include'
            });

            const data = await response.json();

            if (data.authenticated) {
                this.currentUser = data.user;
                return true;
            }

            return false;
        } catch (error) {
            console.error('Auth check error:', error);
            return false;
        }
    }

    /**
     * Logout
     */
    async logout() {
        try {
            await fetch(`${this.baseURL}/api/auth/logout`, {
                method: 'POST',
                credentials: 'include'
            });

            this.currentUser = null;
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    /**
     * Generic API request helper
     */
    async request(endpoint, options = {}) {
        const config = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);

            if (response.status === 401) {
                // Session expired, try to re-authenticate
                if (this.tg) {
                    await this.authenticateWithTelegram();
                    // Retry request
                    return await fetch(`${this.baseURL}${endpoint}`, config).then(r => r.json());
                }
                throw new Error('Authentication required');
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }

    // ==================== BANK API ====================

    async getBankAccount() {
        return await this.request('/api/bank/my-account');
    }

    async getBankUsers() {
        return await this.request('/api/bank/users');
    }

    async makeBankTransfer(to, amount, comment = '') {
        return await this.request('/api/bank/transfer', {
            method: 'POST',
            body: JSON.stringify({ to, amount, comment })
        });
    }

    async getBankHistory() {
        return await this.request('/api/bank/history');
    }

    // ==================== SHOP API ====================

    async getShopProducts() {
        return await this.request('/api/shop/products');
    }

    async getMyStore() {
        return await this.request('/api/shop/my-store');
    }

    async purchaseProducts(cart) {
        return await this.request('/api/shop/purchase', {
            method: 'POST',
            body: JSON.stringify({ cart })
        });
    }

    // ==================== MYWORK API ====================

    async startShift() {
        return await this.request('/api/mywork/start-shift', {
            method: 'POST'
        });
    }

    async stopShift(minutes, pay) {
        return await this.request('/api/mywork/stop-shift', {
            method: 'POST',
            body: JSON.stringify({ minutes, pay })
        });
    }

    async getShifts() {
        return await this.request('/api/mywork/shifts');
    }

    // ==================== MYINFO API ====================

    async getMyInfoRecords() {
        return await this.request('/api/myinfo/records');
    }

    async saveMyInfoRecords(records) {
        return await this.request('/api/myinfo/records', {
            method: 'POST',
            body: JSON.stringify(records)
        });
    }

    // ==================== UTILITY METHODS ====================

    /**
     * Show notification (uses Telegram or browser notification)
     */
    notify(message, type = 'info') {
        if (this.tg && this.tg.showAlert) {
            this.tg.showAlert(message);
        } else {
            // Fallback to console
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    /**
     * Haptic feedback (Telegram only)
     */
    haptic(style = 'medium') {
        if (this.tg && this.tg.HapticFeedback) {
            this.tg.HapticFeedback.impactOccurred(style);
        }
    }

    /**
     * Format number with locale
     */
    formatNumber(number) {
        return new Intl.NumberFormat(this.language === 'ru' ? 'ru-RU' : 'en-US').format(number);
    }

    /**
     * Format date with locale
     */
    formatDate(date) {
        return new Date(date).toLocaleString(this.language === 'ru' ? 'ru-RU' : 'en-US');
    }
}

// Global API instance
const api = new HomeOSAPI();

// Auto-initialize
(async function() {
    try {
        await api.loadTranslations();
        
        // Try to authenticate with Telegram
        if (api.tg && api.tg.initData) {
            try {
                await api.authenticateWithTelegram();
                console.log('✅ Authenticated with Telegram');
            } catch (error) {
                console.log('ℹ️ Telegram auth not available, will require manual login');
            }
        } else {
            // Check if session exists
            await api.checkAuth();
        }
    } catch (error) {
        console.error('API initialization error:', error);
    }
})();