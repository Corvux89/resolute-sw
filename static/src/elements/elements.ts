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

customElements.define('custom-modal', CustomModal)