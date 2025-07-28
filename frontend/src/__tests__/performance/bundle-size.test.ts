import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

describe('Bundle Size Performance Tests', () => {
  const bundleStatsPath = path.join(__dirname, '../../../bundle-stats.json');
  const maxBundleSize = 500 * 1024; // 500KB
  const maxChunkSize = 200 * 1024; // 200KB

  beforeAll(() => {
    // Build the project to generate bundle stats
    try {
      execSync('npm run build', { stdio: 'pipe' });
    } catch (error) {
      console.warn('Build failed, using existing bundle stats');
    }
  });

  describe('Main Bundle Size', () => {
    it('should have main bundle under 500KB', () => {
      const stats = JSON.parse(fs.readFileSync(bundleStatsPath, 'utf8'));
      const mainBundle = stats.chunks.find((chunk: any) => chunk.names.includes('main'));
      
      expect(mainBundle.size).toBeLessThan(maxBundleSize);
      console.log(`Main bundle size: ${(mainBundle.size / 1024).toFixed(2)}KB`);
    });

    it('should have reasonable chunk sizes', () => {
      const stats = JSON.parse(fs.readFileSync(bundleStatsPath, 'utf8'));
      
      stats.chunks.forEach((chunk: any) => {
        expect(chunk.size).toBeLessThan(maxChunkSize);
        console.log(`Chunk ${chunk.names.join(', ')}: ${(chunk.size / 1024).toFixed(2)}KB`);
      });
    });
  });

  describe('Dependency Analysis', () => {
    it('should not have duplicate dependencies', () => {
      const stats = JSON.parse(fs.readFileSync(bundleStatsPath, 'utf8'));
      const modules = stats.modules || [];
      
      const moduleNames = modules.map((module: any) => module.name);
      const duplicates = moduleNames.filter((name: string, index: number) => 
        moduleNames.indexOf(name) !== index
      );
      
      expect(duplicates).toHaveLength(0);
    });

    it('should have optimized imports', () => {
      const stats = JSON.parse(fs.readFileSync(bundleStatsPath, 'utf8'));
      const modules = stats.modules || [];
      
      // Check for large libraries that should be tree-shaken
      const largeLibraries = modules.filter((module: any) => 
        module.size > 50 * 1024 && 
        (module.name.includes('lodash') || module.name.includes('moment'))
      );
      
      expect(largeLibraries.length).toBeLessThan(5);
    });
  });

  describe('Code Splitting', () => {
    it('should have proper code splitting for routes', () => {
      const stats = JSON.parse(fs.readFileSync(bundleStatsPath, 'utf8'));
      const chunks = stats.chunks || [];
      
      // Should have separate chunks for different routes
      const routeChunks = chunks.filter((chunk: any) => 
        chunk.names.some((name: string) => 
          name.includes('route') || name.includes('page')
        )
      );
      
      expect(routeChunks.length).toBeGreaterThan(1);
    });

    it('should have vendor chunk separation', () => {
      const stats = JSON.parse(fs.readFileSync(bundleStatsPath, 'utf8'));
      const chunks = stats.chunks || [];
      
      const vendorChunk = chunks.find((chunk: any) => 
        chunk.names.includes('vendor')
      );
      
      expect(vendorChunk).toBeDefined();
      expect(vendorChunk.size).toBeLessThan(300 * 1024); // 300KB
    });
  });

  describe('Asset Optimization', () => {
    it('should have optimized images', () => {
      const publicPath = path.join(__dirname, '../../../public');
      const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg'];
      
      const images = fs.readdirSync(publicPath)
        .filter(file => imageExtensions.some(ext => file.endsWith(ext)))
        .map(file => path.join(publicPath, file));
      
      images.forEach(imagePath => {
        const stats = fs.statSync(imagePath);
        expect(stats.size).toBeLessThan(500 * 1024); // 500KB per image
      });
    });

    it('should have compressed assets', () => {
      const buildPath = path.join(__dirname, '../../../build');
      const jsFiles = fs.readdirSync(buildPath)
        .filter(file => file.endsWith('.js'))
        .map(file => path.join(buildPath, file));
      
      jsFiles.forEach(filePath => {
        const content = fs.readFileSync(filePath, 'utf8');
        // Check if file is minified (no comments, no spaces)
        const lines = content.split('\n');
        const avgLineLength = content.length / lines.length;
        expect(avgLineLength).toBeGreaterThan(80); // Minified files have long lines
      });
    });
  });
});