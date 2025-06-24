const fs = require('fs');
const path = './src/components/AuthModal.tsx';
let content = fs.readFileSync(path, 'utf8');

// Login form input'larına eksik id'leri ekle
content = content.replace(
  /(<input\s+)className="w-full px-3 py-2 border border-gray-300([^>]*>)/g,
  (match, prefix, suffix) => {
    if (!match.includes('id=')) {
      if (match.includes('placeholder="your@email.com"')) {
        return prefix + 'id="loginEmail" ' + match.slice(prefix.length);
      }
      if (match.includes('placeholder="Your password"')) {
        return prefix + 'id="loginPassword" ' + match.slice(prefix.length);
      }
    }
    return match;
  }
);

// Forgot password türkçe -> İngilizce
content = content.replace(
  'Şifremi Unuttum',
  'Forgot Password'
);

// API URL problemi için sync yerine direkt URL kullan
content = content.replace(
  /const API_BASE_URL = await getApiUrl\(\);/g,
  'const API_BASE_URL = "http://localhost:8000/api";'
);

fs.writeFileSync(path, content);
console.log('AuthModal complete fix applied!');
