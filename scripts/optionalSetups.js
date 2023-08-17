const {decoder, encoder, Field} = require('tetris-fumen');
const Hashmap = require('hashmap');
const {glueFumen} = require('./glueFumen');
const {unglueFumen} = require('./unglueFumen');

function combinations(set, k) {
	var i, j, combs, head, tailcombs;
	
	// There is no way to take e.g. sets of 5 elements from
	// a set of 4.
	if (k > set.length || k <= 0) {
		return [];
	}
	
	// K-sized set has only one K-sized subset.
	if (k == set.length) {
		return [set];
	}
	
	// There is N 1-sized subsets in a N-sized set.
	if (k == 1) {
		combs = [];
		for (i = 0; i < set.length; i++) {
			combs.push([set[i]]);
		}
		return combs;
	}

    combs = [];
	for (i = 0; i < set.length - k + 1; i++) {
		// head is a list that includes only our current element.
		head = set.slice(i, i + 1);
		// We take smaller combinations from the subsequent elements
		tailcombs = combinations(set.slice(i + 1), k - 1);
		// For each (k-1)-combination we join it with the current
		// and store it to the set of k-combinations.
		for (j = 0; j < tailcombs.length; j++) {
			combs.push(head.concat(tailcombs[j]));
		}
	}
	return combs;
}

var pieceVal = new Hashmap();
pieceVal.set('T', 7);
pieceVal.set('I', 6);
pieceVal.set('L', 5);
pieceVal.set('J', 4);
pieceVal.set('S', 3);
pieceVal.set('Z', 2);
pieceVal.set('O', 1);

// get input
let userInput = process.argv;
let inputFumen = userInput[2];
let choice = userInput[3];
console.log(inputFumen, choice);
if(choice == undefined){
    choice = 1;
}
else{
    choice = parseInt(choice);
}

// first page is static and second page is optional
let inputPages = decoder.decode(inputFumen)
let staticPage = inputPages[0];
let optionalPage = inputPages[1];

// gray out the static part of second page
let grayOptionalField = "";
let staticPageField = staticPage.field.str().split("\n").slice(0, -1);
let optionalPageField = optionalPage.field.str().split("\n").slice(0, -1);

// get the lines from optional page that is taller than static
while(staticPageField.length < optionalPageField.length){
    grayOptionalField += optionalPageField[0];
    optionalPageField = optionalPageField.slice(1);
}

staticPageField = staticPageField.join("\n");
optionalPageField = optionalPageField.join("\n");

for(let index in staticPageField){
    if(staticPageField[index].match(/[TILJSZO]/)){
        grayOptionalField += "X";
    }
    else{
        if(optionalPageField[index] != "\n"){
            grayOptionalField += optionalPageField[index];
        }
    }
}

grayOptionalField = Field.create(grayOptionalField);
let grayOptionalFumen = encoder.encode([{field: grayOptionalField}]);
let gluedGrayOptionalFumen = glueFumen([grayOptionalFumen], false);
let gluedGrayOptionalPages = decoder.decode(gluedGrayOptionalFumen[0]);

let operations = new Hashmap();
let operPieces = [];
for(let page of gluedGrayOptionalPages){
    let piece = page.operation.type;
    operations.set(piece, page.operation);
    operPieces.push(piece);
}

// sort the pieces
operPieces.sort((a, b) => pieceVal.get(b) - pieceVal.get(a));

// get all combinations of length given
pieceCombos = [];
for(let count = 1; count <= choice; count++){
    pieceCombos.push(...combinations(operPieces, count));
}

allOptionalSetupsPages = [staticPage];

for(let combo of pieceCombos){
    let addOperPages = [{field: staticPage.field}];
	let firstPage = true;
    for(let piece of combo){
        addOperPages.push({operation: operations.get(piece)});
        let addOperFumen = encoder.encode(addOperPages);
        let ungluedAddOperFumen = unglueFumen(["--fu", addOperFumen], true);
        addOperPages = [decoder.decode(ungluedAddOperFumen[0])[0]];
    }

    allOptionalSetupsPages.push(addOperPages[0]);
}

let allOptionalFumen = encoder.encode(allOptionalSetupsPages);
console.log(allOptionalFumen);