import express from 'express';
import { Router } from 'express';

const router: Router = express.Router();

/**
 * @swagger
 * /api/jobs/featured:
 *   get:
 *     summary: Get featured jobs
 *     description: Retrieve a list of featured job postings
 *     tags: [Jobs]
 *     responses:
 *       200:
 *         description: List of featured jobs
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Job'
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Error'
 */
router.get('/featured', async (_req, res) => {
  try {
    const featuredJobs = [
      {
        id: '1',
        title: 'Senior Frontend Developer',
        company: {
          id: '1',
          name: 'Tech Corp',
          logo: 'https://via.placeholder.com/150',
          description: 'Leading technology company',
          website: 'https://techcorp.com'
        },
        description: 'Looking for an experienced frontend developer to join our remote team...',
        location: 'Remote - Worldwide',
        type: 'Full-time',
        salary: {
          min: 120000,
          max: 150000,
          currency: 'USD'
        },
        skills: ['React', 'TypeScript', 'Node.js', 'GraphQL'],
        postedAt: new Date().toISOString()
      },
      {
        id: '2',
        title: 'DevOps Engineer',
        company: {
          id: '2',
          name: 'Cloud Solutions Inc',
          logo: 'https://via.placeholder.com/150',
          description: 'Cloud infrastructure specialists',
          website: 'https://cloudsolutions.com'
        },
        description: 'We are seeking a skilled DevOps Engineer to manage our cloud infrastructure...',
        location: 'Remote - US/EU',
        type: 'Full-time',
        salary: {
          min: 110000,
          max: 140000,
          currency: 'USD'
        },
        skills: ['AWS', 'Docker', 'Kubernetes', 'Terraform'],
        postedAt: new Date().toISOString()
      }
    ];
    res.json(featuredJobs);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching featured jobs' });
  }
});

/**
 * @swagger
 * /api/jobs/stats:
 *   get:
 *     summary: Get job statistics
 *     description: Retrieve statistics about jobs and companies
 *     tags: [Jobs]
 *     responses:
 *       200:
 *         description: Job statistics
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 totalJobs:
 *                   type: number
 *                   description: Total number of jobs
 *                 totalCompanies:
 *                   type: number
 *                   description: Total number of companies
 *                 jobsLast24h:
 *                   type: number
 *                   description: Jobs posted in last 24 hours
 *       500:
 *         description: Server error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Error'
 */
router.get('/stats', async (_req, res) => {
  try {
    const stats = {
      totalJobs: 45672,
      totalCompanies: 2847,
      jobsLast24h: 234,
      remoteJobs: 28943,
      averageSalary: 125000
    };
    res.json(stats);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching job statistics' });
  }
});

export const jobRoutes = router; 