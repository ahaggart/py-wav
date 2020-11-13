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
}

export type MappingBase = GConstructor<Mappable>;

export type MappableData = {type: string, [key: string]: any};
export function isMappableData(obj: any): obj is MappableData {
    return typeof obj === 'object' && obj !== null && ("type" in obj)
}