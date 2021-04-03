"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
var express_1 = __importDefault(require("express"));
var path_1 = __importDefault(require("path"));
var app = express_1.default();
var port = process.env.PORT || 8080;
// Configure Express to use EJS
app.set("views", path_1.default.join(__dirname, "dashboard/html/"));
app.set("view engine", "ejs");
// define a route handler for the default home page
app.get("/", function (req, res) {
    res.render("index");
});
app.listen(port, function () {
    console.log("server started at http://localhost:" + port);
});
