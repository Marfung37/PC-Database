const fs = require('fs');
const {mirrorFumen, mirrorPieces} = require('./fumenMirror');

// percent tolerance
const percentTolerance = 1;

// piece values
var pieceVal = {
    'T': 7,
    'I': 6,
    'L': 5,
    'J': 4,
    'S': 3,
    'Z': 2,
    'O': 1
}

// output data
var outputData = [];

// read the lines
var lines = fs.readFileSync('sqlInput.tsv').toString().split("\r\n");

// add header line
outputData.push(lines[0].trim());
lines = lines.slice(1);

// hold all the setups
let allSetups = [];

// get the setups from the file
for(let line of lines){
    let setup = line.split("\t")[6];
    allSetups.push(setup);
}

allSetups = Array.prototype.slice.call(allSetups);

// loop through the setups
for(let index in lines){
    // get a line as array
    let line = lines[index].split('\t')
    
    // if there is not already mirror
    if(line[11] == ''){
        // get the setup
        let setup = line[6];
        // get the leftover
        let leftover = line[1];
        // get the build
        let build = line[2];

        // get the fumen of the mirror of the setup
        let mirrorSetup = mirrorFumen(setup);
        
        // mirror the leftover
        let mirrorLeftover = mirrorPieces(leftover).split("");
        mirrorLeftover.sort((a, b) => pieceVal[b] - pieceVal[a]);
        mirrorLeftover = mirrorLeftover.join("")

        let mirrorBuild = mirrorPieces(build).split("");
        mirrorBuild.sort((a, b) => pieceVal[b] - pieceVal[a]);
        mirrorBuild = mirrorBuild.join("")
        
        // check if there is any matches to the mirror
        if(!allSetups.slice(index).includes(mirrorSetup) || (setup == mirrorSetup && leftover == mirrorLeftover && build == mirrorBuild)){
            // set the mirror column to NULL
            // if the leftover can be mirrored
            if(leftover == mirrorLeftover && build == mirrorBuild){
                line[11] = 'NULL';
            } else {
                line[11] = 'Need Mirror';
            }
            
        }
        else{
            let inTolerence = false;
            let startSearchIndex = 0;
            let mirrorIndex = 0;
            let mirrorLine = [];
            let error = false;
            while(!inTolerence){
                // find the mirror index
                let sliceMirrorIndex = Number(allSetups.slice(startSearchIndex).indexOf(mirrorSetup))

                if(sliceMirrorIndex == -1){
                    //console.log(`Line: ${Number(index) + 2}`);
                    //console.log(`Found mirrors but out of tolerence for ${percentTolerance} for ${setup}`)
                    error = true;
                    break;
                }

                mirrorIndex = Number(startSearchIndex) + sliceMirrorIndex;

                // get the mirror line 
                mirrorLine = lines[mirrorIndex].split("\t");

                // get percents from the lines
                let percent = Number(line[9].slice(0, -1));
                let mirrorPercent = Number(mirrorLine[9].slice(0, -1));

                // get cover dependency length
                let coverDependLen = line[3].length;
                let mirrorCoverDependLen = mirrorLine[3].length;

                // check if percent is within tolerance and mirror line doesn't already have a mirror
                let sameCoverLen = coverDependLen == mirrorCoverDependLen;
                let leftoverMirrored = mirrorLine[1] == mirrorLeftover;
                let mirrorDoesntHaveMirror = mirrorLine[11] == '';
                let withinTolerance = Math.abs(percent - mirrorPercent) <= percentTolerance;
                if(sameCoverLen && leftoverMirrored && mirrorDoesntHaveMirror && withinTolerance){
                    inTolerence = true;
                }
                else{
                    startSearchIndex = mirrorIndex + 1;
                }
            }

            if(!error){
                // set the mirror column to the id of the mirror line
                line[11] = mirrorLine[0];

                // set the mirror line mirror column to this id
                mirrorLine[11] = line[0];
                
                // change the mirror line in lines
                lines[mirrorIndex] = mirrorLine.join("\t");
            }
        }
    }

    // output array
    outputData.push(line.join("\t"));
    console.log(line[11]);
}

fs.writeFileSync('sqlOutputWithMirror.csv', outputData.join("\n"));
