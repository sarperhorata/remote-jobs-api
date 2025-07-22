// React Autocomplete Debug Script
// Bu script'i browser console'da çalıştırarak autocomplete'i test edebilirsiniz

async function testReactAutocomplete() {
  console.log('🧪 Testing React autocomplete...');
  
  try {
    // API URL'ini al
    const apiUrl = 'http://localhost:8001/api/v1';
    console.log('🔗 API URL:', apiUrl);
    
    // React araması yap
    const response = await fetch(`${apiUrl}/jobs/job-titles/search?q=React&limit=5`);
    console.log('📡 Response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ React search results:', data);
    
    // Sonuçları kontrol et
    if (data && data.length > 0) {
      console.log('🎉 React autocomplete çalışıyor!');
      console.log('📊 Bulunan sonuçlar:');
      data.forEach((item, index) => {
        console.log(`${index + 1}. ${item.title} (${item.count} jobs)`);
      });
    } else {
      console.log('⚠️ React araması sonuç döndürmedi');
    }
    
  } catch (error) {
    console.error('❌ React autocomplete test failed:', error);
  }
}

// Test fonksiyonunu çalıştır
testReactAutocomplete();

// Global olarak erişilebilir yap
window.testReactAutocomplete = testReactAutocomplete; 