import mongoose from 'mongoose';
import fs from 'fs';
import Company from '../models/Company';
import { logger } from '../utils/logger';

// Use the working MongoDB URI
const mongoUri = 'mongodb+srv://myremotejobs:cH622T5iGoc9tzfe@remotejobs.tn0gxu0.mongodb.net/remotejobs?retryWrites=true&w=majority&appName=RemoteJobs';

interface ExportEntry {
  name: string;
  uri: string;
  content?: string;
  tags?: string[];
  schedule?: string;
  [key: string]: any;
}

/**
 * Import companies from the export data file
 * @param filePath Path to the export data JSON file
 */
async function importCompaniesFromExport(filePath: string): Promise<void> {
  try {
    // Connect to MongoDB
    await mongoose.connect(mongoUri);
    logger.info('Connected to MongoDB');

    // Read the export file
    const rawData = fs.readFileSync(filePath, 'utf8');
    const exportData: ExportEntry[] = JSON.parse(rawData);
    
    logger.info(`Loaded export data with ${exportData.length} entries`);

    // Get existing companies from the database
    const existingCompanies = await Company.find({}, { website: 1, name: 1 });
    
    const existingWebsites = new Set(existingCompanies.map(company => company.website));
    const existingNames = new Set(existingCompanies.map(company => company.name));
    
    logger.info(`Found ${existingCompanies.length} existing companies in the database`);

    // Process each entry to create a company record
    const companiesToInsert = [];
    let duplicateCount = 0;
    
    for (const entry of exportData) {
      if (!entry.name || !entry.uri) {
        continue;
      }

      // Extract company name and website
      const companyName = extractCompanyName(entry.name);
      const website = extractWebsite(entry.uri);
      
      // Skip if this company already exists
      if (existingWebsites.has(website) || existingNames.has(companyName)) {
        duplicateCount++;
        continue;
      }
      
      // Prepare company data
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
      
      companiesToInsert.push(companyData);
      
      // Also add to the existing sets to prevent duplicates in this import batch
      existingWebsites.add(website);
      existingNames.add(companyName);
    }
    
    logger.info(`Found ${duplicateCount} duplicate companies`);
    logger.info(`Preparing to import ${companiesToInsert.length} new companies`);

    // Insert companies if any
    if (companiesToInsert.length > 0) {
      const insertedCompanies = await Company.insertMany(companiesToInsert);
      logger.info(`Successfully imported ${insertedCompanies.length} new companies`);
    } else {
      logger.info('No new companies to import');
    }

    // Close connection
    await mongoose.connection.close();
    logger.info('MongoDB connection closed');
    
  } catch (error) {
    logger.error('Error importing companies from export data:', error);
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

// Check if file path is provided
if (process.argv.length < 3) {
  logger.error('Please provide the path to the export data file');
  logger.info('Usage: npx ts-node src/scripts/importCompanies.ts <filePath>');
  process.exit(1);
}

const filePath = process.argv[2];

// Run the import function
importCompaniesFromExport(filePath)
  .catch(error => {
    logger.error('Error in main process:', error);
    process.exit(1);
  }); 