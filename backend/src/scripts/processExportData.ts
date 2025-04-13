import fs from 'fs';
import { logger } from '../utils/logger';

interface JobListing {
  title: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
  location: string;
  type: string;
  skills: string[];
  source: string;
  sourceUrl: string;
  applicationUrl: string;
  postedAt: Date;
  companyWebsite?: string;
}

/**
 * Process crawled export data and convert it to the format required by importJobs.ts
 * @param inputFilePath Path to the crawled export data JSON file
 * @param outputFilePath Path to save the processed data for job import
 */
async function processExportData(inputFilePath: string, outputFilePath: string): Promise<void> {
  try {
    // Read the export file
    const rawData = fs.readFileSync(inputFilePath, 'utf8');
    const exportData = JSON.parse(rawData);
    
    logger.info(`Loaded export data with ${exportData.length} entries`);
    
    // Array to store processed job data
    const processedJobs: JobListing[] = [];
    
    // Process each entry in the export data
    for (const entry of exportData) {
      // Skip entries without name, URI, or content
      if (!entry.name || !entry.uri || !entry.content) {
        continue;
      }
      
      // Extract company name from the entry name or URI
      const companyName = extractCompanyName(entry.name, entry.uri);
      let companyWebsite = extractCompanyWebsite(entry.uri);
      
      // Process the content to extract job listings
      const jobListings = extractJobListings(companyName, entry.content, entry.uri);
      
      // Add processed job listings to the result array
      if (jobListings.length > 0) {
        logger.info(`Extracted ${jobListings.length} job listings from ${companyName}`);
        jobListings.forEach(job => {
          job.companyWebsite = companyWebsite;
          processedJobs.push(job);
        });
      }
    }
    
    logger.info(`Total processed jobs: ${processedJobs.length}`);
    
    // Write the processed data to output file
    fs.writeFileSync(outputFilePath, JSON.stringify(processedJobs, null, 2));
    logger.info(`Processed data saved to ${outputFilePath}`);
    
  } catch (error) {
    logger.error('Error processing export data:', error);
    process.exit(1);
  }
}

/**
 * Extract company name from entry name or URI
 */
function extractCompanyName(entryName: string, uri: string): string {
  // First try from entry name
  if (entryName.includes(' – ')) {
    return entryName.split(' – ')[0].trim();
  }
  
  if (entryName.includes(' | ')) {
    return entryName.split(' | ')[0].trim();
  }
  
  if (entryName.includes(' - ')) {
    return entryName.split(' - ')[0].trim();
  }
  
  // If entry name doesn't have company name, try extracting from URI
  try {
    const url = new URL(uri);
    const domain = url.hostname.replace('www.', '');
    return domain.split('.')[0].charAt(0).toUpperCase() + domain.split('.')[0].slice(1);
  } catch (e) {
    // Return entry name as fallback
    return entryName;
  }
}

/**
 * Extract company website from URI
 */
function extractCompanyWebsite(uri: string): string {
  try {
    const url = new URL(uri);
    // If it's a job board, try to get the main company domain
    if (url.hostname.includes('greenhouse.io') || 
        url.hostname.includes('lever.co') || 
        url.hostname.includes('workable.com') ||
        url.hostname.includes('recruitee.com') ||
        url.hostname.includes('applytojob.com') ||
        url.hostname.includes('breezy.hr') ||
        url.hostname.includes('ashbyhq.com')) {
      
      // Extract from pathname segments
      const pathSegments = url.pathname.split('/').filter(s => s);
      if (pathSegments.length > 0) {
        return `https://${pathSegments[0]}.com`;
      }
    }
    
    // Default to the main domain
    return `https://${url.hostname}`;
  } catch (e) {
    return uri;
  }
}

/**
 * Extract job listings from content
 */
