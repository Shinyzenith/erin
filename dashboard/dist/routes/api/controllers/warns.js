"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const warns = require('./../models/warns');
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../../../../.env") });
const connectionUri = 'mongodb://127.0.0.1:27017/erin?compressors=snappy';
mongoose_1.default.set('useNewUrlParser', true);
mongoose_1.default.set('useUnifiedTopology', true);
mongoose_1.default.connect(connectionUri, (err) => {
    if (err) {
        console.log(err);
    }
});
async function insertWarn(record, res) {
    const response = await warns.create(record, (err) => {
        if (err) {
            res.status(500).json({ 'message': 'databse entry failed', err });
            return;
        }
    });
}
;
async function fetchWarns(userID, guildID, res) {
    let searchDocument = { uid: userID };
    const records = await warns.findOne(searchDocument, (err) => {
        if (err) {
            res.status(500).json({ 'message': 'fetchWarn function failed with status code 500', err });
        }
    });
    try {
        const warns = records.records.gid[guildID];
        if (typeof (warns) === "undefined") {
            res.status(500).json({ 'message': 'No entry found.' });
            return;
        }
        else {
            console.log(warns);
            return;
        }
    }
    catch {
        res.status(500).json({ 'message': 'No entry found.' });
    }
}
;
fetchWarns("751485005993213995", "820125704649572373");
module.exports = { insertWarn, fetchWarns };
