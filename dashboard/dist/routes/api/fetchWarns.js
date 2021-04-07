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
Object.defineProperty(exports, "__esModule", { value: true });
const express = __importStar(require("express"));
const warns_1 = require("./controllers/warns");
const router = express.Router();
router.get('/', (req, res) => {
    res.status(400).json({ 'message': 'This is the fetch data endpoint, pass gid and uid in the request body to interact with it.' });
});
router.post('/', (req, res) => {
    const body = { ...req.body };
    const guildID = body.gid;
    const userID = body.uid;
    if (typeof (guildID) === "undefined" || typeof (userID) === "undefined") {
        return res.status(400).json({ 'message': 'GuildID or UserID not found in request body' });
    }
    if (typeof (guildID) !== "string" || typeof (userID) !== "string") {
        return res.status(400).json({ 'message': 'GuildID and UserID should be of type string' });
    }
    const warns = warns_1.fetchWarns(userID, guildID, res);
    return true;
});
module.exports = router;
