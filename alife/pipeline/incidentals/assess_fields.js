// Mongo shell script for determining how many patents in spotty quarters have the necessary fields. 
// run with mongo patents assess_fields.js

q21986 = ISODate('1986-04-01')
q31986 = ISODate('1986-07-01')
q12000 = ISODate('2000-01-01')
q22000 = ISODate('2000-04-01')



var x = db.patns.find({'isd': {$gte: q21986, $lt: q31986}}).count()
print('Number of patents in db.patns in Q2 1986: ')
print(x)

var y = db.patns.find({'isd': {$gte: q12000, $lt: q22000}}).count()
print('Number of patents in db.patns in Q1 2000: ')
print(y)

var a = db.patns.find({$and: [{'isd': {$gte: q21986, $lt: q31986}},{'text': {$ne: null}}]}).count()
print('Number of patents in db.patns in Q2 1986 with text: ')
print(a)

var b = db.patns.find({$and: [{'isd': {$gte: q12000, $lt: q22000}},{'text': {$ne: null}}]}).count()
print('Number of patents in db.patns in Q1 2000 with text: ')
print(b)

var z = db.patns.find({$and: [{'isd': {$gte: q21986, $lt: q31986}},{'sorted_text': {$ne: []}}]}).count()
print('Number of patents in db.patns in Q2 1986 with sorted_text: ')
print(z)

var w = db.patns.find({$and: [{'isd': {$gte: q12000, $lt: q22000}},{'sorted_text': {$ne: []}}]}).count()
print('Number of patents in db.patns in Q1 2000 with sorted_text: ')
print(w)

var c = db.patns.find({$and: [{'isd': {$gte: q21986, $lt: q31986}},{'top_tf-idf': {$ne: []}}]}).count()
print('number of patents in db.patns in Q2 1986 with top_tf-idf')
print(c)

var d = db.patns.find({$and: [{'isd': {$gte: q12000, $lt: q22000}},{'top_tf-idf': {$ne: []}}]}).count()
print('number of patents in db.patns in Q1 2000 with top_tf-idf')
print(d)

var e = db.traits.find({$and: [{'isd': {$gte: q21986, $lt: q31986}},{'top_tf-idf': {$ne: []}}]}).count()
print('number of patents in db.traits in Q2 1986 with top_tf-idf')
print(e)

var f = db.traits.find({$and: [{'isd': {$gte: q12000, $lt: q22000}},{'top_tf-idf': {$ne: []}}]}).count()
print('number of patents in db.traits in Q1 2000 with top_tf-idf')
print(f)

var g = db.traits.find({$and: [{'isd': {$gte: q21986, $lt: q31986}},{'doc_vec': {'$exists': true, $nin: [null, []]}}]}).count()
print('number of patents in db.traits in Q2 1986 with doc_vec')
print(g)

var h = db.traits.find({$and: [{'isd': {$gte: q12000, $lt: q22000}},{'doc_vec': {'$exists': true, $nin: [null, []]}}]}).count()
print('number of patents in db.traits in Q1 2000 with doc_vec')
print(h)

var j = db.traits.find({$and: [{'isd': {$gte: q21986, $lt: q31986}},{'wordvec_clusters': {'$exists': true, $nin: [null, []]}}]}).count()
print('number of patents in db.traits in Q2 1986 with wordvec_clusters')
print(g)

var k = db.traits.find({$and: [{'isd': {$gte: q12000, $lt: q22000}},{'wordvec_clusters': {'$exists': true, $nin: [null, []]}}]}).count()
print('number of patents in db.traits in Q1 2000 with wordvec_clusters')
print(h)
