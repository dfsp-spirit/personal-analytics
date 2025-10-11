// form-config.js
// Configuration object for dynamic form generation
const FORM_CONFIG = {
    mood: {
        type: 'slider',
        label: 'Overall mood today?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very negative', '10 - Very positive'],
        required: true
    },
    anxiety: {
        type: 'slider',
        label: 'Anxiety level today?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - None', '10 - Extreme'],
        required: false
    },
    energy: {
        type: 'slider',
        label: 'Energy level today?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Exhausted', '10 - Very energetic'],
        required: false
    },
    pain: {
        type: 'slider',
        label: 'Pain Level (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - No pain', '10 - Worst imaginable'],
        required: true
    },
    medication: {
        type: 'select',
        label: 'Anti-Allergic Drug Taken',
        options: {
            0: '0 - None',
            1: '1 - Half pill',
            2: '2 - One pill',
            3: '3 - 1.5 pills',
            4: '4 - Two pills'
        },
        required: true
    },
    allergy: {
        type: 'radio',
        label: 'Allergic Symptoms',
        options: {
            'none': 'None, no allergic symptoms.',
            'other': 'Yes. At body parts other than face.',
            'face': 'Yes. On the face.'
        },
        encoding: { 'none': 0, 'other': 1, 'face': 2 },
        required: true
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
        required: true
    },
    sleep_quality: {
        type: 'slider',
        label: 'Sleep Quality (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very poor', '10 - Excellent'],
        required: true
    },
    stress_level_work: {
        type: 'slider',
        label: 'Work Stress Level (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - No stress', '10 - Extreme stress'],
        required: true
    },
    stress_level_home: {
        type: 'slider',
        label: 'Home Stress Level (0-10)',
        min: 0,
        max: 10,
        scaleLabels: ['0 - No stress', '10 - Extreme stress'],
        required: true
    },
    social_support: {
        type: 'slider',
        label: 'Quality of social interactions?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very poor', '10 - Excellent'],
        required: false
    },

    productivity: {
        type: 'slider',
        label: 'Productivity/accomplishment?',
        min: 0,
        max: 10,
        scaleLabels: ['0 - Very low', '10 - Very high'],
        required: false
    },

    // Physical Activity
    physical_activity: {
        type: 'select',
        label: 'Physical activity level?',
        options: {
            '0': 'None', '1': 'Light', '2': 'Moderate', '3': 'Vigorous'
        },
        required: false
    },

    // Optional: Major events
    positive_events: {
        type: 'radio',
        label: 'Any major positive events?',
        options: {0: 'No', 1: 'Yes'},
        required: false
    },

    negative_events: {
        type: 'radio',
        label: 'Any major negative events?',
        options: {0: 'No', 1: 'Yes'},
        required: false
    }
};