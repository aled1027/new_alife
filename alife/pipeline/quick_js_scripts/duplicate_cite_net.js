// Copies the 'cite_net' collection into a new collection 'traits'
// We want this redundancy so that we still have a collection which fits into RAM
// on teh, but so that we can have a new collection ('traits') with more information
// that all fits into RAM on markov.

db.cite_net.forEach(function(doc) {db.traits.insert(doc); })
