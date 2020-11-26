import { Mappable, MappableData } from '../mapper/Mappable';

export class TransformedSource extends Mappable {
    child: Mappable = null;
    transforms: Mappable[] = null;

    constructor(data: MappableData) {
        super(data)
        this.child = data.child;
        this.transforms = data.transforms
    }

    draw(): HTMLElement {
        const self = document.createElement("div")
        if ("uuid" in this.data) {
            self.id = this.data.uuid
        }
        self.classList.add("wav-source")
        const textContent = document.createTextNode(this.data.type)
        self.appendChild(textContent)

        const children = this.traverse()

        self.appendChild(this.child.draw())
        return self
    }
}