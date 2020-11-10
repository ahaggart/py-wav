import { GConstructor } from './util';
import { TransformedSource } from '../sources/TransformedSource';

type WithType = {type: string};

const registry: {[name: string]: any} = {
    "transformed": TransformedSource,
}

export function construct(data: WithType): any {
    return registry[data.type](data)
}