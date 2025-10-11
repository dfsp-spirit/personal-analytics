// form-config.js
// Configuration object for dynamic form generation

const API_BASE_URL = 'http://localhost:8000';

const FORM_CONFIG = {
    mood: {
        type: 'slider',
        label: 'Overall mood today?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very negative', '10 - Very positive'],
        required: true,
        default: 5,
        parse: (value) => parseInt(value)
    },
    pain: {
        type: 'slider',
        label: 'Pain Level (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - No pain', '10 - Worst imaginable'],
        required: true,
        default: 0,
        parse: (value) => parseInt(value)
    },
    anxiety: {
        type: 'slider',
        label: 'Anxiety level today?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - None', '10 - Extreme'],
        required: true,
        default: 0,
        parse: (value) => parseInt(value)
    },
    energy: {
        type: 'slider',
        label: 'Energy level today?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Exhausted', '10 - Very energetic'],
        required: true,
        default: 5,
        parse: (value) => parseInt(value)
    },
    allergy_state: {
        type: 'radio',
        label: 'Allergic Symptoms',
        options: {
            'none': 'None.',
            'other': 'Yes. At body parts other than face.',
            'face': 'Yes. On the face.'
        },
        encoding: { 'none': 0, 'other': 1, 'face': 2 },
        required: true,
        default: 'none',
        parse: (value) => FORM_CONFIG.allergy_state.encoding[value]
    },
    allergy_medication: {
        type: 'select',
        label: 'Anti-Allergic Drug Taken',
        options: {
            0: '0 - None',
            1: '1 - Half pill',
            2: '2 - One pill',
            3: '3 - 1.5 pills',
            4: '4 - Two pills'
        },
        required: true,
        default: 0,
        parse: (value) => parseInt(value)
    },
    had_sex: {
        type: 'radio',
        label: 'Had Sex in the Last 24 Hours',
        options: {
            0: 'No',
            1: 'Yes, with self',
            2: 'Yes, with partner'
        },
        encoding: { 0: 0, 1: 1, 2: 2 },
        required: true,
        default: 0,
        parse: (value) => parseInt(value)
    },
    sleep_quality: {
        type: 'slider',
        label: 'Sleep Quality (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very poor', '10 - Excellent'],
        required: true,
        default: 5,
        parse: (value) => parseInt(value)
    },
    stress_level_work: {
        type: 'slider',
        label: 'Work Stress Level (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - No stress', '10 - Extreme stress'],
        required: true,
        default: 0,
        parse: (value) => parseInt(value)
    },
    stress_level_home: {
        type: 'slider',
        label: 'Home Stress Level (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - No stress', '10 - Extreme stress'],
        required: true,
        default: 0,
        parse: (value) => parseInt(value)
    },
    social_support: {
        type: 'slider',
        label: 'Quality of social interactions?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very poor', '10 - Excellent'],
        required: true,
        default: 5,
        parse: (value) => parseInt(value)
    },
    physical_activity: {
        type: 'select',
        label: 'Physical activity level?',
        options: {
            '0': 'Almost None (e.g., Home office + minimal movement)', '1': 'Light (e.g., cycle to work)', '2': 'Moderate (e.g., work out, sports club)', '3': 'Vigorous (e.g., very long run, competitive sports)'
        },
        required: true,
        default: '0',
        parse: (value) => parseInt(value)
    },
    weather_enjoyment: {
        type: 'slider',
        label: 'How much did you enjoy today\'s weather?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Hated it', '10 - Loved it'],
        required: true,
        default: 5,
        parse: (value) => parseInt(value)
    },
    daily_activities: {
        type: 'checkbox-group',
        label: 'Today\'s Activities & Factors',
        categories: {
            'general': {
                'positive_events': {
                    short: 'Positive Events',
                    long: 'Exceptional Positive Events'
                },
                'negative_events': {
                    short: 'Negative Events',
                    long: 'Exceptional Negative Events'
                },
                'work': {
                    short: 'Work Day',
                    long: 'Did work today (as opposed to day off or weekend)'
                },
                'chores': {
                    short: 'Many Chores',
                    long: 'Exceptional or many Chores/Errands'
                },
                'sick': {
                    short: 'Sick',
                    long: 'Was sick (cold, flu, etc.)'
                },
                'other_medication': {
                    short: 'Other Medication',
                    long: 'Took other medication (not allergy, e.g., painkillers, antibiotics)'
                }
            },
            'activities': {
                'gaming': {
                    short: 'Gaming',
                    long: 'Gaming on Computer/Console/Phone'
                },
                'computer_creative_work': {
                    short: 'Creative PC Work',
                    long: 'Computer Creative Work'
                },
                'creative': {
                    short: 'Creative Other',
                    long: 'Other Creative Activity (e.g., Drawing/Music)'
                },
                'reading': {
                    short: 'Reading',
                    long: 'Reading for Leisure (e.g., Book, Magazine)'
                },
                'outdoor': {
                    short: 'Outdoor',
                    long: 'Outdoor Activities (e.g., Biking/Hiking/Walking)'
                },
                'exercise': {
                    short: 'Exercise',
                    long: 'Exercise/Sports'
                },
                'tv_movies': {
                    short: 'TV/Movies',
                    long: 'TV/Movies/Youtube'
                },
                'smartphone': {
                    short: 'Smartphone',
                    long: 'Longer Smartphone Use (e.g., Browsing, Apps)'
                },
                'social_media': {
                    short: 'Social Media',
                    long: 'Social Media'
                },
                'learning': {
                    short: 'Learning',
                    long: 'Learning (e.g., Language, Course)'
                }
            },
            'social': {
                'family_time': {
                    short: 'Family Time',
                    long: 'Quality Family Time'
                },
                'relationship_time': {
                    short: 'Partner Time',
                    long: 'Quality Time with Partner'
                },
                'phone_call': {
                    short: 'Call Friends',
                    long: 'Phone/Video Call with Friends or Family'
                },
                'neighbors': {
                    short: 'Neighbors',
                    long: 'Interaction with Neighbors or Acquaintances, parents of child\'s friends'
                },
                'friends': {
                    short: 'Friends',
                    long: 'Met Friend in Person, active visiting or inviting'
                },
                'social_outing': {
                    short: 'Social Outing',
                    long: 'Social Outing (Bar, Party, Concert, Event)'
                }
            },
            'eating & drinking': {
                'ate_too_much': {
                    short: 'Ate Too Much',
                    long: 'Ate Too Much'
                },
                'ate_too_little': {
                    short: 'Ate Too Little',
                    long: 'Ate Too Little or Skipped Meal'
                },
                'eating_out': {
                    short: 'Ate Out',
                    long: 'Ate Out (Restaurant, Party)'
                },
                'great_food': {
                    short: 'Great Food',
                    long: 'Ate Food I Liked a Lot'
                },
                'alcohol': {
                    short: 'Alcohol',
                    long: 'Consumed Alcoholic Beverages'
                },
                'other_drugs': {
                    short: 'Other Drugs',
                    long: 'Consumed Other Drugs'
                }

            }
        },
        required: false,
        default: {},
        parse: (selectedValues) => {
            const allOptions = getAllCheckboxOptions(FORM_CONFIG.daily_activities.categories);
            const result = {};
            allOptions.forEach(option => {
                result[option] = selectedValues.includes(option) ? 1 : 0;
            });
            return result;
        }
    },
    daily_comments: {
        type: 'textarea',
        label: 'Additional notes or comments (optional)',
        placeholder: 'Anything unusual today? Specific pain locations? Mood triggers? Things that helped?',
        required: false,
        default: '',
        parse: (value) => value.trim() || null
    }
};

