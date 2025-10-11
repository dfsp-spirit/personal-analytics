// form-config.js
// Configuration object for dynamic form generation
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
        required: false,
        default: 0,
        parse: (value) => parseInt(value)
    },
    energy: {
        type: 'slider',
        label: 'Energy level today?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Exhausted', '10 - Very energetic'],
        required: false,
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
        parse: (value) => FORM_CONFIG.allergy.encoding[value]
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
        required: false,
        default: 5,
        parse: (value) => parseInt(value)
    },
    productivity: {
        type: 'slider',
        label: 'Productivity/accomplishment?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very low', '10 - Very high'],
        required: false,
        default: 5,
        parse: (value) => parseInt(value)
    },
    physical_activity: {
        type: 'select',
        label: 'Physical activity level?',
        options: {
            '0': 'Almost None (e.g., Home office + minimal movement)', '1': 'Light (e.g., cycle to work)', '2': 'Moderate (e.g., work out, sports club)', '3': 'Vigorous (e.g., very long run, competitive sports)'
        },
        required: false,
        default: '0',
        parse: (value) => parseInt(value)
    },
    daily_activities: {
        type: 'checkbox-group',
        label: 'Today\'s Activities (select all that apply)',
        categories: {
            'general': {
                'positive_events': 'Positive Events',
                'negative_events': 'Negative Events',
                'work': 'Did work today (as opposed to day off or weekend)',
                'chores': 'Exceptional or many Chores/Errands',
            },
            'activities': {
                'gaming': 'Gaming',
                'computer_creative_work': 'Computer Creative Work',
                'creative': 'Other Creative Activity (e.g., Drawing/Music)',
                'reading': 'Reading',
                'outdoor': 'Outdoor Activities (e.g., Biking/Hiking/Walking)',
                'exercise': 'Exercise/Sports',
                'tv_movies': 'TV/Movies',
                'smartphone': 'Smartphone (e.g., Browsing, Apps)',
                'social_media': 'Social Media',
                'learning': 'Learning (e.g., Language, Course)',
            },
            'social': {
                'family_time': 'Quality Family Time (not just co-located)',
                'relationship_time': 'Quality Time with Partner',
                'phone_call': 'Phone/Video Call with Friend/Family',
                'neighbors': 'Interaction with Neighbors or Acquaintances, parents of child\'s friends, etc.',
                'friends': 'Met Friend(s) in Person, active visiting or inviting',
                'social_outing': 'Social Outing (e.g., Bar, Party, Event)',
            },
            'eating': {
                'ate_too_much': 'Ate Too Much',
                'ate_too_little': 'Ate Too Little or skipped meal',
                'eating_out': 'Ate Out (e.g., Restaurant, Takeaway, Party. Not including eating out during lunch break at work.)',
                'liked_food': 'Ate Food I Liked a Lot',
            }
        },
        required: false,
        default: {}, // Empty object for none selected
        parse: (selectedValues) => {
            // Convert to binary object: {gaming: 1, reading: 0, ...}
            const allOptions = getAllCheckboxOptions(FORM_CONFIG.daily_activities.categories);
            const result = {};
            allOptions.forEach(option => {
                result[option] = selectedValues.includes(option) ? 1 : 0;
            });
            return result;
        }
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
        Object.entries(FORM_CONFIG).forEach(([fieldName, config]) => {
            if (config.default !== undefined) {
                const element = document.getElementById(fieldName);
                if (element) {
                    if (config.type === 'radio') {
                        const radio = document.querySelector(`input[name="${fieldName}"][value="${config.default}"]`);
                        if (radio) radio.checked = true;
                    } else {
                        element.value = config.default;
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