function extractJobListings(companyName: string, content: string, sourceUrl: string): JobListing[] {
  const jobs: JobListing[] = [];
  
  // Clean up the content - replace newlines and extra spaces
  const cleanContent = content.replace(/(\r\n|\n|\r)/gm, " ").replace(/\s+/g, " ");
  
  // Try to identify job sections or listings
  const jobSections = splitIntoJobSections(cleanContent);
  
  if (jobSections.length === 0) {
    // Try alternative approach - look for job titles
    const jobTitles = extractJobTitles(cleanContent);
    
    jobTitles.forEach(title => {
      jobs.push({
        title: title,
        description: `Job opening for ${title} at ${companyName}`,
        requirements: [],
        responsibilities: [],
        skills: [],
        source: 'Crawled',
        sourceUrl: sourceUrl,
        location: 'Remote',
        type: 'Full-time',
        applicationUrl: sourceUrl,
        postedAt: new Date()
      });
    });
    
    return jobs;
  }
  
  // Process each job section
  jobSections.forEach(section => {
    const title = extractTitle(section, companyName);
    if (!title) return;
    
    jobs.push({
      title: title,
      description: section.substring(0, 1000), // First 1000 chars as description
      requirements: extractRequirements(section),
      responsibilities: extractResponsibilities(section),
      location: extractLocation(section) || 'Remote',
      type: extractJobType(section) || 'Full-time',
      skills: extractSkills(section),
      source: 'Crawled',
      sourceUrl: sourceUrl,
      applicationUrl: extractApplicationUrl(section, sourceUrl),
      postedAt: new Date()
    });
  });
  
  return jobs;
}

/**
 * Split content into job sections
 */
function splitIntoJobSections(content: string): string[] {
  // Common job title patterns
  const jobTitlePatterns = [
    /\b(Senior|Junior|Lead|Principal|Staff)?\s?([A-Z][a-z]+\s?)+\b(Engineer|Developer|Manager|Designer|Analyst|Specialist|Architect|Consultant|Director)\b/g,
    /\b(Software|Product|Project|UX|UI|Web|Mobile|Frontend|Backend|Full[-\s]Stack|DevOps|QA|Data)\s(Engineer|Developer|Manager|Designer|Analyst|Specialist|Architect)\b/g
  ];
  
  // Try to find job titles and split the content at these points
  let splitPoints: number[] = [];
  
  jobTitlePatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      // Only use as split if it looks like a title (preceded by newline, bullet point or nothing)
      const precedingChar = content.charAt(match.index - 1) || '';
      if (precedingChar === '' || precedingChar === '\n' || precedingChar === '•' || precedingChar === '-' || precedingChar === '*' || precedingChar === ',') {
        splitPoints.push(match.index);
      }
    }
  });
  
  // If we found potential split points, split the content
  if (splitPoints.length > 0) {
    splitPoints.sort((a, b) => a - b);
    
    const sections = [];
    for (let i = 0; i < splitPoints.length; i++) {
      const start = splitPoints[i];
      const end = i < splitPoints.length - 1 ? splitPoints[i + 1] : content.length;
      sections.push(content.substring(start, end).trim());
    }
    
    return sections;
  }
  
  // If we couldn't split by job titles, try other delimiters
  const delimiters = ['---', '***', '•••', '___', '\n\n', '\r\n\r\n'];
  
  for (const delimiter of delimiters) {
    if (content.includes(delimiter)) {
      return content.split(delimiter).map(s => s.trim()).filter(s => s);
    }
  }
  
  // If all else fails, return the full content as one section
  return [content];
}

/**
 * Extract job titles from content
 */
function extractJobTitles(content: string): string[] {
  const jobTitles: string[] = [];
  
  // Common job title patterns
  const jobTitlePatterns = [
    /\b(Senior|Junior|Lead|Principal|Staff)?\s?([A-Z][a-z]+\s?)+\b(Engineer|Developer|Manager|Designer|Analyst|Specialist|Architect|Consultant|Director)\b/g,
    /\b(Software|Product|Project|UX|UI|Web|Mobile|Frontend|Backend|Full[-\s]Stack|DevOps|QA|Data)\s(Engineer|Developer|Manager|Designer|Analyst|Specialist|Architect)\b/g
  ];
  
  jobTitlePatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      jobTitles.push(match[0]);
    }
  });
  
  return [...new Set(jobTitles)]; // Remove duplicates
}

