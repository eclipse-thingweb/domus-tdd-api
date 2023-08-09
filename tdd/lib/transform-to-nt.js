const jsonld = require("../jsonld/lib/jsonld.js");
const data = process.argv[2];

async function transform() {
  try {
    const rdf = await jsonld.toRDF(JSON.parse(data), { format: "application/n-quads" });
    return rdf;
  } catch (error) {
    throw new Error(418);
  }
}

transform().then(console.log);
