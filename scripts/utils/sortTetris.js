const Hashmap = require('hashmap');

var pieceVal = new Hashmap();
pieceVal.set('T', 7);
pieceVal.set('I', 6);
pieceVal.set('L', 5);
pieceVal.set('J', 4);
pieceVal.set('S', 3);
pieceVal.set('Z', 2);
pieceVal.set('O', 1);

let inputPieces = process.argv[2].split(/\s/);

for(let p of inputPieces){
    let pieces = p.split("")
    pieces.sort((a, b) => pieceVal.get(b) - pieceVal.get(a));
    console.log(pieces.join(""));
}