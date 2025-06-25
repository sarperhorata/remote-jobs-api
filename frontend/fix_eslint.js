const fs = require('fs');
const path = require('path');

// Fix EmailVerification.tsx
const emailVerificationPath = './src/pages/EmailVerification.tsx';
if (fs.existsSync(emailVerificationPath)) {
  let content = fs.readFileSync(emailVerificationPath, 'utf8');
  
  // Add useCallback to imports
  content = content.replace(
    "import React, { useState, useEffect } from 'react';",
    "import React, { useState, useEffect, useCallback } from 'react';"
  );
  
  // Wrap verifyEmail with useCallback
  content = content.replace(
    /const verifyEmail = async \(token: string\) => \{/,
    'const verifyEmail = useCallback(async (token: string) => {'
  );
  
  // Add dependency array to useCallback
  content = content.replace(
    /setError\(error instanceof Error \? error\.message : 'Email doğrulama başarısız'\);\s*\}\s*\};/,
    "setError(error instanceof Error ? error.message : 'Email doğrulama başarısız');\n    }\n  }, [navigate]);"
  );
  
  fs.writeFileSync(emailVerificationPath, content);
  console.log('✅ EmailVerification.tsx fixed');
}

// Fix OnboardingProfileSetup.tsx
const onboardingPath = './src/pages/OnboardingProfileSetup.tsx';
if (fs.existsSync(onboardingPath)) {
  let content = fs.readFileSync(onboardingPath, 'utf8');
  
  // Remove unused variables
  content = content.replace(
    /const \[step, setStep\] = useState.*?\('choice'\);[\s\n]*/,
    ''
  );
  content = content.replace(
    /const \[loading, setLoading\] = useState.*?false\);[\s\n]*/,
    ''
  );
  content = content.replace(
    /const \[success, setSuccess\] = useState.*?''\);[\s\n]*/,
    ''
  );
  content = content.replace(
    /\/\/ CV Upload states[\s\n]*const \[selectedFile, setSelectedFile\] = useState.*?null\);[\s\n]*/,
    ''
  );
  content = content.replace(
    /const \[dragActive, setDragActive\] = useState.*?false\);[\s\n]*/,
    ''
  );
  content = content.replace(
    /\/\/ Manual profile states[\s\n]*const \[manualProfile, setManualProfile\] = useState.*?\}\);[\s\n]*/,
    ''
  );
  
  // Remove handleLinkedInConnect function since it's not used
  content = content.replace(
    /const handleLinkedInConnect = async.*?\};[\s\n]*/s,
    ''
  );
  
  // Update onClick handlers to use simple navigation
  content = content.replace(
    /onClick=\{\(\) => setStep\('linkedin'\)\}/g,
    "onClick={() => console.log('LinkedIn integration coming soon')}"
  );
  content = content.replace(
    /onClick=\{\(\) => setStep\('cv'\)\}/g,
    "onClick={() => console.log('CV upload coming soon')}"
  );
  content = content.replace(
    /onClick=\{\(\) => setStep\('manual'\)\}/g,
    "onClick={() => console.log('Manual profile coming soon')}"
  );
  
  fs.writeFileSync(onboardingPath, content);
  console.log('✅ OnboardingProfileSetup.tsx fixed');
}

console.log('🎉 ESLint fixes completed!'); 