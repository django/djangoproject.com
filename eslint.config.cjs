const js = require("@eslint/js");
const globals = require("globals");
const defineConfig = require("eslint/config").defineConfig;

module.exports = defineConfig([
    {
        files: ["**/*.{js,mjs,cjs}"],
        plugins: { js },
        extends: ["js/recommended"],
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.jquery,
            },
        },
    },
]);
