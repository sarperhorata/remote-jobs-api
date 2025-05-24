import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';
import { logger } from '../utils/logger';

/**
 * Convert a CSV file to JSON format
 * @param csvFilePath Path to the CSV file
 * @param jsonFilePath Path where to save the JSON output
 */
function convertCsvToJson(csvFilePath: string, jsonFilePath: string) {
  try {
    // Read the CSV file
    const csvData = fs.readFileSync(csvFilePath, 'utf8');
    
    // Parse CSV data
    const records = parse(csvData, {
      columns: true,
      skip_empty_lines: true,
      trim: true
    });
    
    logger.info(`Parsed ${records.length} records from CSV file`);
    
    // Transform data to match Company schema
    const companies = records.map((record: any) => {
      // Map CSV fields to Company schema fields
      // Adjust these mappings based on your actual CSV column names
      return {
        name: record.name || record.company_name || record.company || '',
        website: record.website || record.url || record.company_url || '',
        logo: record.logo || record.logo_url || record.company_logo || '',
        description: record.description || record.company_description || '',
        industry: record.industry || record.category || '',
        size: record.size || record.company_size || '',
        location: record.location || record.headquarters || '',
        remotePolicy: record.remote_policy || 'Remote-First',
        benefits: record.benefits ? record.benefits.split(',').map((b: string) => b.trim()) : [],
        techStack: record.tech_stack ? record.tech_stack.split(',').map((t: string) => t.trim()) : [],
        socialLinks: {
          linkedin: record.linkedin || record.linkedin_url || '',
          twitter: record.twitter || record.twitter_url || '',
          github: record.github || record.github_url || ''
        }
      };
    });
    
    // Filter out invalid companies (must have name and website)
    const validCompanies = companies.filter(company => company.name && company.website);
    
    logger.info(`Found ${companies.length - validCompanies.length} invalid records (missing name or website)`);
    logger.info(`Saving ${validCompanies.length} valid companies to JSON file`);
    
    // Write to JSON file
    fs.writeFileSync(jsonFilePath, JSON.stringify(validCompanies, null, 2));
    
    logger.info(`Successfully converted CSV to JSON and saved to ${jsonFilePath}`);
    
  } catch (error) {
    logger.error('Error converting CSV to JSON:', error);
    process.exit(1);
  }
}

// Check if file paths are provided
if (process.argv.length < 4) {
  logger.error('Please provide paths for both input CSV and output JSON files');
  logger.info('Usage: npx ts-node src/scripts/convertCsvToJson.ts <csvFilePath> <jsonFilePath>');
  process.exit(1);
}

const csvFilePath = process.argv[2];
const jsonFilePath = process.argv[3];

// Run the conversion function
convertCsvToJson(csvFilePath, jsonFilePath); 