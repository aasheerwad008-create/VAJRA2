const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying KavachaTrustRegistry to Polygon Amoy...");
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const Registry = await hre.ethers.getContractFactory("KavachaTrustRegistry");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();
  const addr = await registry.getAddress();

  console.log("Contract deployed at:", addr);
  console.log("Explorer:", `https://amoy.polygonscan.com/address/${addr}`);

  // Save for frontend
  const out = { contractAddress: addr, network: hre.network.name, deployedAt: new Date().toISOString() };
  const outPath = path.join(__dirname, "../../frontend/lib/deployment.json");
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  console.log("Saved to frontend/lib/deployment.json");
}

main().catch(e => { console.error(e); process.exitCode = 1; });
