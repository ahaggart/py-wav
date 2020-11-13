import { MappingBase, MappableData, isMappableData, Mappable } from './Mappable';
import { Registry } from './registry'; 

export class Mapper {
    registry: Registry = null
    quiet = true

    constructor(registry: Registry, quiet: boolean=true) {
        this.registry = registry
        this.quiet = quiet
    }

    tree_print(msg: string, depth: number) {
        if (!this.quiet) {
            console.log("-".repeat(depth) + msg)
        }
    }

    unpack(obj: MappableData | any[] | any, depth: number, name: string="Value")
    : any {
        if (isMappableData(obj)) { 
            return this.construct(obj, depth)
        } else if (Array.isArray(obj)) {
            this.tree_print("array", depth)
            return obj.map(e => this.unpack(e, depth+1))
        } else {
            this.tree_print(name + ": " + obj, depth)
            return obj
        }
    }

    construct(data: MappableData, depth: number=0): Mappable {
        this.tree_print("Node: " + data.type, depth)

        const fields = Object.keys(data)

        const mappedData = Object.fromEntries(fields.map(field => {
            return [field, this.unpack(data[field], depth+1, field)]
        }))

        try {
            const node =  new this.registry[data.type](mappedData)
            return node
        } catch (err) {
            console.log("Error constructing node of type: " + data.type)
            throw err
        }
    }
}