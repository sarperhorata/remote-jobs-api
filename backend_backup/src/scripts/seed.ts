import mongoose from 'mongoose';
import Company from '../models/Company';
import Job from '../models/Job';
import { logger } from '../utils/logger';

// Use the working MongoDB URI directly
const mongoUri = 'mongodb+srv://myremotejobs:cH622T5iGoc9tzfe@remotejobs.tn0gxu0.mongodb.net/remotejobs?retryWrites=true&w=majority&appName=RemoteJobs';

const companies = [
  {
    name: 'Google',
    website: 'https://careers.google.com',
    logo: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/google_logo.max-1000x1000.png',
    description: 'Google is an American multinational technology company that specializes in Internet-related services and products.',
    industry: 'Technology',
    size: '10000+',
    location: 'Mountain View, CA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['Python', 'Java', 'C++', 'Go', 'JavaScript', 'TensorFlow', 'Kubernetes'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/google',
      twitter: 'https://twitter.com/google',
      github: 'https://github.com/google'
    }
  },
  {
    name: 'Microsoft',
    website: 'https://careers.microsoft.com',
    logo: 'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31',
    description: 'Microsoft Corporation is an American multinational technology corporation which produces computer software, consumer electronics, personal computers, and related services.',
    industry: 'Technology',
    size: '10000+',
    location: 'Redmond, WA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['C#', '.NET', 'Azure', 'TypeScript', 'React', 'PowerShell', 'Docker'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/microsoft',
      twitter: 'https://twitter.com/microsoft',
      github: 'https://github.com/microsoft'
    }
  },
  {
    name: 'Amazon',
    website: 'https://www.amazon.jobs',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/4/4a/Amazon_icon.svg',
    description: 'Amazon.com, Inc. is an American multinational technology company which focuses on e-commerce, cloud computing, digital streaming, and artificial intelligence.',
    industry: 'Technology',
    size: '10000+',
    location: 'Seattle, WA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['Java', 'Python', 'AWS', 'React', 'Node.js', 'Docker', 'Kubernetes'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/amazon',
      twitter: 'https://twitter.com/amazon',
      github: 'https://github.com/aws'
    }
  },
  {
    name: 'Meta',
    website: 'https://www.metacareers.com',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg',
    description: 'Meta Platforms, Inc., doing business as Meta and formerly known as Facebook, Inc., is an American multinational technology conglomerate.',
    industry: 'Technology',
    size: '10000+',
    location: 'Menlo Park, CA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['PHP', 'React', 'GraphQL', 'Python', 'Hack', 'MySQL', 'Cassandra'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/meta',
      twitter: 'https://twitter.com/meta',
      github: 'https://github.com/facebook'
    }
  },
  {
    name: 'Apple',
    website: 'https://jobs.apple.com',
    logo: 'https://www.apple.com/ac/globalnav/7/en_US/images/be15095f-5a20-57d0-ad14-cf4c638e223a/globalnav_apple_image__b5er5ngrzxqq_large.svg',
    description: 'Apple Inc. is an American multinational technology company that specializes in consumer electronics, computer software, and online services.',
    industry: 'Technology',
    size: '10000+',
    location: 'Cupertino, CA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['Swift', 'Objective-C', 'Python', 'Java', 'JavaScript', 'Ruby', 'Go'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/apple',
      twitter: 'https://twitter.com/apple',
      github: 'https://github.com/apple'
    }
  },
  {
    name: 'Netflix',
    website: 'https://jobs.netflix.com',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/6/69/Netflix_logo.svg',
    description: 'Netflix, Inc. is an American subscription streaming service and production company.',
    industry: 'Entertainment',
    size: '1000-10000',
    location: 'Los Gatos, CA',
    remotePolicy: 'Remote-First',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work', 'Unlimited PTO'],
    techStack: ['Java', 'Python', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/netflix',
      twitter: 'https://twitter.com/netflix',
      github: 'https://github.com/netflix'
    }
  },
  {
    name: 'Spotify',
    website: 'https://www.spotifyjobs.com',
    logo: 'https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png',
    description: 'Spotify is a Swedish audio streaming and media services provider.',
    industry: 'Entertainment',
    size: '1000-10000',
    location: 'Stockholm, Sweden',
    remotePolicy: 'Remote-First',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work', 'Learning Budget'],
    techStack: ['Java', 'Python', 'React', 'Node.js', 'Go', 'Kotlin', 'Swift'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/spotify',
      twitter: 'https://twitter.com/spotify',
      github: 'https://github.com/spotify'
    }
  },
  {
    name: 'Shopify',
    website: 'https://www.shopify.com/careers',
    logo: 'https://cdn.shopify.com/shopifycloud/brochure/assets/brand-assets/shopify-logo-primary-logo-456baa801ee66a0a435671082365958316831c9960c480451dd0330bcdae304f.svg',
    description: 'Shopify Inc. is a Canadian multinational e-commerce company.',
    industry: 'E-commerce',
    size: '1000-10000',
    location: 'Ottawa, Canada',
    remotePolicy: 'Remote-First',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work', 'Learning Budget'],
    techStack: ['Ruby', 'React', 'Node.js', 'Python', 'Go', 'Java', 'PHP'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/shopify',
      twitter: 'https://twitter.com/shopify',
      github: 'https://github.com/Shopify'
    }
  },
  {
    name: 'GitLab',
    website: 'https://about.gitlab.com/jobs',
    logo: 'https://about.gitlab.com/images/press/logo/svg/gitlab-logo-gray-rgb.svg',
    description: 'GitLab Inc. is a DevOps platform delivered as a single application.',
    industry: 'Technology',
    size: '1000-10000',
    location: 'Remote',
    remotePolicy: 'Remote-First',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work', 'Learning Budget'],
    techStack: ['Ruby', 'React', 'Vue.js', 'Go', 'Python', 'Java', 'Kubernetes'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/gitlab',
      twitter: 'https://twitter.com/gitlab',
      github: 'https://github.com/gitlabhq'
    }
  },
  {
    name: 'DigitalOcean',
    website: 'https://www.digitalocean.com/careers',
    logo: 'https://www.digitalocean.com/assets/images/logo.svg',
    description: 'DigitalOcean, Inc. is an American cloud infrastructure provider.',
    industry: 'Technology',
    size: '500-1000',
    location: 'New York, NY',
    remotePolicy: 'Remote-First',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work', 'Learning Budget'],
    techStack: ['Go', 'Python', 'React', 'Ruby', 'Kubernetes', 'Docker', 'Terraform'],
    socialLinks: {
      linkedin: 'https://www.linkedin.com/company/digitalocean',
      twitter: 'https://twitter.com/digitalocean',
      github: 'https://github.com/digitalocean'
    }
  }
];

