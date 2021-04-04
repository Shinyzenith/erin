"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const express_handlebars_1 = __importDefault(require("express-handlebars"));
dotenv_1.default.config({ "path": path_1.default.join(__dirname, "../../.env") });
const app = express_1.default();
const port = process.env.SERVER_PORT || 8080;
//Handlebars middleware
app.engine('handlebars', express_handlebars_1.default({ defaultLayout: 'homepage' }));
app.set('view engine', 'handlebars');
app.set("views", path_1.default.join(__dirname, "./views"));
app.use(express_1.default.static(path_1.default.join(__dirname + "./../dist/assets")));
app.get('/', (req, res) => {
    res.render('index', {
        content: 'OwO wot dis >~<'
    });
});
app.get('/alt', (req, res) => {
    res.render('index', {
        layout: 'test',
        content: 'OwO UwU >~<'
    });
});
//@TODO: SETUP ./routes instead of this one dirty huge ass file for all the routes > ~ <
app.listen(port, () => console.log(`Server started at http://localhost:${port}`));
