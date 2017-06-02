use wordlists
var file = cat('path/to/yourFile.txt');  // read the file
var lines = file.split('\n'); // create an array of words
for (var i = 0, l = lines.length; i < l; i++){ // for every word insert it in the collection
    print(lines[i]); 
}