import { Mappable } from "../mapper/Mappable";

export class Renderer {
    constructor() {

    }

    render(root: Mappable): HTMLElement {
        const parent = document.createElement("div")
        console.log("rendering " + root.data.type)
        if ("uuid" in root.data) {
            parent.id = root.data.uuid
        }
        parent.classList.add("wav-source")
        const textContent = document.createTextNode(root.data.type)
        parent.appendChild(textContent)

        const children = root.traverse()

        children.forEach(child => parent.appendChild(this.render(child)))
        return parent
    }
}