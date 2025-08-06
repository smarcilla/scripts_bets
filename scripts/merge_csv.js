// merge_csv.js
// Uso: node merge_csv.js output.csv input1.csv input2.csv input3.csv ...

const dfd = require("danfojs-node");
const path = require("path");

async function mergeCSVs(outputPath, inputPaths) {
  const dfs = [];
  for (let p of inputPaths) {
    console.log(`Leyendo ${p}...`);
    const df = await dfd.readCSV(p);
    dfs.push(df);
  }
  const dfAll = dfd.concat(dfs);
  console.log(`Escribiendo ${outputPath} con ${dfAll.shape[0]} filas...`);
  await dfd.toCSV(dfAll, { filePath: outputPath });
  console.log("¡Merge completado!");
}

const [output, ...inputs] = process.argv.slice(2);
if (!output || inputs.length === 0) {
  console.error("Usage: node merge_csv.js output.csv in1.csv in2.csv ...");
  process.exit(1);
}

mergeCSVs(output, inputs).catch(err => console.error(err));
