#!/usr/bin/env node

// Debug script for autocomplete API testing
// Usage: node debug-autocomplete.js

const https = require('http');

console.log('🔍 Testing Autocomplete API...\n');

// Test the statistics endpoint
const options = {
  hostname: 'localhost',
  port: 8001,
  path: '/api/jobs/statistics',
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
};

const req = https.request(options, (res) => {
  console.log(`📊 Status: ${res.statusCode}`);
  console.log(`📋 Headers:`, res.headers);
  
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    try {
      const parsed = JSON.parse(data);
      console.log('\n✅ Response received:');
      console.log(`📈 Total jobs: ${parsed.total_jobs || 'N/A'}`);
      console.log(`🏢 Companies: ${parsed.jobs_by_company?.length || 'N/A'}`);
      console.log(`📍 Locations: ${parsed.jobs_by_location?.length || 'N/A'}`);
      console.log(`💼 Positions: ${parsed.positions?.length || 'N/A'}`);
      
      if (parsed.positions && parsed.positions.length > 0) {
        console.log('\n🎯 Sample positions:');
        parsed.positions.slice(0, 5).forEach((pos, i) => {
          console.log(`   ${i + 1}. ${pos.title} (${pos.count} jobs)`);
        });
        console.log('\n✅ Autocomplete data is available!');
      } else {
        console.log('\n❌ No positions data found - autocomplete will use fallback');
      }
      
      console.log('\n📋 Full response structure:');
      console.log(JSON.stringify(parsed, null, 2));
      
    } catch (error) {
      console.error('❌ Failed to parse JSON:', error.message);
      console.log('Raw response:', data);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request failed:', error.message);
  console.log('\n🔧 Troubleshooting:');
  console.log('   1. Make sure backend is running: uvicorn main:app --reload --host 0.0.0.0 --port 8001');
  console.log('   2. Check if port 8001 is accessible');
  console.log('   3. Verify backend logs for errors');
});

req.on('timeout', () => {
  console.error('❌ Request timed out');
  req.destroy();
});

// Set timeout
req.setTimeout(5000);

req.end();

console.log('🌐 Making request to http://localhost:8001/api/jobs/statistics...'); 