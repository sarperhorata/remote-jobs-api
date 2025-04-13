import mongoose from 'mongoose';
import fs from 'fs';
import readline from 'readline';
import Company from '../models/Company';
import Job from '../models/Job';
import { logger } from '../utils/logger';
import { createHash } from 'crypto';

// MongoDB URI
const mongoUri = 'mongodb+srv://myremotejobs:cH622T5iGoc9tzfe@remotejobs.tn0gxu0.mongodb.net/remotejobs?retryWrites=true&w=majority&appName=RemoteJobs';

interface ExportData {
  client: {
    local: number;
  };
  data: CompanyData[];
}

interface CompanyData {
  name: string;
  uri: string;
  content?: string;
  config: string;
  tags?: string[];
  content_type: number;
  state: number;
  schedule: string;
  ts: string;
  datasource_id: any;
}

interface ParsedConfig {
  selections?: any[];
  ignoreEmptyText?: boolean;
  includeStyle?: boolean;
  dataAttr?: string;
  regexp?: {
    expr: string;
    flags: string;
  };
  [key: string]: any;
}

/**
 * Main function to extract companies and job listings from export data
 */
async function extractCompaniesAndJobs(filePath: string): Promise<void> {
  try {
    // Connect to MongoDB
    await mongoose.connect(mongoUri);
    logger.info('Connected to MongoDB');

    // Get existing companies to avoid duplicates
    const existingCompanies = await Company.find();
    const existingWebsites = new Set(existingCompanies.map(company => company.website));
    const existingNames = new Set(existingCompanies.map(company => company.name.toLowerCase()));
    
    logger.info(`Found ${existingCompanies.length} existing companies in database`);

    // Get existing jobs to avoid duplicates
    const existingJobs = await Job.find();
    const existingJobsMap = new Map();
    existingJobs.forEach(job => {
      const key = `${job.title}-${job.companyId}`;
      existingJobsMap.set(key, job);
    });

    logger.info(`Found ${existingJobs.length} existing jobs in database`);

    // Read the export file line by line
    const fileStream = fs.createReadStream(filePath, { encoding: 'utf8' });
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    // Read all the content from the file
    const fileContent = await fs.promises.readFile(filePath, 'utf8');
    
    try {
      // Parse the export data
      const exportData: ExportData = JSON.parse(fileContent);
      
      logger.info(`Loaded export data with ${exportData.data.length} entries`);
      
      // Statistics
      let newCompaniesCount = 0;
      let updatedCompaniesCount = 0;
      let skippedCompaniesCount = 0;
      let newJobsCount = 0;
      let updatedJobsCount = 0;
      let skippedJobsCount = 0;
      let failedCompaniesCount = 0;
      let failedJobsCount = 0;
      
      // Process each entry (company)
      for (let i = 0; i < exportData.data.length; i++) {
        const companyData = exportData.data[i];
        
        try {
          // Extract company name and website
          const { name, uri } = companyData;
          
          if (!name || !uri) {
            logger.warn(`Skipping entry #${i} - Missing name or URI`);
            skippedCompaniesCount++;
            continue;
          }
          
          // Clean the company name
          const companyName = cleanCompanyName(name);
          const website = cleanWebsiteURL(uri);
          
          // Check if company already exists
          const companyExists = existingWebsites.has(website) || existingNames.has(companyName.toLowerCase());
          let company;
          
          if (companyExists) {
            // Find the existing company
            company = existingCompanies.find(c => 
              c.website === website || 
              c.name.toLowerCase() === companyName.toLowerCase()
            );
            
            if (company) {
              // Update the company with new information if needed
              let updated = false;
              
              if (company.name !== companyName) {
                company.name = companyName;
                updated = true;
              }
              
              if (company.website !== website) {
                company.website = website;
                updated = true;
              }
              
              // More fields can be updated here if needed
              
              if (updated) {
                await company.save();
                updatedCompaniesCount++;
                logger.info(`Updated company: ${companyName}`);
              } else {
                skippedCompaniesCount++;
              }
            }
          } else {
            // Create a new company
            company = new Company({
              name: companyName,
              website: website,
              logo: '',
              description: `${companyName} is a company that offers remote jobs.`,
              industry: extractIndustry(companyData),
              size: 'Unknown',
              location: 'Remote',
              remotePolicy: 'Remote-First',
              benefits: [],
              techStack: [],
              socialLinks: {}
            });
            
            await company.save();
            newCompaniesCount++;
            
            // Add to existing sets to avoid duplicates within this run
            existingWebsites.add(website);
            existingNames.add(companyName.toLowerCase());
            
            logger.info(`Created new company: ${companyName}`);
          }
          
          // Process job listings from content if available
          if (companyData.content && company) {
            const jobListings = extractJobListings(companyData.content, companyName, website, uri);
            
            // Add each job listing to the database
            for (const jobData of jobListings) {
              try {
                // Create a unique key for this job
                const jobKey = `${jobData.title}-${company._id}`;
                
                // Check if job already exists
                if (existingJobsMap.has(jobKey)) {
                  // Update existing job if needed
                  const existingJob = existingJobsMap.get(jobKey);
                  let jobUpdated = false;
                  
                  // Check for updates - implement this according to your needs
                  // For simplicity, we'll just update the description if it's different
                  if (existingJob.description !== jobData.description) {
                    existingJob.description = jobData.description;
                    jobUpdated = true;
                  }
                  
                  if (jobUpdated) {
                    await existingJob.save();
                    updatedJobsCount++;
                    logger.debug(`Updated job: ${jobData.title} at ${companyName}`);
                  } else {
                    skippedJobsCount++;
                  }
                } else {
                  // Create new job
                  const newJob = new Job({
                    title: jobData.title,
                    companyId: company._id,
                    description: jobData.description,
                    requirements: jobData.requirements,
                    responsibilities: jobData.responsibilities,
                    skills: jobData.skills,
                    location: jobData.location || 'Remote',
                    type: jobData.type || 'Full-time',
                    salary: {
                      min: jobData.salaryMin || null,
                      max: jobData.salaryMax || null,
                      currency: jobData.salaryCurrency || 'USD'
                    },
                    experience: {
                      min: jobData.experienceMin || null,
                      max: jobData.experienceMax || null
                    },
                    education: jobData.education || '',
                    benefits: jobData.benefits || [],
                    applicationUrl: jobData.applicationUrl || uri,
                    source: 'Crawled',
                    sourceUrl: uri,
                    status: 'active',
                    postedAt: new Date(),
                    expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days from now
                  });
                  
                  await newJob.save();
                  newJobsCount++;
                  
                  // Add to existing map to avoid duplicates within this run
                  existingJobsMap.set(jobKey, newJob);
                  
                  logger.debug(`Created new job: ${jobData.title} at ${companyName}`);
                }
              } catch (error) {
                logger.error(`Error processing job ${jobData.title} at ${companyName}:`, error);
                failedJobsCount++;
              }
            }
          }
          
          // Log progress every 10 entries
          if ((i + 1) % 10 === 0) {
            logger.info(`Processed ${i + 1}/${exportData.data.length} companies`);
          }
        } catch (error) {
          logger.error(`Error processing company entry #${i}:`, error);
          failedCompaniesCount++;
        }
      }
      
      // Log final statistics
      logger.info('====== IMPORT COMPLETED ======');
      logger.info(`Total companies in export: ${exportData.data.length}`);
      logger.info(`New companies created: ${newCompaniesCount}`);
      logger.info(`Existing companies updated: ${updatedCompaniesCount}`);
      logger.info(`Companies skipped (no changes): ${skippedCompaniesCount}`);
      logger.info(`Companies failed to process: ${failedCompaniesCount}`);
      logger.info(`New jobs created: ${newJobsCount}`);
      logger.info(`Existing jobs updated: ${updatedJobsCount}`);
      logger.info(`Jobs skipped (no changes): ${skippedJobsCount}`);
      logger.info(`Jobs failed to process: ${failedJobsCount}`);
      
    } catch (error) {
      logger.error('Error parsing export data:', error);
      throw error;
    }
    
    // Close database connection
    await mongoose.connection.close();
    logger.info('MongoDB connection closed');
    
  } catch (error) {
    logger.error('Error in extractCompaniesAndJobs:', error);
    
    // Make sure to close database connection on error
    if (mongoose.connection.readyState === 1) {
      await mongoose.connection.close();
      logger.info('MongoDB connection closed after error');
    }
    
    process.exit(1);
  }
}

