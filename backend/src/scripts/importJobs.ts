import mongoose from 'mongoose';
import fs from 'fs';
import Job from '../models/Job';
import Company from '../models/Company';
import { logger } from '../utils/logger';

// Use the working MongoDB URI
const mongoUri = 'mongodb+srv://myremotejobs:cH622T5iGoc9tzfe@remotejobs.tn0gxu0.mongodb.net/remotejobs?retryWrites=true&w=majority&appName=RemoteJobs';

/**
 * Import jobs from a JSON file and add them to the database
 * @param filePath Path to the JSON file containing jobs
 */
async function importJobs(filePath: string) {
  try {
    // Connect to MongoDB
    await mongoose.connect(mongoUri);
    logger.info('Connected to MongoDB');

    // Read the JSON file
    const jsonData = fs.readFileSync(filePath, 'utf8');
    const importedJobs = JSON.parse(jsonData);
    
    logger.info(`Loaded ${importedJobs.length} jobs from file`);

    // Get existing companies for mapping
    const companies = await Company.find({});
    logger.info(`Found ${companies.length} companies in the database`);

    // Create map of company website to ID for faster lookups
    const companyMap = new Map();
    companies.forEach(company => {
      companyMap.set(company.website, company._id);
      
      // Also map domain names for fuzzy matching
      try {
        const domain = new URL(company.website).hostname.replace('www.', '');
        companyMap.set(domain, company._id);
      } catch (e) {
        // Ignore invalid URLs
      }
    });

    // Get existing jobs to avoid duplicates
    const existingJobs = await Job.find({}, { title: 1, companyId: 1, sourceUrl: 1 });
    logger.info(`Found ${existingJobs.length} existing jobs in the database`);

    // Create sets for duplicate checking
    const existingSourceUrls = new Set(existingJobs.map(job => job.sourceUrl));
    
    // Process and prepare jobs for import
    const jobsToProcess = [];
    
    for (const job of importedJobs) {
      // Skip if job already exists by source URL
      if (existingSourceUrls.has(job.sourceUrl)) {
        continue;
      }
      
      // Find company ID for this job
      let companyId = null;
      
      // Direct match by company website if available
      if (job.companyWebsite && companyMap.has(job.companyWebsite)) {
        companyId = companyMap.get(job.companyWebsite);
      } 
      // Try to match by source URL domain
      else if (job.sourceUrl) {
        try {
          const domain = new URL(job.sourceUrl).hostname.replace('www.', '');
          if (companyMap.has(domain)) {
            companyId = companyMap.get(domain);
          }
        } catch (e) {
          // Ignore invalid URLs
        }
      }
      
      // Skip jobs that can't be associated with a company
      if (!companyId) {
        logger.warn(`Could not find company for job: ${job.title}, source: ${job.sourceUrl}`);
        continue;
      }
      
      // Format job for insertion
      jobsToProcess.push({
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
        source: job.source || 'Crawled',
        sourceUrl: job.sourceUrl,
        status: 'active',
        postedAt: job.postedAt ? new Date(job.postedAt) : new Date(),
        expiresAt: job.expiresAt ? new Date(job.expiresAt) : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days from now
      });
    }
    
    logger.info(`Found ${importedJobs.length - jobsToProcess.length} duplicate or invalid jobs`);
    logger.info(`Preparing to import ${jobsToProcess.length} new jobs`);

    // Insert jobs if any
    if (jobsToProcess.length > 0) {
      const insertedJobs = await Job.insertMany(jobsToProcess);
      logger.info(`Successfully imported ${insertedJobs.length} new jobs`);
    } else {
      logger.info('No new jobs to import');
    }

    // Close connection
    await mongoose.connection.close();
    logger.info('MongoDB connection closed');
    
  } catch (error) {
    logger.error('Error importing jobs:', error);
    process.exit(1);
  }
}

// Check if file path is provided
if (process.argv.length < 3) {
  logger.error('Please provide the path to the jobs JSON file');
  logger.info('Usage: npx ts-node src/scripts/importJobs.ts <filePath>');
  process.exit(1);
}

const filePath = process.argv[2];

// Run the import function
importJobs(filePath); 