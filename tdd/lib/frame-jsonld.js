const jsonld = require("../jsonld/lib/jsonld.js");
const data = process.argv[2];
const framedata = process.argv[3];

async function frame() {
  try {
    const doc = await jsonld.fromRDF(data, { format: "application/n-quads", useNativeTypes: "true" });
    try {
      const framed = await jsonld.frame(doc, JSON.parse(framedata));
      return JSON.stringify(framed, null, 2);
    } catch (error) {
      throw new Error(418);
    }
  } catch (error) {
    throw new Error(418);
  }
}

frame().then(console.log);
