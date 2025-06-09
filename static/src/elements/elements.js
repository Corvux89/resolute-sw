class CustomModal extends HTMLElement {
    constructor() {
        super();
        this._id = '';
        this._title = '';
        this.bodyContent = '';
    }
    getExtraAttributes() {
        // Collect all attributes except those handled by the component
        const exclude = ['custom-id', 'title'];
        return Array.from(this.attributes)
            .filter(attr => !exclude.includes(attr.name))
            .map(attr => `${attr.name}="${attr.value}"`)
            .join(' ');
    }
    static get observedAttributes() {
        return ['custom-id', 'title'];
    }
    connectedCallback() {
        this.updateFromAttributes();
        this.render();
    }
    attributeCallbackChange(name, oldValue, newValue) {
        if (name == 'custom-id') {
            this._id = newValue || '';
        }
        if (name == 'title') {
            this._title = newValue || '';
        }
        this.render();
    }
    updateFromAttributes() {
        const customID = this.getAttribute('custom-id');
        const title = this.getAttribute('title');
        if (customID) {
            this._id = customID;
        }
        if (title) {
            this._title = title;
        }
    }
    render() {
        this.bodyContent = this.innerHTML;
        const extraAttrs = this.getExtraAttributes();
        this.innerHTML = `
    <div class="modal fade" id="${this._id}" tabindex="-1" role="dialog" aria-labelledby="${this._id}" ${extraAttrs}>
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header text-center">
            <h4 class="modal-title w-100 font-weight-bold text-black">${this._title}</h4>
            <button type="button" class="close" data-bs-dismiss="modal" aria-label="Close">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            ${this.bodyContent}
          </div>
        </div>
      </div>
    </div>
    `;
    }
}
class TextInput extends HTMLElement {
    constructor() {
        super();
        this.label = '';
        this._id = '';
        this.value = '';
        this.required = false;
        this.disabled = false;
    }
    // Observe changes to 'label-text' and 'custom-id' attributes
    static get observedAttributes() {
        return ['label-text', 'custom-id', 'value', 'required', 'disabled'];
    }
    // Called when the element is connected to the DOM
    connectedCallback() {
        // Initialize values when the element is connected to the DOM
        this.updateFromAttributes();
        this.render();
    }
    // Called when one of the observed attributes changes
    attributeChangedCallback(name, oldValue, newValue) {
        // Update internal properties based on the changed attribute
        if (name === 'label-text') {
            this.label = newValue || '';
        }
        if (name === 'custom-id') {
            this._id = newValue || '';
        }
        if (name === 'value') {
            this.value = newValue;
        }
        this.required = this.hasAttribute('required');
        this.disabled = this.hasAttribute('disabled');
        this.render(); // Re-render when attributes change
    }
    // Initialize the properties from the attributes if available
    updateFromAttributes() {
        const labelText = this.getAttribute('label-text');
        const customId = this.getAttribute('custom-id');
        const value = this.getAttribute('value');
        if (labelText) {
            this.label = labelText;
        }
        if (customId) {
            this._id = customId;
        }
        if (value) {
            this.value = value;
        }
        this.required = this.hasAttribute('required');
        this.disabled = this.hasAttribute('disabled');
    }
    // Method to render the input field with floating label
    render() {
        this.innerHTML = `
      <div class="form-floating">
          <input 
            type="text" 
            class="form-control" 
            id="${this._id}" 
            ${this.value ? `value="${this.value}"` : ""}
            ${this.required == true ? ' required' : ''}
            ${this.disabled == true ? ' disabled' : ''}
            >
          <label for="${this._id}">${this.label}</label>
      </div>
      `;
    }
}
class NumberInput extends HTMLElement {
    constructor() {
        super();
        this.label = '';
        this._id = '';
        this.required = false;
        this.disabled = false;
    }
    // Observe changes to 'label-text' and 'custom-id' attributes
    static get observedAttributes() {
        return ['label-text', 'custom-id', 'value', 'required', 'disabled', 'step'];
    }
    // Called when the element is connected to the DOM
    connectedCallback() {
        // Initialize values when the element is connected to the DOM
        this.updateFromAttributes();
        this.render();
    }
    // Called when one of the observed attributes changes
    attributeChangedCallback(name, oldValue, newValue) {
        // Update internal properties based on the changed attribute
        if (name === 'label-text') {
            this.label = newValue || '';
        }
        if (name === 'custom-id') {
            this._id = newValue || '';
        }
        if (name == 'step') {
            this.step = Number(newValue);
        }
        if (name === 'value') {
            this.value = Number(newValue);
        }
        this.required = this.hasAttribute('required');
        this.disabled = this.hasAttribute('disabled');
        this.render(); // Re-render when attributes change
    }
    // Initialize the properties from the attributes if available
    updateFromAttributes() {
        const labelText = this.getAttribute('label-text');
        const customId = this.getAttribute('custom-id');
        const value = this.getAttribute('value');
        const step = this.getAttribute('step');
        if (labelText) {
            this.label = labelText;
        }
        if (customId) {
            this._id = customId;
        }
        if (this.step) {
            this.step = Number(step);
        }
        if (value) {
            this.value = Number(value);
        }
        this.required = this.hasAttribute('required');
        this.disabled = this.hasAttribute('disabled');
    }
    // Method to render the input field with floating label
    render() {
        this.innerHTML = `
      <div class="form-floating">
        <input type="number" class="form-control" id="${this._id}" value="${this.value ?? ''}" 
        step="${this.step ?? 1}"
        ${this.required ? 'required' : ''}
        ${this.disabled ? 'disabled' : ''}
        />
        <label for="${this._id}">${this.label}</label>
      </div>
    `;
    }
}
export class SelectInput extends HTMLElement {
    constructor() {
        super();
        this._id = '';
        this.label = '';
        this.options = [];
        this.selectedValue = '';
        this.multiple = false;
        this.size = '';
        this.allowNone = false;
    }
    static get observedAttributes() {
        return ['options', 'selected', 'custom-id', 'custom-label', 'multiple', 'allownone'];
    }
    connectedCallback() {
        this.updateFromAttributes();
        this.render();
    }
    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'custom-id') {
            this._id = newValue;
        }
        if (name == 'custom-label') {
            this.label = newValue;
        }
        this.multiple = this.hasAttribute('multiple');
        if (name === 'options') {
            try {
                this.options = JSON.parse(newValue);
            }
            catch (e) {
                console.error('Invalid JSON for options attribute', e);
            }
        }
        if (name === 'selected') {
            this.selectedValue = newValue;
        }
        this.allowNone = this.hasAttribute('allownone');
        this.render();
    }
    updateFromAttributes() {
        const id = this.getAttribute('custom-id');
        const label = this.getAttribute('custom-label');
        const options = this.getAttribute('options');
        const selected = this.getAttribute('selected');
        const size = this.getAttribute('size');
        if (id) {
            this._id = id;
        }
        if (label) {
            this.label = label;
        }
        if (options) {
            try {
                this.options = JSON.parse(options);
            }
            catch (e) {
                console.error('Invalid JSON for options attribute', e);
            }
        }
        if (selected) {
            this.selectedValue = selected;
        }
        if (size) {
            this.size = size;
        }
        this.allowNone = this.hasAttribute('allownone');
        this.multiple = this.hasAttribute('multiple');
    }
    renderOptions() {
        let options = this.options;
        if (this.allowNone) {
            options = [{ value: '', label: '' }, ...options];
        }
        return options
            .map((option) => `<option value="${option.value}" ${option.value == this.selectedValue ? 'selected' : ''}>${option.label}</option>`)
            .join('');
    }
    render() {
        if (this.multiple) {
            this.innerHTML = `
          <label for="${this._id}" class="text-white">${this.label}</label>
          <select class="form-select" id="${this._id}" ${this.multiple ? 'multiple' : ''} ${this.size != '' ? `size="${this.size}"` : ''}>
            ${this.renderOptions()}
          </select>
      `;
        }
        else {
            this.innerHTML = `
        <div class="form-floating">
          <select class="form-select" id="${this._id}" ${this.size != '' ? `size="${this.size}"` : ''}>
            ${this.renderOptions()}
          </select>
          <label for="${this._id}">${this.label}</label>
        </div>
      `;
        }
    }
}
customElements.define('custom-modal', CustomModal);
customElements.define("text-input", TextInput);
customElements.define("number-input", NumberInput);
customElements.define("select-input", SelectInput);
