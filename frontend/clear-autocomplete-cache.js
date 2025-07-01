// Autocomplete Cache Clear & Debug Script
// Browser console'da çalıştır: copy(autocompleteFixScript) sonra paste et

const autocompleteFixScript = `
// 1. Cache'i temizle
console.log('🧹 Clearing all API caches...');
if (window.localStorage) {
  Object.keys(localStorage).forEach(key => {
    if (key.includes('api') || key.includes('url') || key.includes('cache')) {
      localStorage.removeItem(key);
      console.log('Removed cache key:', key);
    }
  });
}

// 2. Service Worker'ları temizle
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(registration => registration.unregister());
    console.log('Service workers cleared');
  });
}

// 3. API URL'i manuel test et
async function testAutocompleteAPI() {
  console.log('🔍 Testing autocomplete API...');
  
  const testUrls = [
    'http://localhost:8001/api/v1/jobs/job-titles/search?q=dev&limit=3',
    'http://localhost:8002/api/v1/jobs/job-titles/search?q=dev&limit=3',
    'http://localhost:8000/api/v1/jobs/job-titles/search?q=dev&limit=3'
  ];
  
  for (const url of testUrls) {
    try {
      console.log('Testing URL:', url);
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Working API found:', url);
        console.log('Sample data:', data);
        
        // Force update API config
        if (window.clearApiUrlCache) {
          window.clearApiUrlCache();
        }
        
        return url.replace('/jobs/job-titles/search?q=dev&limit=3', '');
      }
    } catch (error) {
      console.log('❌ URL failed:', url, error.message);
    }
  }
  
  console.log('❌ No working API URL found');
  return null;
}

// 4. Autocomplete input'ları test et
function testAutocompleteInputs() {
  console.log('🔍 Testing autocomplete inputs...');
  
  const autocompleteInputs = document.querySelectorAll('input[placeholder*="job"]');
  console.log('Found inputs:', autocompleteInputs.length);
  
  autocompleteInputs.forEach((input, index) => {
    console.log(\`Input \${index + 1}:\`, input.placeholder);
    
    // Trigger events
    input.focus();
    input.value = 'developer';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    setTimeout(() => {
      console.log(\`Input \${index + 1} dropdown check - elements with role="option":\`, 
        document.querySelectorAll('[role="option"], .dropdown, .suggestions').length);
    }, 1000);
  });
}

// 5. Page reload with fresh cache
function freshReload() {
  console.log('🔄 Performing fresh reload...');
  setTimeout(() => {
    window.location.reload(true);
  }, 1000);
}

// Ana test fonksiyonu
async function runAutocompleteDebug() {
  console.log('🚀 Running autocomplete debug...');
  
  const workingAPI = await testAutocompleteAPI();
  if (workingAPI) {
    console.log('💡 Working API URL found:', workingAPI);
  }
  
  testAutocompleteInputs();
  
  console.log('✅ Debug complete. Check for dropdown elements or run freshReload() if needed.');
}

// Test'i çalıştır
runAutocompleteDebug();
`;

// Script'i global scope'a koy
window.autocompleteFixScript = autocompleteFixScript;

console.log('🔧 Autocomplete fix script loaded. Copy the script below and paste in browser console:');
console.log(autocompleteFixScript); 