// Helper function to flatten all checkbox options
function getAllCheckboxOptions(categories) {
    const options = [];
    Object.values(categories).forEach(category => {
        options.push(...Object.keys(category));
    });
    return options;
}

// Utility functions for form handling
const FormUtils = {
    // Get default value for a field
    getDefaultValue: function(fieldName) {
        const config = FORM_CONFIG[fieldName];
        return config.default !== undefined ? config.default : null;
    },

    // Parse field value according to its config
    parseFieldValue: function(fieldName, rawValue) {
        const config = FORM_CONFIG[fieldName];
        if (!config || !rawValue) return null;

        if (config.parse) {
            return config.parse(rawValue);
        } else if (config.type === 'checkbox-group') {
            // Default parsing for checkboxes if no custom parse provided
            const allOptions = getAllCheckboxOptions(config.categories);
            const result = {};
            allOptions.forEach(option => {
                result[option] = rawValue.includes(option) ? 1 : 0;
            });
            return result;
        } else {
            return parseInt(rawValue);
        }
    },

    // Set default values on form reset
    setFormDefaults: function() {
    // First reset the entire form to clear all values
    document.getElementById('healthForm').reset();

    // Then set defaults for each field
    Object.entries(FORM_CONFIG).forEach(([fieldName, config]) => {
        const element = document.getElementById(fieldName);
        if (element) {
            if (config.type === 'radio') {
                // Set default radio button
                const radio = document.querySelector(`input[name="${fieldName}"][value="${config.default}"]`);
                if (radio) radio.checked = true;
            } else if (config.type === 'checkbox-group') {
                // Uncheck all checkboxes in the group
                const checkboxes = document.querySelectorAll(`input[name="${fieldName}"]`);
                checkboxes.forEach(cb => cb.checked = false);
            } else if (config.default !== undefined) {
                // Set default value for other field types
                element.value = config.default;
            } else {
                // For fields without defaults, ensure they're empty
                // This fixes the textarea issue
                if (config.type === 'textarea' || element.tagName === 'TEXTAREA') {
                    element.value = '';
                }
            }
        }
    });
},
    // Collect all form data with proper parsing
    collectFormData: function() {
        const formData = {
            date: new Date().toISOString().split('T')[0],
            timestamp: new Date().toISOString()
        };

        Object.entries(FORM_CONFIG).forEach(([fieldName, config]) => {
            let rawValue;

            if (config.type === 'radio') {
                const selected = document.querySelector(`input[name="${fieldName}"]:checked`);
                rawValue = selected ? selected.value : null;
            } else if (config.type === 'checkbox-group') {
                // Get all checked checkboxes
                const checkedBoxes = document.querySelectorAll(`input[name="${fieldName}"]:checked`);
                rawValue = Array.from(checkedBoxes).map(cb => cb.value);
            } else {
                const element = document.getElementById(fieldName);
                rawValue = element ? element.value : null;
            }

            formData[fieldName] = rawValue ? this.parseFieldValue(fieldName, rawValue) : null;
        });

        return formData;
    },

    // Load existing data into form
    loadDataIntoForm: function(data) {
        Object.entries(FORM_CONFIG).forEach(([fieldName, config]) => {
            if (data[fieldName] !== undefined) {
                const element = document.getElementById(fieldName);
                if (element) {
                    if (config.type === 'radio') {
                        // For radio, we need to find the key that matches the value
                        let valueToSet;
                        if (config.encoding) {
                            // Reverse lookup in encoding
                            valueToSet = Object.keys(config.encoding).find(
                                key => config.encoding[key] === data[fieldName]
                            );
                        } else {
                            valueToSet = data[fieldName].toString();
                        }

                        const radio = document.querySelector(`input[name="${fieldName}"][value="${valueToSet}"]`);
                        if (radio) radio.checked = true;
                    } else {
                        element.value = data[fieldName];
                    }
                }
            }
        });
    }
};