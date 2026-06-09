import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";


export default [
  {
    files: [ "**/*.{js,mjs,cjs,ts,vue}" ],
  },
  {
    languageOptions: {
      globals: globals.browser
    }
  },
  {
    rules: {
      "no-unused-vars": "warn",
    }
  },
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs["flat/base"],
  ...pluginVue.configs["flat/recommended"],
  ...pluginVue.configs["flat/strongly-recommended"],
  {
    files: [ "**/*.vue" ],
    languageOptions: {
      parserOptions:
        {
          parser: tseslint.parser
        }
    },
  },
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/member-ordering": [ "error", {
        default: [
          "public-static-field",
          "public-static-method",
          "public-instance-field",
          "public-constructor",
          "public-instance-method",

          "protected-static-field",
          "protected-static-method",
          "protected-instance-field",
          "protected-constructor",
          "protected-instance-method",

          "private-static-field",
          "private-static-method",
          "private-instance-field",
          "private-constructor",
          "private-instance-method"
        ]
      } ],
      "no-native-reassign": "error",
      'vue/no-unused-vars': 'error',
      "vue/require-default-prop": "off",
      "vue/attribute-hyphenation": [ "error", "never" ],
      "vue/component-definition-name-casing": [ "error", "PascalCase" ],
      "vue/prop-name-casing": [ "error", "camelCase" ],
      "vue/attributes-order": [ "error", {
        "order": [
          "DEFINITION",
          "LIST_RENDERING",
          "CONDITIONALS",
          "RENDER_MODIFIERS",
          "GLOBAL",
          [ "UNIQUE", "SLOT" ],
          "TWO_WAY_BINDING",
          "ATTR_STATIC",
          "ATTR_DYNAMIC",
          "ATTR_SHORTHAND_BOOL",
          "OTHER_DIRECTIVES",
          "EVENTS",
          "CONTENT"
        ],
        "alphabetical": true
      } ],
      "vue/max-attributes-per-line": [ "error", {
        "singleline": {
          "max": 2
        },
        "multiline": {
          "max": 1
        }
      } ],
      "vue/v-on-event-hyphenation": [ "error", "never" ],
      "vue/block-lang": [ "error", {
        "script": {
          "lang": "ts"
        }
      } ],
      "vue/block-order": [ "error", {
        "order": [ [ "template", "script" ], "style" ]
      } ],
      "vue/component-name-in-template-casing": [ "error", "PascalCase" ],
      "vue/custom-event-name-casing": [ "error", "camelCase", {
        "ignores": [ "/^([a-zA-Z]+:)+[a-zA-Z]+$/u" ]
      } ],
      "vue/define-emits-declaration": [ "error", "type-based" ],
      "vue/enforce-style-attribute": [ "error", {
        "allow": [ "plain" ]
      } ],
      "vue/html-comment-content-spacing": [ "error", "always" ],
      "vue/html-comment-indent": [ "error", "tab" ],
      "vue/max-template-depth": [ "warn", {
        maxDepth: 7
      } ],
      "vue/no-boolean-default": [ "error", "default-false" ],
      "vue/no-empty-component-block": [ "error" ],
      "vue/no-multiple-objects-in-class": [ "error" ],
      "vue/no-ref-object-reactivity-loss": [ "error" ],
      "vue/no-restricted-component-names": [
        "error",
        {
          "name": "/^custom/",
          "message": "Please do not use component names starting with 'custom'"
        }
      ],
      "vue/no-static-inline-styles": [ "error" ],
      "vue/no-root-v-if": [ "error" ],
      "vue/no-template-target-blank": [ "error" ],
      "vue/no-undef-properties": [ "error" ],
      "vue/no-unused-refs": [ "error" ],
      "vue/no-use-v-else-with-v-for": [ "error" ],
      "vue/no-useless-v-bind": [ "error" ],
      "vue/no-v-text": [ "error" ],
      "vue/padding-line-between-blocks": [ "error" ],
      "vue/require-macro-variable-name": [ "error" ],
      "vue/require-typed-ref": [ "error" ],

      "no-duplicate-imports": [ "error" ],
      "no-undef": 0,
      "@typescript-eslint/no-unused-vars": [ "error", {
        "args": "all",
        "argsIgnorePattern": "^_",
        "caughtErrorsIgnorePattern": "^_",
        "destructuredArrayIgnorePattern": "^_",
        "caughtErrors": "all",
        "varsIgnorePattern": "^props$",
        "ignoreRestSiblings": true
      } ]
    },
    languageOptions: {
      globals: {
        ENVIRONMENT: 'readonly',
        RUNTIME_ENVIRONMENT: 'readonly'
      }
    }
  }
];