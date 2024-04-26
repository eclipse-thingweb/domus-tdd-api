const path = require("path");

module.exports = {
  context: path.resolve(__dirname, "js-src"),
  target: "node16",
  entry: {
    "frame-jsonld": ["./frame-jsonld"],
    "transform-to-nt": ["./transform-to-nt"],
  },
  output: {
    path: path.resolve(__dirname, "tdd", "lib"),
    filename: "[name].js",
  },
  resolve: {
    fallback: {
      "rdf-canonize-native": false,
      "web-streams-polyfill/ponyfill/es2018": false,
    },
  },
};
