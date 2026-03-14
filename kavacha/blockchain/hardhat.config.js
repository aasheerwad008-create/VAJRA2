require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const hasValidKey = PRIVATE_KEY && PRIVATE_KEY.length >= 64 && PRIVATE_KEY !== "your_wallet_private_key_here";

module.exports = {
  solidity: "0.8.20",
  networks: {
    amoy: {
      url: process.env.POLYGON_AMOY_RPC || "https://rpc-amoy.polygon.technology",
      accounts: hasValidKey ? [PRIVATE_KEY] : [],
      chainId: 80002,
    }
  }
};
