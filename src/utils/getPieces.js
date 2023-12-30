const {decoder} = require('tetris-fumen');
const Hashmap = require('hashmap');
const {glueFumen} = require('./glueFumen');

var pieceVal = new Hashmap();
pieceVal.set('T', 7);
pieceVal.set('I', 6);
pieceVal.set('L', 5);
pieceVal.set('J', 4);
pieceVal.set('S', 3);
pieceVal.set('Z', 2);
pieceVal.set('O', 1);

let builds = [];
let inputFumens = process.argv[2].split(/\s/);
let gluedFumens = glueFumen(inputFumens);

for(let fumenPart of gluedFumens){
    if(fumenPart.startsWith("Warning: ")){
        continue;
    }
    fumenPart = fumenPart.split(" ");
    let subbuilds = [];
    // for each fumen in a line
    for(let fumen of fumenPart){
        let build = [];
        let fumenPages;
        try{
            fumenPages = decoder.decode(fumen);
        } catch {
            console.log(`${fumen} couldn't be decoded`)
            continue;
        }
        

        for(let page of fumenPages){
            build.push(page.operation.type);
        }
        build.sort((a, b) => pieceVal.get(b) - pieceVal.get(a));
        subbuilds.push(build.join(""));
    }
    builds.push(subbuilds.join(";"));
}

console.log(builds.join("\n"))
