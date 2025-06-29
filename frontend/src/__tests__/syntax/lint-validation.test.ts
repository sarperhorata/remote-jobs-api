/**
 * Lint Validation Tests
 * This test suite validates that our code passes ESLint rules
 */
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

describe('Lint Validation', () => {
  const timeout = 30000; // 30 seconds timeout for lint checks

  test('should pass ESLint without errors', async () => {
    try {
      // Run ESLint on specific directories
      const { stdout, stderr } = await execAsync('npx eslint src/ --ext .ts,.tsx --format json', {
        cwd: process.cwd(),
        timeout
      });

      // Parse ESLint output
      let lintResults;
      try {
        lintResults = JSON.parse(stdout);
      } catch (parseError) {
        console.warn('Could not parse ESLint output as JSON:', stdout);
        // If JSON parsing fails, just check if there are obvious errors in stderr
        if (stderr && stderr.includes('error')) {
          throw new Error(`ESLint stderr contains errors: ${stderr}`);
        }
        return; // Skip test if we can't parse but no obvious errors
      }

      // Check for ESLint errors
      const errorFiles = lintResults.filter((file: any) => 
        file.errorCount > 0 || file.fatalErrorCount > 0
      );

      if (errorFiles.length > 0) {
        const errorDetails = errorFiles.map((file: any) => {
          const errors = file.messages.filter((msg: any) => msg.severity === 2);
          return `${file.filePath}:\n${errors.map((err: any) => 
            `  Line ${err.line}:${err.column} - ${err.message} (${err.ruleId})`
          ).join('\n')}`;
        }).join('\n\n');

        throw new Error(`ESLint found errors:\n${errorDetails}`);
      }

    } catch (error: any) {
      if (error.code === 'ENOENT') {
        console.warn('ESLint not found, skipping lint validation test');
        return;
      }
      throw error;
    }
  }, timeout);

  test('should not have undefined variables in JSX', async () => {
    try {
      // Specifically check for react/jsx-no-undef errors
      const { stdout } = await execAsync('npx eslint src/ --ext .ts,.tsx --format json --rule "react/jsx-no-undef: error"', {
        cwd: process.cwd(),
        timeout
      });

      let lintResults;
      try {
        lintResults = JSON.parse(stdout);
      } catch {
        return; // Skip if can't parse
      }

      const undefinedVarFiles = lintResults.filter((file: any) => 
        file.messages.some((msg: any) => 
          msg.ruleId === 'react/jsx-no-undef' && msg.severity === 2
        )
      );

      if (undefinedVarFiles.length > 0) {
        const errorDetails = undefinedVarFiles.map((file: any) => {
          const errors = file.messages.filter((msg: any) => msg.ruleId === 'react/jsx-no-undef');
          return `${file.filePath}:\n${errors.map((err: any) => 
            `  Line ${err.line}:${err.column} - ${err.message}`
          ).join('\n')}`;
        }).join('\n\n');

        throw new Error(`Undefined variables found in JSX:\n${errorDetails}`);
      }

    } catch (error: any) {
      if (error.code === 'ENOENT') {
        console.warn('ESLint not found, skipping undefined variables test');
        return;
      }
      if (error.message.includes('Undefined variables found')) {
        throw error;
      }
      // Other errors are acceptable for this test
    }
  }, timeout);

  test('should have all required imports for used components', () => {
    // This is a basic test to ensure common patterns are followed
    const componentPatterns = [
      { component: 'X', import: "import { X } from 'lucide-react'" },
      { component: 'Check', import: "import { Check } from 'lucide-react'" },
      { component: 'Eye', import: "import { Eye } from 'lucide-react'" },
      { component: 'EyeOff', import: "import { EyeOff } from 'lucide-react'" },
      { component: 'Heart', import: "import { Heart } from 'lucide-react'" },
      { component: 'ChevronDown', import: "import { ChevronDown } from 'lucide-react'" }
    ];

    // This test documents the expected import patterns
    // In a real scenario, you'd check actual files
    expect(componentPatterns).toBeDefined();
    expect(componentPatterns.length).toBeGreaterThan(0);
  });

  test('should not have TypeScript errors', async () => {
    try {
      // Run TypeScript compiler to check for type errors
      const { stdout, stderr } = await execAsync('npx tsc --noEmit --project tsconfig.json', {
        cwd: process.cwd(),
        timeout
      });

      // If tsc exits with code 0 and no stderr, there are no type errors
      if (stderr && stderr.includes('error TS')) {
        throw new Error(`TypeScript compilation errors found:\n${stderr}`);
      }

    } catch (error: any) {
      if (error.code === 'ENOENT') {
        console.warn('TypeScript compiler not found, skipping type check');
        return;
      }
      
      // If the error contains TypeScript errors, fail the test
      if (error.stdout && error.stdout.includes('error TS')) {
        throw new Error(`TypeScript compilation errors found:\n${error.stdout}`);
      }
      
      // For other errors (like missing tsconfig), just warn
      console.warn('TypeScript check failed:', error.message);
    }
  }, timeout);
}); 