import cron from 'node-cron';
import { JobCrawlerService } from '../services/JobCrawlerService';
import { logger } from '../services/LoggerService';

// Run every day at midnight
cron.schedule('0 0 * * *', async () => {
  try {
    logger.info('Starting daily job crawl');
    const crawler = JobCrawlerService.getInstance();
    await crawler.crawlJobs();
    logger.info('Completed daily job crawl');
  } catch (error) {
    logger.error('Error in daily job crawl:', error);
  }
}); 