// form-generator.js

// Add a doc string for function:
// Generates a form based on the provided configuration object
// Each field is created according to its type and properties
// Supports slider, select, and radio input types
// Handles required fields and displays scale labels for sliders



function generateFormField(fieldName, config) {
    const wrapper = document.createElement('div');
    wrapper.className = 'form-group';
    wrapper.id = `field-${fieldName}`;

    // Label
    const label = document.createElement('label');
    label.textContent = config.label;
    if (config.required) {
        label.classList.add('required');
    }
    wrapper.appendChild(label);

    // Generate input based on type
    switch(config.type) {
        case 'slider':
            wrapper.appendChild(generateSlider(fieldName, config));
            break;
        case 'select':
            wrapper.appendChild(generateSelect(fieldName, config));
            break;
        case 'radio':
            wrapper.appendChild(generateRadio(fieldName, config));
            break;
    }

    return wrapper;
}

function generateSlider(fieldName, config) {
    const container = document.createElement('div');

    // Slider input
    const slider = document.createElement('input');
    slider.type = 'range';
    slider.id = fieldName;
    slider.name = fieldName;
    slider.min = config.min;
    slider.max = config.max;
    slider.value = config.min;
    slider.required = config.required;
    container.appendChild(slider);

    // Scale labels
    if (config.scaleLabels) {
        const labels = document.createElement('div');
        labels.className = 'scale-labels';
        labels.innerHTML = `<span>${config.scaleLabels[0]}</span><span>${config.scaleLabels[1]}</span>`;
        container.appendChild(labels);
    }

    // Current value display
    const valueDisplay = document.createElement('div');
    valueDisplay.className = 'value-display';  // Add this line
    valueDisplay.innerHTML = `Current: <span id="${fieldName}Value">${config.min}</span>`;
    container.appendChild(valueDisplay);

    // Live value update
    slider.addEventListener('input', function() {
        document.getElementById(`${fieldName}Value`).textContent = this.value;
    });

    return container;
}

function generateSelect(fieldName, config) {
    const select = document.createElement('select');
    select.id = fieldName;
    select.name = fieldName;
    select.required = config.required;

    for (const [value, text] of Object.entries(config.options)) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        select.appendChild(option);
    }

    return select;
}

function generateRadio(fieldName, config) {
    const container = document.createElement('div');
    container.className = 'radio-group';

    for (const [value, text] of Object.entries(config.options)) {
        const label = document.createElement('label');

        const input = document.createElement('input');
        input.type = 'radio';
        input.name = fieldName;
        input.value = value;
        input.required = config.required;

        label.appendChild(input);
        label.appendChild(document.createTextNode(text));
        container.appendChild(label);
        container.appendChild(document.createElement('br'));
    }

    return container;
}