import $ from 'jquery'

console.log("hello world")

$(document).ready(main);

function main() {
    $.get("song.json", createElements)
}

function createElements(data, status) {
    const root_container = $("#root-container")
    root_container.append(JSON.stringify(data))
    createElement(root_container, data)
}

function createElement(parent, data) {
    var child = $("<div></div>")
    child.prop("id", data.uuid)
    child.addClass("wav-source")
    child.append(data.type)
    parent.append(child)
}
