import axios from 'axios';
import { logger } from './LoggerService';
import { Job } from '../models/Job';
import { Company } from '../models/Company';

const HR_COMPANIES = [
  {
    name: 'Ashby',
    baseUrl: 'https://jobs.ashbyhq.com',
    apiEndpoint: '/api/non-user-graphql',
    query: `
      query {
        jobs {
          id
          title
          location
          department
          employmentType
          description
          company {
            id
            name
            website
            logo
          }
        }
      }
    `
  },
  {
    name: 'Greenhouse',
    baseUrl: 'https://boards.greenhouse.io',
    apiEndpoint: '/api/v1/jobs',
  },
  {
    name: 'Breezy',
    baseUrl: 'https://breezy.hr',
    apiEndpoint: '/api/v1/jobs',
  },
  {
    name: 'Lever',
    baseUrl: 'https://jobs.lever.co',
    apiEndpoint: '/api/v1/jobs',
  },
  {
    name: 'Workday',
    baseUrl: 'https://workday.wd5.myworkdayjobs.com',
    apiEndpoint: '/api/jobs',
  },
  {
    name: 'BambooHR',
    baseUrl: 'https://api.bamboohr.com',
    apiEndpoint: '/api/gateway.php',
  },
  {
    name: 'JazzHR',
    baseUrl: 'https://api.jazzhr.com',
    apiEndpoint: '/v1/jobs',
  },
  {
    name: 'Recruitee',
    baseUrl: 'https://api.recruitee.com',
    apiEndpoint: '/jobs',
  },
  {
    name: 'Jobvite',
    baseUrl: 'https://jobs.jobvite.com',
    apiEndpoint: '/api/jobs',
  },
  {
    name: 'SmartRecruiters',
    baseUrl: 'https://api.smartrecruiters.com',
    apiEndpoint: '/v1/companies/jobs',
  },
  {
    name: 'Workable',
    baseUrl: 'https://api.workable.com',
    apiEndpoint: '/spi/v3/jobs',
  },
  {
    name: 'Personio',
    baseUrl: 'https://api.personio.de',
    apiEndpoint: '/v1/jobs',
  },
  {
    name: 'BambooHR',
    baseUrl: 'https://api.bamboohr.com',
    apiEndpoint: '/v1/jobs',
  },
  {
    name: 'Paylocity',
    baseUrl: 'https://api.paylocity.com',
    apiEndpoint: '/api/v2/jobs',
  },
  {
    name: 'Paycom',
    baseUrl: 'https://api.paycomonline.net',
    apiEndpoint: '/v1/jobs',
  },
  {
    name: 'Paychex',
    baseUrl: 'https://api.paychex.com',
    apiEndpoint: '/jobs',
  },
  {
    name: 'ADP',
    baseUrl: 'https://api.adp.com',
    apiEndpoint: '/jobs',
  },
  {
    name: 'Ceridian',
    baseUrl: 'https://api.ceridian.com',
    apiEndpoint: '/jobs',
  },
  {
    name: 'UKG',
    baseUrl: 'https://api.ukg.com',
    apiEndpoint: '/jobs',
  },
  {
    name: 'Paycor',
    baseUrl: 'https://api.paycor.com',
    apiEndpoint: '/jobs',
  }
];

export class JobCrawlerService {
  private static instance: JobCrawlerService;

  private constructor() {}

  public static getInstance(): JobCrawlerService {
    if (!JobCrawlerService.instance) {
      JobCrawlerService.instance = new JobCrawlerService();
    }
    return JobCrawlerService.instance;
  }

  async crawlJobs() {
    for (const company of HR_COMPANIES) {
      try {
        logger.info(`Starting crawl for ${company.name}`);
        
        switch (company.name) {
          case 'Ashby':
            await this.crawlAshbyJobs(company);
            break;
          case 'Greenhouse':
            await this.crawlGreenhouseJobs(company);
            break;
          case 'Breezy':
            await this.crawlBreezyJobs(company);
            break;
        }
        
        logger.info(`Completed crawl for ${company.name}`);
      } catch (error) {
        logger.error(`Error crawling ${company.name}:`, error);
      }
    }
  }

  private async crawlAshbyJobs(company: typeof HR_COMPANIES[0]) {
    const response = await axios.post(`${company.baseUrl}${company.apiEndpoint}`, {
      query: company.query
    });

    const jobs = response.data.data.jobs;
    
    for (const job of jobs) {
      if (this.isRemoteJob(job)) {
        await this.saveJob(job, company.name);
      }
    }
  }

  private async crawlGreenhouseJobs(company: typeof HR_COMPANIES[0]) {
    const response = await axios.get(`${company.baseUrl}${company.apiEndpoint}`);
    const jobs = response.data.jobs;

    for (const job of jobs) {
      if (this.isRemoteJob(job)) {
        await this.saveJob(job, company.name);
      }
    }
  }

  private async crawlBreezyJobs(company: typeof HR_COMPANIES[0]) {
    const response = await axios.get(`${company.baseUrl}${company.apiEndpoint}`);
    const jobs = response.data;

    for (const job of jobs) {
      if (this.isRemoteJob(job)) {
        await this.saveJob(job, company.name);
      }
    }
  }

  private isRemoteJob(job: any): boolean {
    const remoteKeywords = ['remote', 'work from home', 'wfh', 'virtual', 'anywhere'];
    const location = job.location?.toLowerCase() || '';
    const description = job.description?.toLowerCase() || '';
    
    return remoteKeywords.some(keyword => 
      location.includes(keyword) || description.includes(keyword)
    );
  }

  private async saveJob(jobData: any, source: string) {
    try {
      // Save company first
      const company = await Company.findOneAndUpdate(
        { name: jobData.company.name },
        {
          name: jobData.company.name,
          website: jobData.company.website,
          logo: jobData.company.logo,
          source
        },
        { upsert: true, new: true }
      );

      // Then save job
      await Job.findOneAndUpdate(
        { externalId: jobData.id, source },
        {
          title: jobData.title,
          description: jobData.description,
          location: jobData.location,
          type: jobData.employmentType,
          companyId: company._id,
          source,
          externalId: jobData.id,
          postedAt: new Date(),
          status: 'active'
        },
        { upsert: true, new: true }
      );

      logger.info(`Saved job: ${jobData.title} from ${source}`);
    } catch (error) {
      logger.error(`Error saving job from ${source}:`, error);
    }
  }
} 