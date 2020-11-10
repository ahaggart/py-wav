export class TransformedSource {
    child: any = null;

    constructor(data: {[child: string]: any}) {
        this.child = data.child;
    }
}