/**
 * Clean company name (remove suffixes like "Careers", "Jobs", etc.)
 */
function cleanCompanyName(name: string): string {
  // List of common suffixes to remove
  const suffixes = [
    'Careers', 'Career', 'Jobs', 'Vacancies', 'Openings at', 'Openings', 
    'Job Openings', 'Current Openings', 'Work at', 'Work for', 'Join'
  ];
  
  let cleanName = name.trim();
  
  // Remove suffixes
  for (const suffix of suffixes) {
    const pattern = new RegExp(`\\s*[\\|\\-–]\\s*${suffix}.*$`, 'i');
    cleanName = cleanName.replace(pattern, '');
    
    const prefixPattern = new RegExp(`^${suffix}\\s*[\\|\\-–]\\s*`, 'i');
    cleanName = cleanName.replace(prefixPattern, '');
    
    const simplePattern = new RegExp(`\\s*${suffix}\\s*$`, 'i');
    cleanName = cleanName.replace(simplePattern, '');
  }
  
  return cleanName.trim();
}

/**
 * Clean website URL (normalize format)
 */
function cleanWebsiteURL(uri: string): string {
  try {
    // Parse the URL to get domain
    const url = new URL(uri);
    
    // For job board URLs, try to extract company domain
    if (
      url.hostname.includes('greenhouse.io') ||
      url.hostname.includes('lever.co') ||
      url.hostname.includes('workable.com') ||
      url.hostname.includes('recruitee.com') ||
      url.hostname.includes('ashbyhq.com') ||
      url.hostname.includes('breezy.hr') ||
      url.hostname.includes('applytojob.com')
    ) {
      // For these platforms, the company name is often in the path or subdomain
      const pathSegments = url.pathname.split('/').filter(s => s);
      if (pathSegments.length > 0) {
        const companySlug = pathSegments[0];
        
        // Try to derive a website URL (this is just a guess)
        return `https://${companySlug}.com`;
      }
      
      // If we can't extract from path, try subdomain
      const subdomains = url.hostname.split('.');
      if (subdomains.length > 2 && !subdomains[0].match(/www|jobs|careers|job|career/i)) {
        return `https://${subdomains[0]}.com`;
      }
    }
    
    // For normal URLs, use the hostname with https
    return `https://${url.hostname}`;
  } catch (error) {
    // If URL parsing fails, return the original
    return uri;
  }
}

