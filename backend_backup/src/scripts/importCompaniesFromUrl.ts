import mongoose from 'mongoose';
import fs from 'fs';
import path from 'path';
import Company from '../models/Company';
import { logger } from '../utils/logger';

// Use the working MongoDB URI
const mongoUri = 'mongodb+srv://myremotejobs:cH622T5iGoc9tzfe@remotejobs.tn0gxu0.mongodb.net/remotejobs?retryWrites=true&w=majority&appName=RemoteJobs';

/**
 * Import companies from a file containing URLs
 * @param filePath Path to the file containing URLs (JSON or CSV)
 */
async function importCompaniesFromUrl(filePath: string) {
  try {
    // Connect to MongoDB
    await mongoose.connect(mongoUri);
    logger.info('Connected to MongoDB');

    // Read the file
    const fileData = fs.readFileSync(filePath, 'utf8');
    let urls: string[] = [];
    
    // Determine file type and parse accordingly
    if (filePath.endsWith('.json')) {
      // Parse JSON
      const jsonData = JSON.parse(fileData);
      
      // Handle different JSON structures
      if (Array.isArray(jsonData)) {
        if (typeof jsonData[0] === 'string') {
          // Array of strings
          urls = jsonData;
        } else if (typeof jsonData[0] === 'object') {
          // Array of objects, extract URL property
          urls = jsonData.map(item => {
            // Check different possible URL field names
            return item.url || item.website || item.company_url || item.link || '';
          }).filter(url => url);
        }
      } else if (typeof jsonData === 'object') {
        // Object with URLs as values
        urls = Object.values(jsonData).filter(url => typeof url === 'string');
      }
    } else if (filePath.endsWith('.csv')) {
      // Simple CSV parsing (assuming one URL per line)
      urls = fileData.split('\n')
        .map(line => line.trim())
        .filter(line => line && !line.startsWith('#'))
        .map(line => {
          // If CSV has headers, try to extract URL
          const parts = line.split(',');
          if (parts.length > 1) {
            // Find a part that looks like a URL
            return parts.find(part => part.includes('http') || part.includes('www.')) || '';
          }
          return line;
        })
        .filter(url => url);
    } else {
      // Assume plain text, one URL per line
      urls = fileData.split('\n')
        .map(line => line.trim())
        .filter(line => line && !line.startsWith('#'));
    }
    
    logger.info(`Found ${urls.length} URLs in the file`);

    // Get existing companies from the database
    const existingCompanies = await Company.find({}, { website: 1 });
    const existingUrls = new Set(existingCompanies.map(company => company.website));
    
    logger.info(`Found ${existingCompanies.length} existing companies in the database`);

    // Filter out duplicates
    const newUrls = urls.filter(url => !existingUrls.has(url));
    
    logger.info(`Found ${urls.length - newUrls.length} duplicate URLs`);
    logger.info(`Preparing to import ${newUrls.length} new company URLs`);

    // Create basic company records for each URL
    const companiesToInsert = newUrls.map(url => {
      // Extract company name from URL
      let name = '';
      try {
        const urlObj = new URL(url);
        name = urlObj.hostname
          .replace('www.', '')
          .split('.')
          .slice(0, -1)
          .join('.')
          .split('-')
          .map(part => part.charAt(0).toUpperCase() + part.slice(1))
          .join(' ');
      } catch (e) {
        // If URL parsing fails, use the URL as is
        name = url.replace('http://', '').replace('https://', '').split('/')[0];
      }
      
      return {
        name,
        website: url,
        logo: '',
        description: `${name} is a company that offers remote jobs.`,
        industry: 'Technology',
        size: 'Unknown',
        location: 'Remote',
        remotePolicy: 'Remote-First',
        benefits: [],
        techStack: [],
        socialLinks: {}
      };
    });

    // Insert new companies if any
    if (companiesToInsert.length > 0) {
      const insertedCompanies = await Company.insertMany(companiesToInsert);
      logger.info(`Successfully imported ${insertedCompanies.length} new company URLs`);
    } else {
      logger.info('No new company URLs to import');
    }

    // Close connection
    await mongoose.connection.close();
    logger.info('MongoDB connection closed');
    
  } catch (error) {
    logger.error('Error importing companies from URL file:', error);
    process.exit(1);
  }
}

// Check if file path is provided
if (process.argv.length < 3) {
  logger.error('Please provide the path to the file containing URLs');
  logger.info('Usage: npx ts-node src/scripts/importCompaniesFromUrl.ts <filePath>');
  process.exit(1);
}

const filePath = process.argv[2];

// Run the import function
importCompaniesFromUrl(filePath); 