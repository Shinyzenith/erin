"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express = __importStar(require("express"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../../../.env") });
const router = express.Router();
const connection_uri = process.env.CONNECTION_URI;
router.post('/', async function (req, res) {
    const body = { ...req.body };
    const guildID = body.gid;
    if (typeof (guildID) === "undefined") {
        return res.status(400).json({ 'message': 'GuildID not found in request body' });
    }
    if (typeof (guildID) === "string") {
        return res.status(400).json({ 'message': 'GuildID should be of type number' });
    }
    return res.status(200).json({ 'message': 'successful', 'gid': `recieved guild id ${guildID}` });
});
module.exports = router;
