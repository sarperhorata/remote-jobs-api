#!/usr/bin/env node

/**
 * Pre-commit test runner for Buzz2Remote frontend.
 * Runs essential tests and blocks deployment if they fail.
 * Priority: Syntax → Unit → Integration
 */

const { spawn } = require('child_process');

function runCommand(command, args = []) {
  return new Promise((resolve) => {
    const process = spawn(command, args, { 
      stdio: 'pipe',
      shell: true 
    });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      resolve({
        success: code === 0,
        stdout,
        stderr,
        code
      });
    });
  });
}

async function main() {
  console.log(`
🧪 Frontend Pre-Commit Test Suite
Time: ${new Date().toLocaleString()}
Priority: Syntax → Unit → Build → Lint
`);

  // Tests to run in priority order (most critical first)
  const tests = [
    {
      name: "🔍 Build Syntax & Import Tests Structure Tests",
      command: "npm test -- --testPathPattern=build-test --watchAll=false --verbose=false"
    },
    {
      name: "🔧 Unit Tests", 
      command: "npm test -- --testPathPattern=unit --watchAll=false --verbose=false"
    },
    {
      name: "🏗️ Build Test",
      command: "npm run build"
    },
    {
      name: "📋 Lint Check",
      command: "npm run lint"
    }
  ];

  let allPassed = true;

  for (const test of tests) {
    console.log(`Running ${test.name}...`);
    
    const result = await runCommand(test.command);
    
    if (result.success) {
      console.log(`✅ ${test.name} PASSED`);
    } else {
      console.log(`❌ ${test.name} FAILED`);
      console.log(`Error: ${result.stderr}`);
      
      // Only show critical errors, not all build warnings
      if (result.stderr && !result.stderr.includes('Warning:')) {
        console.log(`Details: ${result.stdout.substring(0, 500)}...`);
      }
      
      allPassed = false;
      // Stop at first failure for faster feedback
      break;
    }
  }

  console.log("\n" + "=".repeat(50));

  if (allPassed) {
    console.log("🎉 ALL FRONTEND TESTS PASSED! Safe to deploy.");
    console.log("💡 Run 'npm test -- --coverage' for full test suite with coverage");
    process.exit(0);
  } else {
    console.log("💥 FRONTEND TESTS FAILED! DO NOT DEPLOY!");
    console.log("🔧 Fix the failing tests before committing.");
    console.log("📝 Most likely issues:");
    console.log("   - Syntax errors (missing semicolons, brackets)");
    console.log("   - Import errors (missing dependencies, wrong paths)");
    console.log("   - Build errors (TypeScript, React compilation)");
    console.log("   - Component rendering issues");
    process.exit(1);
  }
}

// Handle process termination gracefully
process.on('SIGINT', () => {
  console.log('\n🛑 Test run interrupted by user');
  process.exit(1);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Test run terminated');
  process.exit(1);
});

main().catch(error => {
  console.error('❌ Test runner failed:', error.message);
  process.exit(1);
}); 