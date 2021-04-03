"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
var express_1 = __importDefault(require("express"));
var path_1 = __importDefault(require("path"));
var dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../.env") });
var app = express_1.default();
var port = process.env.SERVER_PORT || 8080;
app.set("views", path_1.default.join(__dirname, "./../html/"));
app.set("view engine", "ejs");
app.get("/", function (req, res) {
    res.render("index");
});
app.listen(port, function () {
    console.log("Server started at http://localhost:" + port);
});
