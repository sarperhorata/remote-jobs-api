#!/usr/bin/env node

/**
 * Pre-commit test runner for Buzz2Remote frontend.
 * Runs essential tests and blocks deployment if they fail.
 * Priority: Build Tests → Unit → Build → Lint
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
Priority: Build Tests → Unit → Build → Lint
`);

  // Tests to run in priority order (most critical first)
  const tests = [
    {
      name: "🔍 Build & Structure Tests",
      command: "npm test -- --testPathPattern=build-test --watchAll=false"
    },
    {
      name: "🔧 Unit Tests", 
      command: "npm test -- --testPathPattern=unit --watchAll=false"
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
      console.log(`Error: ${result.stderr.substring(0, 200)}...`);
      
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
    console.log("   - Build errors (TypeScript, React compilation)");
    console.log("   - Missing dependencies or files");
    console.log("   - Component structure issues");
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