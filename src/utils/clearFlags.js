const {decoder, encoder} = require("tetris-fumen");


function clearFlags(fumen){
    let newFumen = encoder.encode(decoder.decode(fumen).map(function(page){
        return {field: page.field};
    }));

    return newFumen;
}

exports.clearFlags = clearFlags;

if(require.main == module){
    let inputFumens = process.argv[2].split(/\s/);
    for(let fumen of inputFumens){
        console.log(clearFlags(fumen));
    }
}

