import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Remote Jobs API',
      version: '1.0.0',
      description: 'A comprehensive API for remote job management platform',
      contact: {
        name: 'API Support',
        email: 'support@remotejobs.com'
      }
    },
    servers: [
      {
        url: 'http://localhost:8001',
        description: 'Development server'
      }
    ],
    components: {
      schemas: {
        Job: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Unique job identifier'
            },
            title: {
              type: 'string',
              description: 'Job title'
            },
            company: {
              type: 'object',
              properties: {
                id: { type: 'string' },
                name: { type: 'string' },
                logo: { type: 'string' },
                description: { type: 'string' },
                website: { type: 'string' }
              }
            },
            description: {
              type: 'string',
              description: 'Job description'
            },
            location: {
              type: 'string',
              description: 'Job location'
            },
            type: {
              type: 'string',
              description: 'Job type (Full-time, Part-time, Contract)'
            },
            salary: {
              type: 'object',
              properties: {
                min: { type: 'number' },
                max: { type: 'number' },
                currency: { type: 'string' }
              }
            },
            skills: {
              type: 'array',
              items: { type: 'string' }
            },
            postedAt: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        Application: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Application ID'
            },
            jobId: {
              type: 'string',
              description: 'Job ID'
            },
            userId: {
              type: 'string',
              description: 'User ID'
            },
            status: {
              type: 'string',
              enum: ['pending', 'reviewed', 'accepted', 'rejected']
            },
            appliedAt: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        User: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'User ID'
            },
            name: {
              type: 'string',
              description: 'User full name'
            },
            email: {
              type: 'string',
              format: 'email'
            },
            skills: {
              type: 'array',
              items: { type: 'string' }
            }
          }
        },
        Error: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'Error message'
            }
          }
        }
      }
    }
  },
  apis: ['./src/routes/*.ts', './src/index.ts']
};

export const specs = swaggerJsdoc(options);
export { swaggerUi }; 