/**
 * Extract industry from company data
 */
function extractIndustry(companyData: CompanyData): string {
  // Try to extract from tags
  if (companyData.tags && companyData.tags.length > 0) {
    const industryTags = companyData.tags.filter(tag => {
      // List of common industry tags
      const industryKeywords = [
        'tech', 'software', 'finance', 'healthcare', 'education', 
        'ecommerce', 'media', 'marketing', 'design', 'gaming'
      ];
      
      return industryKeywords.some(keyword => 
        tag.toLowerCase().includes(keyword)
      );
    });
    
    if (industryTags.length > 0) {
      return industryTags[0];
    }
  }
  
  // Try to extract from name or URI
  const nameAndUri = `${companyData.name} ${companyData.uri}`.toLowerCase();
  
  if (nameAndUri.includes('tech') || nameAndUri.includes('software') || nameAndUri.includes('dev')) {
    return 'Technology';
  } else if (nameAndUri.includes('finance') || nameAndUri.includes('bank') || nameAndUri.includes('invest')) {
    return 'Finance';
  } else if (nameAndUri.includes('health') || nameAndUri.includes('medical')) {
    return 'Healthcare';
  } else if (nameAndUri.includes('edu') || nameAndUri.includes('learn') || nameAndUri.includes('school')) {
    return 'Education';
  } else if (nameAndUri.includes('commerce') || nameAndUri.includes('shop') || nameAndUri.includes('retail')) {
    return 'Ecommerce';
  } else if (nameAndUri.includes('media') || nameAndUri.includes('news')) {
    return 'Media';
  } else if (nameAndUri.includes('market') || nameAndUri.includes('ads')) {
    return 'Marketing';
  } else if (nameAndUri.includes('design')) {
    return 'Design';
  } else if (nameAndUri.includes('game')) {
    return 'Gaming';
  }
  
  // Default
  return 'Technology';
}

