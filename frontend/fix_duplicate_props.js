const fs = require('fs');
const path = './src/components/AuthModal.tsx';
let content = fs.readFileSync(path, 'utf8');

// Fix duplicate id="loginEmail" 
content = content.replace(
  /id="loginEmail"\s+id="loginEmail" type="email" required value={loginEmail}/,
  'type="email" required value={loginEmail}'
);

// Fix duplicate id="loginPassword"
content = content.replace(
  /id="loginPassword"\s+id="loginPassword" type={showPassword \? 'text' : 'password'} required value={loginPassword}/,
  'type={showPassword ? \'text\' : \'password\'} required value={loginPassword}'
);

// Fix wrong htmlFor for register email (should be registerEmail, not loginEmail)
content = content.replace(
  /<label htmlFor="loginEmail" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\s*Email Adresi/,
  '<label htmlFor="registerEmail" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\n                  Email Adresi'
);

fs.writeFileSync(path, content);
console.log('Duplicate props fixed!');
