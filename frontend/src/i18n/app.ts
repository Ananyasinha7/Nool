// Merchandiser and buyer strings. Imported (as a side effect) by those lazy route chunks only.
import enApp from "./en.app.json";
import taApp from "./ta.app.json";
import { registerDictionary } from "./t";

registerDictionary("en", enApp);
registerDictionary("ta", taApp);
