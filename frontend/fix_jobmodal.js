const fs = require('fs');
const path = './src/components/JobSearch/JobApplicationModal.tsx';
let content = fs.readFileSync(path, 'utf8');

// Fix dynamic field labels to include htmlFor
content = content.replace(
  /<label className="block text-sm font-medium text-gray-700 mb-2">/g,
  '<label htmlFor={field.id} className="block text-sm font-medium text-gray-700 mb-2">'
);

// Fix textarea to include id
content = content.replace(
  /<textarea\s+value=/g,
  '<textarea id={field.id} value='
);

// Fix select to include id  
content = content.replace(
  /<select\s+value=/g,
  '<select id={field.id} value='
);

// Fix input file to include id
content = content.replace(
  /<input\s+type="file"/g,
  '<input id={field.id} type="file"'
);

// Fix regular input to include id
content = content.replace(
  /<input\s+type={field\.type}/g,
  '<input id={field.id} type={field.type}'
);

fs.writeFileSync(path, content);
console.log('JobApplicationModal fixed!');
