import { GConstructor } from './util';
export class Mappable {
    data: MappableData = null;

    constructor(data: MappableData) {
        this.data = data;
    }

    getData(): {[key: string]: any} {
        return this.data
    }

    traverse(): Mappable[] {
        return []
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

        children.forEach(child => self.appendChild(child.draw()))
        return self
    }
}

export type MappingBase = GConstructor<Mappable>;

export type MappableData = {type: string, [key: string]: any};
export function isMappableData(obj: any): obj is MappableData {
    return typeof obj === 'object' && obj !== null && ("type" in obj)
}