/**
 * Extract title from job section
 */
function extractTitle(jobSection: string, _companyName: string): string | null {
  // Look for a job title at the beginning of the section
  const firstLine = jobSection.split('.')[0].trim();
  
  // If the first line looks like a job title, use it
  if (firstLine.length < 100 && 
      !/^(About|we are looking|apply|join|click|view|email)/i.test(firstLine) &&
      !firstLine.includes('http')) {
    return firstLine;
  }
  
  // Try common job title patterns
  const jobTitlePatterns = [
    /\b(Senior|Junior|Lead|Principal|Staff)?\s?([A-Z][a-z]+\s?)+\b(Engineer|Developer|Manager|Designer|Analyst|Specialist|Architect|Consultant|Director)\b/,
    /\b(Software|Product|Project|UX|UI|Web|Mobile|Frontend|Backend|Full[-\s]Stack|DevOps|QA|Data)\s(Engineer|Developer|Manager|Designer|Analyst|Specialist|Architect)\b/
  ];
  
  for (const pattern of jobTitlePatterns) {
    const match = jobSection.match(pattern);
    if (match) {
      return match[0];
    }
  }
  
  return null;
}

/**
 * Extract requirements from job section
 */
function extractRequirements(jobSection: string): string[] {
  const requirements: string[] = [];
  
  // Look for a requirements section
  const requirementsPatterns = [
    /requirements:(.+?)(?:responsibilities|qualifications|what you'll do|about you|we offer|benefits|apply now|$)/is,
    /qualifications:(.+?)(?:responsibilities|requirements|what you'll do|about you|we offer|benefits|apply now|$)/is,
    /what we're looking for:(.+?)(?:responsibilities|requirements|qualifications|what you'll do|we offer|benefits|apply now|$)/is,
    /about you:(.+?)(?:responsibilities|requirements|qualifications|what you'll do|what we offer|benefits|apply now|$)/is
  ];
  
  for (const pattern of requirementsPatterns) {
    const match = jobSection.match(pattern);
    if (match && match[1]) {
      // Extract bullet points or numbered items
      const bulletPattern = /(?:•|\*|\-|\d+\.)\s*([^•\*\-\d]+)/g;
      let bulletMatch;
      while ((bulletMatch = bulletPattern.exec(match[1])) !== null) {
        if (bulletMatch[1].trim()) {
          requirements.push(bulletMatch[1].trim());
        }
      }
      
      // If no bullet points found, use the whole section
      if (requirements.length === 0) {
        requirements.push(match[1].trim());
      }
      
      break;
    }
  }
  
  return requirements;
}

/**
 * Extract responsibilities from job section
 */
function extractResponsibilities(jobSection: string): string[] {
  const responsibilities: string[] = [];
  
  // Look for a responsibilities section
  const responsibilitiesPatterns = [
    /responsibilities:(.+?)(?:requirements|qualifications|what we're looking for|about you|we offer|benefits|apply now|$)/is,
    /what you'll do:(.+?)(?:requirements|qualifications|what we're looking for|about you|we offer|benefits|apply now|$)/is,
    /the role:(.+?)(?:requirements|qualifications|what we're looking for|about you|we offer|benefits|apply now|$)/is,
    /job description:(.+?)(?:requirements|qualifications|what we're looking for|about you|we offer|benefits|apply now|$)/is
  ];
  
  for (const pattern of responsibilitiesPatterns) {
    const match = jobSection.match(pattern);
    if (match && match[1]) {
      // Extract bullet points or numbered items
      const bulletPattern = /(?:•|\*|\-|\d+\.)\s*([^•\*\-\d]+)/g;
      let bulletMatch;
      while ((bulletMatch = bulletPattern.exec(match[1])) !== null) {
        if (bulletMatch[1].trim()) {
          responsibilities.push(bulletMatch[1].trim());
        }
      }
      
      // If no bullet points found, use the whole section
      if (responsibilities.length === 0) {
        responsibilities.push(match[1].trim());
      }
      
      break;
    }
  }
  
  return responsibilities;
}

/**
 * Extract location from job section
 */
function extractLocation(jobSection: string): string | null {
  // Look for common location patterns
  const locationPatterns = [
    /location:?\s*([^,\.\n]+)/i,
    /location\/remote:?\s*([^,\.\n]+)/i,
    /\b(remote|worldwide|anywhere)\b/i,
    /\b(new york|san francisco|london|berlin|paris|tokyo|singapore|toronto|sydney)\b/i
  ];
  
  for (const pattern of locationPatterns) {
    const match = jobSection.match(pattern);
    if (match) {
      if (match[1]) {
        return match[1].trim();
      } else if (match[0].toLowerCase() === 'remote' || match[0].toLowerCase() === 'worldwide' || match[0].toLowerCase() === 'anywhere') {
        return 'Remote';
      } else {
        return match[0].trim();
      }
    }
  }
  
  return null;
}

/**
 * Extract job type from job section
 */
function extractJobType(jobSection: string): string | null {
  // Look for common job type patterns
  const jobTypePatterns = [
    /\b(full[ -]time|part[ -]time|contract|freelance|internship)\b/i,
    /job type:?\s*([^,\.\n]+)/i,
    /employment type:?\s*([^,\.\n]+)/i
  ];
  
  for (const pattern of jobTypePatterns) {
    const match = jobSection.match(pattern);
    if (match) {
      if (match[1]) {
        return match[1].trim();
      } else {
        return match[0].trim();
      }
    }
  }
  
  return null;
}

/**
 * Extract skills from job section
 */
function extractSkills(jobSection: string): string[] {
  // Common tech skills to look for
  const skillsSet = new Set([
    'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 'Ruby', 'PHP', 'Swift', 'Kotlin',
    'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'ASP.NET',
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB',
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab',
    'REST', 'GraphQL', 'gRPC', 'API', 'Microservices', 'CI/CD', 'DevOps', 'Agile', 'Scrum'
  ]);
  
  const skills: string[] = [];
  
  // Look for skill mentions
  skillsSet.forEach(skill => {
    const regex = new RegExp(`\\b${skill}\\b`, 'i');
    if (regex.test(jobSection)) {
      skills.push(skill);
    }
  });
  
  return skills;
}

/**
 * Extract application URL from job section
 */
function extractApplicationUrl(jobSection: string, sourceUrl: string): string {
  // Look for application URL
  const urlPattern = /(https?:\/\/[^\s"']+)/g;
  const urls: string[] = [];
  
  let match;
  while ((match = urlPattern.exec(jobSection)) !== null) {
    urls.push(match[1]);
  }
  
  // Try to find an application URL
  for (const url of urls) {
    if (url.includes('apply') || url.includes('job') || url.includes('career') || url.includes('position')) {
      return url;
    }
  }
  
  // If no application URL found, use the source URL
  return sourceUrl;
}

// Check if file paths are provided
if (process.argv.length < 4) {
  logger.error('Please provide paths for both input and output files');
  logger.info('Usage: npx ts-node src/scripts/processExportData.ts <inputFilePath> <outputFilePath>');
  process.exit(1);
}

const inputFilePath = process.argv[2];
const outputFilePath = process.argv[3];

// Run the processing function
processExportData(inputFilePath, outputFilePath)
  .catch(error => {
    logger.error('Error in main process:', error);
    process.exit(1);
  }); 