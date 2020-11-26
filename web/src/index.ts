import * as $ from 'jquery';
import { Mapper } from './mapper/Mapper';
import { registry } from './mapper/registry';
import { Renderer } from './rendering/Renderer';

$(document).ready(main);

function main() {
    $.get("drone.json", createElements)
}

function createElements(data: any, status: any) {
    const root_container = $("#root-container")
    createElement(root_container, data)
    root_container.append(JSON.stringify(data))
}

function createElement(parent: any, data: any) {
    const mapper = new Mapper(registry)
    const root_node = mapper.construct(data)
    const renderer = new Renderer()

    parent.append(root_node.draw())
}
