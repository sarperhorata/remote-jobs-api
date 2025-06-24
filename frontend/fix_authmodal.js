const fs = require('fs');
const path = './src/components/AuthModal.tsx';
let content = fs.readFileSync(path, 'utf8');

// Fix login email
content = content.replace(
  /<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\s*Email Address\s*<\/label>/,
  '<label htmlFor="loginEmail" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\n                  Email Address\n                </label>'
);

content = content.replace(
  /type="email"\s+required\s+value={loginEmail}/,
  'id="loginEmail" type="email" required value={loginEmail}'
);

// Fix login password  
content = content.replace(
  /<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\s*Password\s*<\/label>/,
  '<label htmlFor="loginPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\n                  Password\n                </label>'
);

content = content.replace(
  /type={showPassword \? 'text' : 'password'}\s+required\s+value={loginPassword}/,
  'id="loginPassword" type={showPassword ? \'text\' : \'password\'} required value={loginPassword}'
);

// Fix register email
content = content.replace(
  /<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\s*Email Adresi\s*<\/label>/,
  '<label htmlFor="registerEmail" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\n                  Email Adresi\n                </label>'
);

content = content.replace(
  /type="email"\s+required\s+value={registerEmail}/,
  'id="registerEmail" type="email" required value={registerEmail}'
);

fs.writeFileSync(path, content);
console.log('AuthModal fixed!');
