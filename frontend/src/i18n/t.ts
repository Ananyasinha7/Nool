import enCore from "./en.core.json";
import taCore from "./ta.core.json";

export type Lang = "en" | "ta";
type Tree = { [k: string]: string | Tree };

function flatten(tree: Tree, prefix = "", out: Record<string, string> = {}): Record<string, string> {
  for (const [k, v] of Object.entries(tree)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (typeof v === "string") out[key] = v;
    else flatten(v, key, out);
  }
  return out;
}

/** Starts with the core strings (login + supervisor); ./app registers the rest when the merchandiser or
 * buyer chunk loads, before any of their components render. */
export const dictionaries: Record<Lang, Record<string, string>> = {
  en: flatten(enCore as Tree),
  ta: flatten(taCore as Tree),
};

export function registerDictionary(lang: Lang, tree: object): void {
  flatten(tree as Tree, "", dictionaries[lang]);
}

/** Keys, not strings, in code: t('sup.send'). Falls back to English, then to the key itself. */
export function translate(lang: Lang, key: string, params?: Record<string, string | number>): string {
  const raw = dictionaries[lang][key] ?? dictionaries.en[key] ?? key;
  if (!params) return raw;
  return raw.replace(/\{(\w+)\}/g, (_, name: string) => String(params[name] ?? `{${name}}`));
}
