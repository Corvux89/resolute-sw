class CustomModal extends HTMLElement{
  private _id: string = ''
  private _title: string = ''
  private bodyContent: string = ''

  constructor() {
    super()
  }

  static get observedAttributes() {
    return ['custom-id', 'title'];
  }

  connectedCallback(){
    this.updateFromAttributes()
    this.render()
  }

  attributeCallbackChange(name: string, oldValue: string, newValue: string){
    if (name == 'custom-id'){
      this._id = newValue || ''
    }

    if (name == 'title'){
      this._title = newValue || ''
    }

    this.render()
  }

  private updateFromAttributes(){
    const customID = this.getAttribute('custom-id')
    const title = this.getAttribute('title')

    if (customID){
      this._id = customID
    }

    if (title){
      this._title = title
    }
  }

  render(){
    this.bodyContent = this.innerHTML

    this.innerHTML = `
    <div class="modal fade" id="${this._id}" tabindex="-1" role="dialog" aria-labelledby="${this._id}">
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header text-center">
            <h4 class="modal-title w-100 font-weight-bold text-black">${this._title}</h4>
            <button type="button" class="close" data-bs-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            ${this.bodyContent}
          </div>
        </div>
      </div>
    </div>
    `
  }
}

class TextInput extends HTMLElement {
  private label: string = '';
  private _id: string = ''; 
  private value: string='';
  private required: boolean = false;
  private disabled: boolean = false;

  constructor() {
      super();
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
  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
      // Update internal properties based on the changed attribute
      if (name === 'label-text') {
          this.label = newValue || ''; 
      }
      if (name === 'custom-id') {
          this._id = newValue || ''; 
      }

      if (name === 'value'){
        this.value = newValue;
      }

      this.required = this.hasAttribute('required')
      this.disabled = this.hasAttribute('disabled')

      this.render(); // Re-render when attributes change
  }

  // Initialize the properties from the attributes if available
  private updateFromAttributes() {
      const labelText = this.getAttribute('label-text');
      const customId = this.getAttribute('custom-id');
      const value = this.getAttribute('value')
      
      if (labelText) {
          this.label = labelText;
      }
      if (customId) {
          this._id = customId;
      }

      if (value){
        this.value = value
      }

      this.required = this.hasAttribute('required')
      this.disabled = this.hasAttribute('disabled')
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
            ${this.required == true ? ' required': ''}
            ${this.disabled == true ? ' disabled' : ''}
            >
          <label for="${this._id}">${this.label}</label>
      </div>
      `;
  }
}

class SelectTab extends HTMLElement {
  private _id: string = '';
  private label: string = '';
  private options: { value: string; label: string }[] = [];
  private selectedValue: string = '';
  private multiple: boolean = false;
  private size: string = '';

  constructor() {
    super();
  }

  static get observedAttributes() {
    return ['options', 'selected', 'custom-id', 'custom-label', 'multiple'];
  }

  connectedCallback() {
    this.updateFromAttributes();
    this.render();
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (name === 'custom-id') {
      this._id = newValue;
    }

    if (name == 'custom-label'){
      this.label = newValue
    }

   this.multiple = this.hasAttribute('multiple')

    if (name === 'options') {
      try {
        this.options = JSON.parse(newValue);
      } catch (e) {
        console.error('Invalid JSON for options attribute', e);
      }
    }

    if (name === 'selected') {
      this.selectedValue = newValue;
    }

    this.render();
  }

  private updateFromAttributes() {
    const id = this.getAttribute('custom-id');
    const label = this.getAttribute('custom-label');
    const options = this.getAttribute('options');
    const selected = this.getAttribute('selected');
    const size = this.getAttribute('size')

    if (id) {
      this._id = id;
    }

    if (label){
      this.label = label;
    }

    if (options) {
      try {
        this.options = JSON.parse(options);
      } catch (e) {
        console.error('Invalid JSON for options attribute', e);
      }
    }

    if (selected) {
      this.selectedValue = selected;
    }

    if (size){
      this.size = size;
    }

    this.multiple = this.hasAttribute('multiple')
    
  }

  private renderOptions() {
    return this.options
      .map(
        (option) =>
          `<option value="${option.value}" ${
            option.value === this.selectedValue ? 'selected' : ''
          }>${option.label}</option>`
      )
      .join('');
  }

  render() {

    if (this.multiple){
      this.innerHTML = `
          <label for="${this._id}" class="text-white">${this.label}</label>
          <select class="form-select" id="${this._id}" ${this.multiple ? 'multiple' : ''} ${this.size!= '' ? `size="${this.size}"` : ''}>
            ${this.renderOptions()}
          </select>
      `;
    } else {
      this.innerHTML = `
        <div class="form-floating">
          <select class="form-select" id="${this._id}" ${this.size!= '' ? `size="${this.size}"` : ''}>
            ${this.renderOptions()}
          </select>
          <label for="${this._id}">${this.label}</label>
        </div>
      `;
    }

  }
}

customElements.define('custom-modal', CustomModal)
customElements.define("text-input", TextInput)
customElements.define("select-tab", SelectTab)