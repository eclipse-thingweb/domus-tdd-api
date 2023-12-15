const jsonld = require("jsonld");
const data = process.argv[2];

async function transform() {
  const rdf = await jsonld.toRDF(JSON.parse(data), {
    format: "application/n-quads",
  });
  return rdf;
}

transform().then(console.log);
