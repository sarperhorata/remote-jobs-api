import fs from 'fs';
import path from 'path';

interface CoverageData {
  total: {
    lines: { total: number; covered: number; skipped: number };
    functions: { total: number; covered: number; skipped: number };
    branches: { total: number; covered: number; skipped: number };
    statements: { total: number; covered: number; skipped: number };
  };
  files: Record<string, any>;
}

interface CoverageReport {
  summary: {
    totalLines: number;
    coveredLines: number;
    totalFunctions: number;
    coveredFunctions: number;
    totalBranches: number;
    coveredBranches: number;
    totalStatements: number;
    coveredStatements: number;
    lineCoverage: number;
    functionCoverage: number;
    branchCoverage: number;
    statementCoverage: number;
  };
  files: Array<{
    file: string;
    lines: { total: number; covered: number; coverage: number };
    functions: { total: number; covered: number; coverage: number };
    branches: { total: number; covered: number; coverage: number };
    statements: { total: number; covered: number; coverage: number };
  }>;
  categories: {
    components: Array<string>;
    services: Array<string>;
    utils: Array<string>;
    pages: Array<string>;
    contexts: Array<string>;
  };
  thresholds: {
    global: { lines: number; functions: number; branches: number; statements: number };
    components: { lines: number; functions: number; branches: number; statements: number };
    services: { lines: number; functions: number; branches: number; statements: number };
    utils: { lines: number; functions: number; branches: number; statements: number };
  };
}

class CoverageReporter {
  private coveragePath: string;
  private reportPath: string;

  constructor() {
    this.coveragePath = path.join(__dirname, '../../coverage/coverage-summary.json');
    this.reportPath = path.join(__dirname, '../../coverage/detailed-report.json');
  }

  private readCoverageData(): CoverageData | null {
    try {
      if (fs.existsSync(this.coveragePath)) {
        const data = fs.readFileSync(this.coveragePath, 'utf8');
        return JSON.parse(data);
      }
      return null;
    } catch (error) {
      console.error('Error reading coverage data:', error);
      return null;
    }
  }

  private calculateCoveragePercentage(covered: number, total: number): number {
    return total > 0 ? Math.round((covered / total) * 100 * 100) / 100 : 0;
  }

  private categorizeFiles(files: Record<string, any>): {
    components: Array<string>;
    services: Array<string>;
    utils: Array<string>;
    pages: Array<string>;
    contexts: Array<string>;
  } {
    const categories = {
      components: [] as Array<string>,
      services: [] as Array<string>,
      utils: [] as Array<string>,
      pages: [] as Array<string>,
      contexts: [] as Array<string>,
    };

    Object.keys(files).forEach(file => {
      if (file.includes('/components/')) {
        categories.components.push(file);
      } else if (file.includes('/services/')) {
        categories.services.push(file);
      } else if (file.includes('/utils/')) {
        categories.utils.push(file);
      } else if (file.includes('/pages/')) {
        categories.pages.push(file);
      } else if (file.includes('/contexts/')) {
        categories.contexts.push(file);
      }
    });

    return categories;
  }

  private generateDetailedReport(coverageData: CoverageData): CoverageReport {
    const { total, files } = coverageData;
    const categorizedFiles = this.categorizeFiles(files);

    const summary = {
      totalLines: total.lines.total,
      coveredLines: total.lines.covered,
      totalFunctions: total.functions.total,
      coveredFunctions: total.functions.covered,
      totalBranches: total.branches.total,
      coveredBranches: total.branches.covered,
      totalStatements: total.statements.total,
      coveredStatements: total.statements.covered,
      lineCoverage: this.calculateCoveragePercentage(total.lines.covered, total.lines.total),
      functionCoverage: this.calculateCoveragePercentage(total.functions.covered, total.functions.total),
      branchCoverage: this.calculateCoveragePercentage(total.branches.covered, total.branches.total),
      statementCoverage: this.calculateCoveragePercentage(total.statements.covered, total.statements.total),
    };

    const fileReports = Object.entries(files).map(([file, data]) => ({
      file,
      lines: {
        total: data.lines.total,
        covered: data.lines.covered,
        coverage: this.calculateCoveragePercentage(data.lines.covered, data.lines.total),
      },
      functions: {
        total: data.functions.total,
        covered: data.functions.covered,
        coverage: this.calculateCoveragePercentage(data.functions.covered, data.functions.total),
      },
      branches: {
        total: data.branches.total,
        covered: data.branches.covered,
        coverage: this.calculateCoveragePercentage(data.branches.covered, data.branches.total),
      },
      statements: {
        total: data.statements.total,
        covered: data.statements.covered,
        coverage: this.calculateCoveragePercentage(data.statements.covered, data.statements.total),
      },
    }));

    const thresholds = {
      global: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
      components: {
        lines: 85,
        functions: 85,
        branches: 85,
        statements: 85,
      },
      services: {
        lines: 90,
        functions: 90,
        branches: 90,
        statements: 90,
      },
      utils: {
        lines: 95,
        functions: 95,
        branches: 95,
        statements: 95,
      },
    };

    return {
      summary,
      files: fileReports,
      categories: categorizedFiles,
      thresholds,
    };
  }