const timeZones = [
  { region: 'US Remote', gmt: 'GMT-8 to GMT-4' },
  { region: 'Europe Remote', gmt: 'GMT+0 to GMT+3' },
  { region: 'Asia Pacific Remote', gmt: 'GMT+7 to GMT+12' },
  { region: 'Latin America Remote', gmt: 'GMT-5 to GMT-3' },
  { region: 'Africa Remote', gmt: 'GMT+0 to GMT+4' },
  { region: 'Middle East Remote', gmt: 'GMT+2 to GMT+4' }
];

const jobTypes = [
  'Full-time',
  'Part-time',
  'Contract',
  'Freelance',
  'Internship'
];

const categories = [
  'Software Development',
  'Data Science',
  'DevOps',
  'Product Management',
  'UX/UI Design',
  'Marketing',
  'Sales',
  'Customer Support',
  'Content Writing',
  'Project Management'
];

async function seed() {
  try {
    // Connect to MongoDB
    await mongoose.connect(mongoUri);
    logger.info('Connected to MongoDB');

    // Clear existing data
    await Company.deleteMany({});
    await Job.deleteMany({});
    logger.info('Cleared existing data');

    // Insert companies
    const insertedCompanies = await Company.insertMany(companies);
    logger.info(`Inserted ${insertedCompanies.length} companies`);

    // Generate sample jobs
    const jobs = [];
    for (const company of insertedCompanies) {
      // Generate 5-10 jobs per company
      const numJobs = Math.floor(Math.random() * 5) + 5;
      for (let i = 0; i < numJobs; i++) {
        const category = categories[Math.floor(Math.random() * categories.length)];
        const timeZone = timeZones[Math.floor(Math.random() * timeZones.length)];
        const type = jobTypes[Math.floor(Math.random() * jobTypes.length)];
        
        jobs.push({
          title: `${category} - ${company.name}`,
          companyId: company._id,
          description: `We are looking for a ${category} professional to join our team at ${company.name}.`,
          requirements: [
            '5+ years of experience',
            'Strong communication skills',
            'Team player',
            'Problem-solving abilities'
          ],
          responsibilities: [
            'Develop and maintain software applications',
            'Collaborate with cross-functional teams',
            'Write clean, maintainable code',
            'Participate in code reviews'
          ],
          skills: company.techStack.slice(0, 5),
          location: timeZone.region,
          type: type,
          salary: {
            min: 80000,
            max: 150000,
            currency: 'USD'
          },
          experience: {
            min: 3,
            max: 8
          },
          education: 'Bachelor\'s degree in Computer Science or related field',
          benefits: company.benefits,
          applicationUrl: `${company.website}/apply`,
          source: 'Direct',
          sourceUrl: company.website,
          status: 'active',
          postedAt: new Date(),
          expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days from now
        });
      }
    }

    // Insert jobs
    const insertedJobs = await Job.insertMany(jobs);
    logger.info(`Inserted ${insertedJobs.length} jobs`);

    logger.info('Seed completed successfully');
    process.exit(0);
  } catch (error) {
    logger.error('Error seeding database:', error);
    process.exit(1);
  }
}

seed(); 