const {encoder, decoder, Field} = require('tetris-fumen');
const Hashmap = require('hashmap');

const pieceMirror = new Hashmap();
    pieceMirror.set("L", "J");
    pieceMirror.set("J", "L");
    pieceMirror.set("S", "Z");
    pieceMirror.set("Z", "S");

function reverse(value) {  
    return Array.from(
      String(value || '')
    ).reverse().join('')
}

function mirrorPieces(string){
    let mirroredStr = "";
    for(let char of string){
        if(pieceMirror.has(char)){
            mirroredStr += pieceMirror.get(char);
        }
        else{
            mirroredStr += char;
        }
    }
    return mirroredStr;
}

function mirrorFumen(fumen){
    let decodedPages = decoder.decode(fumen);
    let pages = []
    for(let page of decodedPages){
        let field = page.field.str().split("\n").slice(0,-1);
        let newLines = [];
        for(let line of field){
            let reversedLine = reverse(line);
            let newLine = mirrorPieces(reversedLine)
            newLines.push(newLine);
        }

        let newField = Field.create(newLines.join(""));
        pages.push({field: newField, })
    }
    let newFumen = encoder.encode(pages);

    return newFumen;
}

exports.mirrorFumen = mirrorFumen;
exports.mirrorPieces = mirrorPieces;

if(require.main == module){
    let inputFumens = process.argv[2].split(/\s/);
    for(let fumen of inputFumens){
        console.log(mirrorFumen(fumen));
    }
}
