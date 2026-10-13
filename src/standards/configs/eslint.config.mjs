// Provisional lint set: the two recommended sets in the typescript-eslint.io quickstart.
import js from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import globals from "globals";
import tseslint from "typescript-eslint";

export default defineConfig(globalIgnores(["dist/", "build/"]), {
  files: ["**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"],
  extends: [js.configs.recommended, tseslint.configs.recommended],
  languageOptions: {
    globals: { ...globals.browser, ...globals.node },
  },
});
