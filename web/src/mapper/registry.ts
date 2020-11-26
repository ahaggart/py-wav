import { Mappable, MappingBase } from './Mappable';
import { WithChild, WithChildren } from './TraversalMixins';
import { TransformedSource } from '../sources/TransformedSource';

type WithType = {type: string};

export const registry: {[name: string]: MappingBase} = {
    "transformed": TransformedSource,
    "additive": WithChildren(Mappable, "children", arr => arr[1]),
    "dilation": WithChild(Mappable),
    "sine": Mappable,
    "sequential": WithChildren(Mappable),
    "saw": Mappable,
    "note": Mappable,
    "bezier": Mappable,

    "s_wav": Mappable,

    "fourier": Mappable,

    "t_scaling": Mappable,

    "harmonic": Mappable,
    "beading": Mappable,

    "p_sliding": Mappable,
    "p_source": Mappable,
}

export type Registry = {[name: string]: MappingBase};