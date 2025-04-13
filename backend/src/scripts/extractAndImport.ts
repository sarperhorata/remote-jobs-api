import mongoose from 'mongoose';
import fs from 'fs';
import readline from 'readline';
import Company from '../models/Company';
import Job from '../models/Job';
import { logger } from '../utils/logger';

// Use the working MongoDB URI
const mongoUri = 'mongodb+srv://myremotejobs:cH622T5iGoc9tzfe@remotejobs.tn0gxu0.mongodb.net/remotejobs?retryWrites=true&w=majority&appName=RemoteJobs';

interface ProcessedJob {
  title: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
  location: string;
  companyWebsite: string;
  sourceUrl: string;
  [key: string]: any;
}

/**
 * Main function to extract companies and jobs from export data and import to MongoDB
 */
async function extractAndImport(filePath: string): Promise<void> {
  try {
    // Connect to MongoDB
    await mongoose.connect(mongoUri);
    logger.info('Connected to MongoDB');

    // Get existing companies from the database
    const existingCompanies = await Company.find({}, { website: 1, name: 1 });
    const existingWebsites = new Set(existingCompanies.map(company => company.website));
    const existingNames = new Set(existingCompanies.map(company => company.name));
    
    logger.info(`Found ${existingCompanies.length} existing companies in the database`);

    // Get existing jobs to avoid duplicates
    const existingJobs = await Job.find({}, { title: 1, companyId: 1, sourceUrl: 1 });
    const existingSourceUrls = new Set(existingJobs.map(job => job.sourceUrl));
    
    logger.info(`Found ${existingJobs.length} existing jobs in the database`);

    // Initialize counters
    let totalEntries = 0;
    let processedEntries = 0;
    let duplicateCompanies = 0;
    let newCompanies = 0;
    let newJobs = 0;
    let duplicateJobs = 0;
    let invalidEntries = 0;

    // Create a map to store company ID by website
    const companyMap = new Map();
    existingCompanies.forEach(company => {
      companyMap.set(company.website, company._id);
      
      // Also map domain names for fuzzy matching
      try {
        const domain = new URL(company.website).hostname.replace('www.', '');
        companyMap.set(domain, company._id);
      } catch (e) {
        // Ignore invalid URLs
      }
    });

    // Process the export file line by line
    const fileStream = fs.createReadStream(filePath);
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    let jsonLines: string[] = [];
    
    // Read all lines from file
    for await (const line of rl) {
      jsonLines.push(line);
    }

    // Join lines and try to parse as JSON
    try {
      const jsonData = JSON.parse(jsonLines.join(''));
      logger.info(`Loaded ${jsonData.length} entries from export file`);
      totalEntries = jsonData.length;
      
      // Process each entry
      for (const entry of jsonData) {
        processedEntries++;
        
        if (!entry.name || !entry.uri) {
          invalidEntries++;
          continue;
        }

        // Extract company name and website
        const companyName = extractCompanyName(entry.name);
        const website = extractWebsite(entry.uri);
        
        // Check if company already exists
        let companyId;
        if (existingWebsites.has(website) || existingNames.has(companyName)) {
          duplicateCompanies++;
          // Get existing company ID
          companyId = companyMap.get(website);
          
          if (!companyId) {
            // Try to find by name
            const company = existingCompanies.find(c => c.name === companyName);
            if (company) {
              companyId = company._id;
            }
          }
        } else {
          // Create new company
          const companyData = {
            name: companyName,
            website: website,
            logo: '',
            description: `${companyName} is a company that offers remote jobs.`,
            industry: 'Technology',
            size: 'Unknown',
            location: 'Remote',
            remotePolicy: 'Remote-First',
            benefits: [],
            techStack: [],
            socialLinks: {}
          };
          
          const newCompany = new Company(companyData);
          await newCompany.save();
          newCompanies++;
          
          companyId = newCompany._id;
          companyMap.set(website, companyId);
          existingWebsites.add(website);
          existingNames.add(companyName);
          
          logger.info(`Created new company: ${companyName}`);
        }
        
        // Skip job extraction if we don't have a company ID
        if (!companyId) {
          continue;
        }
        
        // Extract jobs from content
        if (entry.content) {
          const jobListings = extractJobListings(companyName, entry.content, entry.uri);
          
          for (const job of jobListings) {
            // Skip if job already exists by source URL
            if (existingSourceUrls.has(job.sourceUrl)) {
              duplicateJobs++;
              continue;
            }
            
            // Format job for insertion
            const jobData = {
              title: job.title,
              companyId: companyId,
              description: job.description || '',
              requirements: job.requirements || [],
              responsibilities: job.responsibilities || [],
              skills: job.skills || [],
              location: job.location || 'Remote',
              type: job.type || 'Full-time',
              salary: {
                min: job.salaryMin || null,
                max: job.salaryMax || null,
                currency: job.salaryCurrency || 'USD'
              },
              experience: {
                min: job.experienceMin || null,
                max: job.experienceMax || null
              },
              education: job.education || '',
              benefits: job.benefits || [],
              applicationUrl: job.applicationUrl || job.sourceUrl,
              source: 'Crawled',
              sourceUrl: job.sourceUrl,
              status: 'active',
              postedAt: job.postedAt ? new Date(job.postedAt) : new Date(),
              expiresAt: job.expiresAt ? new Date(job.expiresAt) : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days from now
            };
            
            const newJob = new Job(jobData);
            await newJob.save();
            newJobs++;
            
            existingSourceUrls.add(job.sourceUrl);
          }
          
          // Log progress every 10 entries
          if (processedEntries % 10 === 0) {
            logger.info(`Processed ${processedEntries}/${totalEntries} entries`);
          }
        }
      }
      
    } catch (error) {
      logger.error('Error parsing export data:', error);
    }

    // Log final results
    logger.info(`Completed processing ${processedEntries} entries from export data`);
    logger.info(`Found ${duplicateCompanies} duplicate companies`);
    logger.info(`Created ${newCompanies} new companies`);
    logger.info(`Found ${duplicateJobs} duplicate jobs`);
    logger.info(`Created ${newJobs} new jobs`);
    logger.info(`Skipped ${invalidEntries} invalid entries`);

    // Close connection
    await mongoose.connection.close();
    logger.info('MongoDB connection closed');
    
  } catch (error) {
    logger.error('Error in extractAndImport:', error);
    process.exit(1);
  }
}

