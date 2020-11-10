import * as $ from 'jquery';
import { TransformedSource } from './sources/TransformedSource';
import { construct } from './mapper/registry';

console.log("hello world")

$(document).ready(main);

function main() {
    $.get("song.json", createElements)
}

function createElements(data: any, status: any) {
    const root_container = $("#root-container")
    root_container.append(JSON.stringify(data))
    createElement(root_container, data)
}

function createElement(parent: any, data: any) {
    console.log(construct(data))
    var child = $("<div></div>")
    child.prop("id", data.uuid)
    child.addClass("wav-source")
    child.append(data.type)
    parent.append(child)
}