  private generateHTMLReport(report: CoverageReport): string {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Coverage Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .metric {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .coverage-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        .coverage-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        .files-section {
            padding: 30px;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }
        .file-name {
            font-family: monospace;
            color: #495057;
        }
        .file-coverage {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .coverage-percentage {
            font-weight: bold;
            min-width: 60px;
        }
        .good { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .category-header {
            background: #e9ecef;
            padding: 15px 30px;
            font-weight: bold;
            color: #495057;
            border-top: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Coverage Report</h1>
            <p>Generated on ${new Date().toLocaleString()}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value">${report.summary.lineCoverage}%</div>
                <div class="metric-label">Line Coverage</div>
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: ${report.summary.lineCoverage}%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.functionCoverage}%</div>
                <div class="metric-label">Function Coverage</div>
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: ${report.summary.functionCoverage}%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.branchCoverage}%</div>
                <div class="metric-label">Branch Coverage</div>
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: ${report.summary.branchCoverage}%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.statementCoverage}%</div>
                <div class="metric-label">Statement Coverage</div>
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: ${report.summary.statementCoverage}%"></div>
                </div>
            </div>
        </div>
        
        <div class="files-section">
            <h2>File Coverage Details</h2>
            
            ${Object.entries(report.categories).map(([category, files]) => `
                <div class="category-header">${category.charAt(0).toUpperCase() + category.slice(1)} (${files.length} files)</div>
                ${files.map(file => {
                    const fileReport = report.files.find(f => f.file === file);
                    if (!fileReport) return '';
                    
                    const getCoverageClass = (coverage: number) => {
                        if (coverage >= 80) return 'good';
                        if (coverage >= 60) return 'warning';
                        return 'danger';
                    };
                    
                    return `
                        <div class="file-item">
                            <div class="file-name">${file}</div>
                            <div class="file-coverage">
                                <span class="coverage-percentage ${getCoverageClass(fileReport.lines.coverage)}">
                                    ${fileReport.lines.coverage}%
                                </span>
                                <div class="coverage-bar" style="width: 100px;">
                                    <div class="coverage-fill" style="width: ${fileReport.lines.coverage}%"></div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            `).join('')}
        </div>
    </div>
</body>
</html>
    `;
    
    return html;
  }

  public generateReport(): void {
    const coverageData = this.readCoverageData();
    
    if (!coverageData) {
      console.error('No coverage data found. Run tests with coverage first.');
      return;
    }

    const report = this.generateDetailedReport(coverageData);
    
    // Save detailed JSON report
    fs.writeFileSync(this.reportPath, JSON.stringify(report, null, 2));
    
    // Generate HTML report
    const htmlReport = this.generateHTMLReport(report);
    const htmlPath = path.join(__dirname, '../../coverage/coverage-report.html');
    fs.writeFileSync(htmlPath, htmlReport);
    
    // Print summary to console
    console.log('\n📊 Test Coverage Report');
    console.log('========================');
    console.log(`Lines: ${report.summary.coveredLines}/${report.summary.totalLines} (${report.summary.lineCoverage}%)`);
    console.log(`Functions: ${report.summary.coveredFunctions}/${report.summary.totalFunctions} (${report.summary.functionCoverage}%)`);
    console.log(`Branches: ${report.summary.coveredBranches}/${report.summary.totalBranches} (${report.summary.branchCoverage}%)`);
    console.log(`Statements: ${report.summary.coveredStatements}/${report.summary.totalStatements} (${report.summary.statementCoverage}%)`);
    
    // Check thresholds
    const thresholdChecks = [
      { name: 'Lines', actual: report.summary.lineCoverage, expected: report.thresholds.global.lines },
      { name: 'Functions', actual: report.summary.functionCoverage, expected: report.thresholds.global.functions },
      { name: 'Branches', actual: report.summary.branchCoverage, expected: report.thresholds.global.branches },
      { name: 'Statements', actual: report.summary.statementCoverage, expected: report.thresholds.global.statements },
    ];
    
    console.log('\n🎯 Threshold Checks');
    console.log('==================');
    thresholdChecks.forEach(check => {
      const status = check.actual >= check.expected ? '✅' : '❌';
      console.log(`${status} ${check.name}: ${check.actual}% (target: ${check.expected}%)`);
    });
    
    console.log('\n📁 Reports Generated:');
    console.log(`- JSON: ${this.reportPath}`);
    console.log(`- HTML: ${htmlPath}`);
  }
}

// Run the reporter if this file is executed directly
if (require.main === module) {
  const reporter = new CoverageReporter();
  reporter.generateReport();
}

export default CoverageReporter;