/**
 * Extract company name from entry name
 */
function extractCompanyName(entryName: string): string {
  // Common patterns in entry names
  if (entryName.includes(' – ')) {
    return entryName.split(' – ')[0].trim();
  }
  
  if (entryName.includes(' | ')) {
    return entryName.split(' | ')[0].trim();
  }
  
  if (entryName.includes(' - ')) {
    return entryName.split(' - ')[0].trim();
  }
  
  // If no pattern matched, return as is
  return entryName;
}

/**
 * Extract website from URI
 */
function extractWebsite(uri: string): string {
  try {
    const url = new URL(uri);
    
    // If it's a job board, try to extract company name from the path
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
    
    // For standard company websites, use the hostname
    return `https://${url.hostname}`;
  } catch (e) {
    // If parsing fails, return the original URI
    return uri;
  }
}

/**
 * Extract job listings from content
 */
function extractJobListings(companyName: string, content: string, sourceUrl: string): ProcessedJob[] {
  const jobs: ProcessedJob[] = [];
  
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
        postedAt: new Date(),
        companyWebsite: extractWebsite(sourceUrl)
      });
    });
    
    return jobs;
  }
  
  // Process each job section
  jobSections.forEach(section => {
    const title = extractTitle(section);
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
      postedAt: new Date(),
      companyWebsite: extractWebsite(sourceUrl)
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
function extractTitle(jobSection: string): string | null {
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

// Check if file path is provided
if (process.argv.length < 3) {
  logger.error('Please provide the path to the export data file');
  logger.info('Usage: npx ts-node src/scripts/extractAndImport.ts <filePath>');
  process.exit(1);
}

const filePath = process.argv[2];

// Run the extract and import function
extractAndImport(filePath)
  .catch(error => {
    logger.error('Error in main process:', error);
    process.exit(1);
  }); 