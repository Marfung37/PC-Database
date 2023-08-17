const { execSync } = require("child_process");
const {encoder, decoder, Field} = require('tetris-fumen');
const { glueFumen } = require("./glueFumen");
const fs = require("fs");
const csvStream = require("csv-reader")

const considerPercents = true;
const sfinder = `${__dirname}/solution-finder-1.4.2/sfinder.jar`
const extendedPieces = `${__dirname}/util/pieces.py`

function reverse(value){  
    return Array.from(
      String(value || '')
    ).reverse().join('')
}

function mirrorField(field){
    const pieceMirror = {
        "L": "J",
        "J": "L",
        "S": "Z",
        "Z": "S"
    }

    let newLines = [];
    for(let line of field){
        let reversedLine = reverse(line);
        let newL = "";
        for(let m of reversedLine){
            if(pieceMirror[m]){
                newL += pieceMirror[m];
            }
            else{
                newL += m;
            }
        }
        newLines.push(newL);
    }

    return newLines;
    
}

var newFumens = [];
var filename = process.argv[2];
var lines = fs.createReadStream(filename, {encoding:'utf8', flag:'r'});
lines.pipe(new csvStream({ parseNumbers: true, parseBooleans: true, trim: true })).on('data', function(line){
    // hold the pages that are congruent
    let pages = [];

    let build = line[2];
    let coverDependency = line[3];
    let intermediateSetup = line[4];
    let setup = line[5]
    let pieces = line[6];
    let percent = line[7];
    let mirror = line[9]

    if(intermediateSetup || build.includes(";")){
        console.log(setup);
        return;
    }

    // cyanize and format field)
    let fumenPages = decoder.decode(setup);
    for(let page of fumenPages){
        let field = page.field.str();
        field = field.replace(/[TILJSZO]/g, "I");
        field = field.split("\n").slice(0, -1);
        
        for(let i = 0; i < 2; i++){
            if(i == 1){
                if(mirror === 'NULL'){
                    field = mirrorField(field);
                } else {
                    break;
                }
            }

            // shift to right wall
            let fullCol = field.length == 4;
            while(fullCol){
                let oldField = [...field];
                for(let row = 0; row < field.length; row++){
                    if(field[row][field[row].length - 1] != "I"){
                        fullCol = false;
                        field = oldField;
                        break;
                    }
                    field[row] = "I" + field[row].slice(0,-1);
                }
            }

            fullCol = true;
            while(fullCol){
                // make cyan fumen code and execute setup
                let cyanFumen = encoder.encode([{field: Field.create(field.join(""))}]);
                execSync(`pypy3 ${extendedPieces} '[${build}]!' > ${__dirname}input/patterns.txt; java -jar ${sfinder} setup -t ${cyanFumen} -f I -d 180`)

                // read from setup.html to get all fumens
                let setupLines = fs.readFileSync(`${__dirname}/output/setup.html`, {encoding:'utf8', flag:'r'});
                let allSetupsLine = setupLines.split("\n")[4];
                let congruentFumen = allSetupsLine.slice(35,-25);
                // if there is any match
                if(considerPercents && congruentFumen){
                    // check for percent matches
                    execSync(`python ${extendedPieces} '${pieces}' > ${__dirname}/input/patterns.txt; java -jar ${sfinder} percent -t ${cyanFumen} -d 180`)
                    let percentLines = fs.readFileSync("${__dirname}/output/last_output.txt", {encoding:'utf8', flag:'r'});
                    let congruentPercent = percentLines.split("\n")[33].match(/^success = (\d+\.\d\d%)/)[1];

                    if(congruentPercent === percent){
                        let outFumenPages = decoder.decode(congruentFumen);
                        for(let p of outFumenPages){
                            pages.push({field: p.field});
                        }
                    } else {
                        // warning about a setup that has weird matches
                        console.log(field.join("\n"))
                        console.log(`The field for ${setup} has ${congruentPercent} but original has ${percent}`);

                    }
                    
                } else {
                    let outFumenPages = decoder.decode(congruentFumen);
                    for(let p of outFumenPages){
                        pages.push({field: p.field});
                    }
                }
                
                
                // shift towards left wall
                if(field.length == 4){
                    let oldField = [...field];
                    for(let row = 0; row < field.length; row++){
                        if(field[row][0] != "I"){
                            fullCol = false;
                            field = oldField;
                            break;
                        }
                        field[row] = field[row].slice(1) + "I";
                    }
                } else { 
                    fullCol = false;
                }
               
            }
        }
        
    }

    let preCoverFumen = encoder.encode(pages);

    // put through gluingfumens
    let gluedFumens = glueFumen(preCoverFumen)

    // put through cover
    execSync(`python ${extendedPieces} '${coverDependency}' > ${__dirname}/input/patterns.txt; java -jar ${sfinder} cover -t ${gluedFumens} -d 180`);

    // run cover to path
    execSync(`python ${__dirname}/util/cover-to-path.py ${__dirname}/output/cover.csv`);

    // run true minimals
    execSync(`node sfinder-strict-minimal/cli.js ${__dirname}/output/cover_to_path.csv`)

    let minimalData = fs.readFileSync("path_minimal_strict.md", {encoding:'utf8', flag:'r'});
    let minimalFumens = minimalData.match(/(v115@[a-zA-Z0-9?/+]*)/g);
    minimalFumens = minimalFumens.slice(0, minimalFumens.length / 2);

    let minimalPages = [];
    for(let code of minimalFumens){
        let page = decoder.decode(code)[0];
        minimalPages.push({field: page.field});
    }

    let minimalFumen = encoder.encode(minimalPages);

    newFumens.push(minimalFumen);
    console.log(minimalFumen);
})
