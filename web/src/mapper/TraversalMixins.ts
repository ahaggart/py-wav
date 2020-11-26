import { Constructor } from './util';
import { Mappable, MappingBase } from './Mappable';

export function WithChild<TBase extends MappingBase>(
    Base: TBase,
    key: string="child",
    extractor: (child: any) => Mappable=e=>e
) {
    return class WithChild extends Base {
        traverse(): Mappable[] {
            return super.traverse().concat([this.data[key]].map(extractor))
        }
    };
}

export function WithChildren<TBase extends MappingBase>(
    Base: TBase,
    key: string="children",
    extractor: (child: any) => Mappable=e=>e
) {
    return class WithChildren extends Base {
        children: Mappable[] = this.data[key];
        
        traverse(): Mappable[] {
            return super.traverse().concat(this.data[key].map(extractor))
        }
    };
}
