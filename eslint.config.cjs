const js = require("@eslint/js");
const globals = require("globals");
const defineConfig = require("eslint/config").defineConfig;

module.exports = defineConfig([
    {
        files: ["**/*.{js,mjs,cjs}"],
        plugins: { js },
        extends: ["js/recommended"],
        languageOptions: {
            ecmaVersion: 2023,
            sourceType: "script",
            globals: {
                ...globals.browser,
                ...globals.jquery,
            },
        },
    },
]);
