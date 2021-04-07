"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const warnSchema = new mongoose_1.default.Schema({
    type: { type: String, required: true },
    reason: { type: String, required: true },
    time: { type: String, required: true },
    mod: { type: String, required: true }
});
const userWarnScheme = new mongoose_1.default.Schema({
    uid: { type: String, required: true },
    gid: mongoose_1.default.Schema.Types.Mixed
});
const userWarnModel = mongoose_1.default.model('warns', userWarnScheme);
module.exports = userWarnModel;
