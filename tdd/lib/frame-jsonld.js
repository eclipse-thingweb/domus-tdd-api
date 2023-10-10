const jsonld = require("jsonld");
const data = process.argv[2];
const framedata = process.argv[3];

async function frame() {
  const doc = await jsonld.fromRDF(data, {
    format: "application/n-quads",
    useNativeTypes: "true",
  });
  const framed = await jsonld.frame(doc, JSON.parse(framedata));
  return JSON.stringify(framed, null, 2);
}

frame().then(console.log);