/**
 * Extract job listings from content
 */
function extractJobListings(content: string, companyName: string, companyWebsite: string, sourceUrl: string): any[] {
  const jobs: any[] = [];
  
  try {
    // Some content might be HTML, some might be plain text
    // Here we'll attempt to extract job titles and descriptions using regex patterns
    
    // Clean up the content - replace newlines and extra spaces
    const cleanContent = content
      .replace(/(\r\n|\n|\r)/gm, " ")
      .replace(/\s+/g, " ")
      .trim();
    
    // Patterns to identify job sections
    // This is an initial attempt - you might need to refine based on actual data
    const jobSectionPatterns = [
      // Match job title patterns
      /(Senior|Principal|Lead|Staff)?\s*(Software|Frontend|Backend|Full[-\s]Stack|UI\/UX|DevOps|Product|Project|Data|Cloud|Mobile|iOS|Android|Web|QA|Test)?\s*(Engineer|Developer|Manager|Designer|Analyst|Scientist|Architect|Lead|Director|Specialist)/gi,
      // Job title with location (remote)
      /([A-Z][a-z]+(\s+[A-Z][a-z]+)*)\s*-\s*(Remote|Full[-\s]Time|Part[-\s]Time)/gi,
      // General job title pattern
      /\b([A-Z][a-z]+(\s+[A-Z][a-z]+){1,5})\s*[\-–]\s*(Remote|Full[-\s]Time|Part[-\s]Time)/gi
    ];
    
    let matches: string[] = [];
    
    // Try each pattern to find job titles
    for (const pattern of jobSectionPatterns) {
      const patternMatches = Array.from(cleanContent.matchAll(pattern))
        .map(match => match[0]);
      
      if (patternMatches.length > 0) {
        matches = [...matches, ...patternMatches];
      }
    }
    
    // If we found job titles, create job listings
    if (matches.length > 0) {
      // Remove duplicates
      const uniqueMatches = [...new Set(matches)];
      
      // Create job listings from matches
      for (const title of uniqueMatches) {
        // Generate a simple hash of the title to use as an ID
        const titleHash = createHash('md5').update(title).digest('hex').substring(0, 10);
        
        // Create a job object
        const job = {
          title: title,
          description: `${title} at ${companyName}. This is a job opportunity for a ${title} role at ${companyName}.`,
          requirements: extractRequirements(cleanContent, title),
          responsibilities: extractResponsibilities(cleanContent, title),
          skills: extractSkills(cleanContent),
          location: 'Remote',
          type: extractJobType(title) || 'Full-time',
          salaryMin: null,
          salaryMax: null,
          salaryCurrency: 'USD',
          experienceMin: null,
          experienceMax: null,
          education: '',
          benefits: [],
          applicationUrl: sourceUrl,
          sourceUrl: sourceUrl,
          companyWebsite: companyWebsite
        };
        
        jobs.push(job);
      }
    } else {
      // If no specific job titles were found, create a generic job listing
      const job = {
        title: `Remote Position at ${companyName}`,
        description: `Work remotely for ${companyName}. This is a job opportunity at ${companyName}.`,
        requirements: [],
        responsibilities: [],
        skills: extractSkills(cleanContent),
        location: 'Remote',
        type: 'Full-time',
        salaryMin: null,
        salaryMax: null,
        salaryCurrency: 'USD',
        experienceMin: null,
        experienceMax: null,
        education: '',
        benefits: [],
        applicationUrl: sourceUrl,
        sourceUrl: sourceUrl,
        companyWebsite: companyWebsite
      };
      
      jobs.push(job);
    }
  } catch (error) {
    logger.error(`Error extracting job listings for ${companyName}:`, error);
  }
  
  return jobs;
}

