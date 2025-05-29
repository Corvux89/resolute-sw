import eslint from '@eslint/js';
import { globalIgnores } from 'eslint/config';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  tseslint.configs.recommended,
  {
    files: ['**/*.ts', '**/*.tsx'], // Ensure TypeScript files are targeted
    extends: [tseslint.configs.disableTypeChecked],
    rules: {
      "no-empty-pattern": "off"
    }
  },
  globalIgnores([
    '**/*.js', // Ignore JavaScript files
  ])
);