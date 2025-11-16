/**
 * HomeOS API Helper - Telegram CloudStorage Integration
 * Простая обертка для работы с Telegram CloudStorage вместо localStorage
 */

class TelegramStorage {
    constructor() {
        this.tg = window.Telegram?.WebApp;
        this.cloudStorage = this.tg?.CloudStorage;
        this.fallbackToLocal = !this.cloudStorage;
        
        if (this.fallbackToLocal) {
            console.warn('Telegram CloudStorage недоступен, используется localStorage');
        } else {
            console.log('✅ Telegram CloudStorage подключен');
        }
    }

    /**
     * Получить данные по ключу
     * @param {string} key - ключ данных
     * @param {*} defaultValue - значение по умолчанию
     * @returns {Promise<*>} данные
     */
    async get(key, defaultValue = null) {
        if (this.fallbackToLocal) {
            try {
                const value = localStorage.getItem(key);
                return value ? JSON.parse(value) : defaultValue;
            } catch (e) {
                return defaultValue;
            }
        }

        return new Promise((resolve) => {
            this.cloudStorage.getItem(key, (err, value) => {
                if (err || !value) {
                    resolve(defaultValue);
                } else {
                    try {
                        resolve(JSON.parse(value));
                    } catch (e) {
                        resolve(defaultValue);
                    }
                }
            });
        });
    }

    /**
     * Сохранить данные
     * @param {string} key - ключ данных
     * @param {*} value - данные для сохранения
     * @returns {Promise<boolean>} успех операции
     */
    async set(key, value) {
        const jsonValue = JSON.stringify(value);
        
        // Проверка размера (Telegram ограничение: 4096 байт)
        if (jsonValue.length > 4096) {
            console.warn(`Данные слишком большие для ключа "${key}": ${jsonValue.length} байт (макс 4096)`);
            // Можно разбить на части, но для простоты пока оставим как есть
        }

        if (this.fallbackToLocal) {
            try {
                localStorage.setItem(key, jsonValue);
                return true;
            } catch (e) {
                console.error('Ошибка сохранения в localStorage:', e);
                return false;
            }
        }

        return new Promise((resolve) => {
            this.cloudStorage.setItem(key, jsonValue, (err, success) => {
                if (err) {
                    console.error('Ошибка сохранения в CloudStorage:', err);
                    resolve(false);
                } else {
                    resolve(success);
                }
            });
        });
    }

    /**
     * Получить несколько ключей одновременно
     * @param {string[]} keys - массив ключей
     * @returns {Promise<Object>} объект с данными
     */
    async getMultiple(keys) {
        if (this.fallbackToLocal) {
            const result = {};
            for (const key of keys) {
                result[key] = await this.get(key, null);
            }
            return result;
        }

        return new Promise((resolve) => {
            this.cloudStorage.getItems(keys, (err, values) => {
                if (err) {
                    console.error('Ошибка получения данных:', err);
                    resolve({});
                } else {
                    const result = {};
                    for (const key of keys) {
                        try {
                            result[key] = values[key] ? JSON.parse(values[key]) : null;
                        } catch (e) {
                            result[key] = null;
                        }
                    }
                    resolve(result);
                }
            });
        });
    }

    /**
     * Удалить ключ
     * @param {string} key - ключ для удаления
     * @returns {Promise<boolean>}
     */
    async remove(key) {
        if (this.fallbackToLocal) {
            localStorage.removeItem(key);
            return true;
        }

        return new Promise((resolve) => {
            this.cloudStorage.removeItem(key, (err, success) => {
                resolve(!err && success);
            });
        });
    }

    /**
     * Получить все ключи
     * @returns {Promise<string[]>}
     */
    async keys() {
        if (this.fallbackToLocal) {
            return Object.keys(localStorage);
        }

        return new Promise((resolve) => {
            this.cloudStorage.getKeys((err, keys) => {
                resolve(err ? [] : keys);
            });
        });
    }
}

// Экспорт для использования
const storage = new TelegramStorage();

// Пример использования:
/*

// Сохранить пользователей
await storage.set('bank_users_v11', users);

// Получить пользователей
const users = await storage.get('bank_users_v11', []);

// Получить несколько ключей сразу
const data = await storage.getMultiple(['bank_users_v11', 'bank_history_v11']);
console.log(data.bank_users_v11);
console.log(data.bank_history_v11);

// Удалить данные
await storage.remove('old_key');

// Получить все ключи
const allKeys = await storage.keys();

*/