/**
 * Extract requirements from content
 */
function extractRequirements(content: string, jobTitle: string): string[] {
  const requirements: string[] = [];
  
  try {
    // Look for requirements section
    const reqSection = content.match(/requirements:(.+?)(?:responsibilities|qualifications|what you'll do|we offer|about you|apply now|$)/is);
    
    if (reqSection && reqSection[1]) {
      // Extract bullet points (often indicated by •, -, *, or numbers)
      const bulletPoints = reqSection[1].match(/(?:•|\*|\-|\d+\.)\s*([^•\*\-\d\.]+)/g);
      
      if (bulletPoints) {
        bulletPoints.forEach(point => {
          const cleanPoint = point
            .replace(/^(?:•|\*|\-|\d+\.)\s*/, '') // Remove bullet indicators
            .trim();
          
          if (cleanPoint) {
            requirements.push(cleanPoint);
          }
        });
      }
    }
    
    // If no requirements found but we have a job title, add some generic requirements based on the job title
    if (requirements.length === 0 && jobTitle) {
      // Extract role from job title
      const role = jobTitle.toLowerCase();
      
      if (role.includes('engineer') || role.includes('developer')) {
        requirements.push('Experience with software development and coding');
        requirements.push('Problem-solving skills and attention to detail');
        requirements.push('Ability to work in a remote team environment');
      } else if (role.includes('design')) {
        requirements.push('Portfolio showcasing design work');
        requirements.push('Experience with design tools and processes');
        requirements.push('Strong visual and creative skills');
      } else if (role.includes('product')) {
        requirements.push('Experience in product management or development');
        requirements.push('Strong communication and collaboration skills');
        requirements.push('Ability to prioritize and manage product roadmap');
      } else if (role.includes('manager')) {
        requirements.push('Leadership experience and team management skills');
        requirements.push('Strong communication and organizational abilities');
        requirements.push('Problem-solving and decision-making skills');
      } else {
        requirements.push('Relevant experience in the field');
        requirements.push('Strong communication skills');
        requirements.push('Ability to work remotely and independently');
      }
    }
  } catch (error) {
    logger.error('Error extracting requirements:', error);
  }
  
  return requirements;
}

/**
 * Extract responsibilities from content
 */
function extractResponsibilities(content: string, jobTitle: string): string[] {
  const responsibilities: string[] = [];
  
  try {
    // Look for responsibilities section
    const respSection = content.match(/responsibilities:(.+?)(?:requirements|qualifications|what we're looking for|about you|we offer|benefits|apply now|$)/is);
    
    if (respSection && respSection[1]) {
      // Extract bullet points (often indicated by •, -, *, or numbers)
      const bulletPoints = respSection[1].match(/(?:•|\*|\-|\d+\.)\s*([^•\*\-\d\.]+)/g);
      
      if (bulletPoints) {
        bulletPoints.forEach(point => {
          const cleanPoint = point
            .replace(/^(?:•|\*|\-|\d+\.)\s*/, '') // Remove bullet indicators
            .trim();
          
          if (cleanPoint) {
            responsibilities.push(cleanPoint);
          }
        });
      }
    }
    
    // If no responsibilities found but we have a job title, add some generic responsibilities based on the job title
    if (responsibilities.length === 0 && jobTitle) {
      // Extract role from job title
      const role = jobTitle.toLowerCase();
      
      if (role.includes('engineer') || role.includes('developer')) {
        responsibilities.push('Develop and maintain software applications');
        responsibilities.push('Collaborate with team members on technical solutions');
        responsibilities.push('Troubleshoot and debug issues as they arise');
      } else if (role.includes('design')) {
        responsibilities.push('Create visual designs for products or features');
        responsibilities.push('Collaborate with product and engineering teams');
        responsibilities.push('Maintain design systems and documentation');
      } else if (role.includes('product')) {
        responsibilities.push('Define product requirements and specifications');
        responsibilities.push('Work with design and engineering teams on implementation');
        responsibilities.push('Gather and analyze user feedback for product improvements');
      } else if (role.includes('manager')) {
        responsibilities.push('Lead and manage team members');
        responsibilities.push('Set goals and track progress');
        responsibilities.push('Communicate with stakeholders and other teams');
      } else {
        responsibilities.push('Contribute to team goals and objectives');
        responsibilities.push('Collaborate with team members across the company');
        responsibilities.push('Maintain documentation and reporting as required');
      }
    }
  } catch (error) {
    logger.error('Error extracting responsibilities:', error);
  }
  
  return responsibilities;
}

/**
 * Extract skills from content
 */
function extractSkills(content: string): string[] {
  const skills = new Set<string>();
  
  try {
    // List of common tech skills to look for
    const skillsToCheck = [
      // Programming languages
      'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go',
      // Frontend frameworks/libraries
      'React', 'Angular', 'Vue', 'Svelte', 'jQuery', 'HTML', 'CSS', 'SASS', 'LESS', 'Tailwind', 'Bootstrap',
      // Backend frameworks
      'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'ASP.NET', 'Laravel', 'Rails',
      // Databases
      'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB', 'Cassandra', 'SQLite',
      // Cloud platforms
      'AWS', 'Azure', 'GCP', 'Google Cloud', 'Heroku', 'DigitalOcean', 'Vercel', 'Netlify',
      // DevOps
      'Docker', 'Kubernetes', 'Jenkins', 'Travis CI', 'CircleCI', 'GitHub Actions', 'Terraform', 'Ansible',
      // Version control
      'Git', 'GitHub', 'GitLab', 'Bitbucket',
      // API technologies
      'REST', 'GraphQL', 'gRPC', 'WebSockets', 'API',
      // Architecture
      'Microservices', 'Serverless', 'Monolith',
      // Methodologies
      'CI/CD', 'DevOps', 'Agile', 'Scrum', 'Kanban', 'TDD', 'BDD',
      // Design
      'UI', 'UX', 'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator',
      // Product management
      'Jira', 'Trello', 'Asana', 'Notion', 'Confluence', 'Product Management', 'Roadmapping'
    ];
    
    // Check for each skill in the content
    for (const skill of skillsToCheck) {
      const regex = new RegExp(`\\b${skill}\\b`, 'i');
      if (regex.test(content)) {
        skills.add(skill);
      }
    }
  } catch (error) {
    logger.error('Error extracting skills:', error);
  }
  
  return Array.from(skills);
}

/**
 * Extract job type from title
 */
function extractJobType(title: string): string | null {
  try {
    const lowercaseTitle = title.toLowerCase();
    
    if (lowercaseTitle.includes('full-time') || lowercaseTitle.includes('full time')) {
      return 'Full-time';
    } else if (lowercaseTitle.includes('part-time') || lowercaseTitle.includes('part time')) {
      return 'Part-time';
    } else if (lowercaseTitle.includes('contract')) {
      return 'Contract';
    } else if (lowercaseTitle.includes('freelance')) {
      return 'Freelance';
    } else if (lowercaseTitle.includes('intern') || lowercaseTitle.includes('internship')) {
      return 'Internship';
    }
  } catch (error) {
    logger.error('Error extracting job type:', error);
  }
  
  return null;
}

// Check if file path is provided
if (process.argv.length < 3) {
  logger.error('Please provide the path to the export data file');
  logger.info('Usage: npx ts-node src/scripts/extractCompaniesAndJobs.ts <filePath>');
  process.exit(1);
}

const filePath = process.argv[2];

// Run the extract and import function
extractCompaniesAndJobs(filePath)
  .then(() => {
    logger.info('Process completed successfully');
    process.exit(0);
  })
  .catch(error => {
    logger.error('Process failed:', error);
    process.exit(1);
  }); 