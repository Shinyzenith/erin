"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../../../../.env") });
const connectionUri = 'mongodb://127.0.0.1:8090/local';
mongoose_1.default.set('useNewUrlParser', true);
mongoose_1.default.set('useUnifiedTopology', true);
mongoose_1.default.connect(connectionUri, (err) => {
    if (err) {
        console.log(err.message);
    }
    else {
        console.log("Successfully connected to the mongo instance");
    }
});
