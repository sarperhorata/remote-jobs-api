from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime

router = APIRouter(prefix="/legal", tags=["Legal"])

# Current version and last updated date
TERMS_VERSION = "1.0"
PRIVACY_VERSION = "1.0"
LAST_UPDATED = "2024-01-15"

@router.get("/terms", response_class=HTMLResponse)
async def get_terms_and_conditions():
    """
    **Terms and Conditions Page**
    
    Comprehensive terms of service including subscription terms, billing policies, and user obligations.
    GDPR compliant and includes specific provisions for EU users.
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Terms and Conditions - Buzz2Remote</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 40px; max-width: 800px; margin: 0 auto; color: #333; }}
            h1 {{ color: #2d3748; border-bottom: 3px solid #f6ad55; padding-bottom: 10px; }}
            h2 {{ color: #4a5568; margin-top: 30px; }}
            h3 {{ color: #718096; }}
            .highlight {{ background-color: #fef5e7; padding: 15px; border-left: 4px solid #f6ad55; margin: 20px 0; }}
            .important {{ background-color: #fed7d7; padding: 15px; border-left: 4px solid #e53e3e; margin: 20px 0; }}
            .contact {{ background-color: #e6fffa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            ul, ol {{ padding-left: 20px; }}
            li {{ margin: 8px 0; }}
            .version {{ color: #718096; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>🐝 Buzz2Remote - Terms and Conditions</h1>
        
        <div class="version">
            <strong>Version:</strong> {TERMS_VERSION} | <strong>Last Updated:</strong> {LAST_UPDATED}
        </div>

        <div class="highlight">
            <strong>📋 Quick Summary:</strong> By using Buzz2Remote, you agree to our terms including subscription billing, 
            data processing under GDPR, and our commitment to helping you find remote work opportunities.
        </div>

        <h2>1. 🎯 Service Description</h2>
        <p><strong>Buzz2Remote</strong> is a comprehensive remote job matching platform that uses artificial intelligence to connect job seekers with global remote opportunities. Our services include:</p>
        <ul>
            <li><strong>AI-Powered Job Matching:</strong> Advanced algorithms to match your skills with relevant opportunities</li>
            <li><strong>Global Job Database:</strong> Thousands of verified remote positions from trusted employers</li>
            <li><strong>Profile Enhancement:</strong> Tools to optimize your professional profile</li>
            <li><strong>Application Management:</strong> Streamlined application tracking and management</li>
            <li><strong>Premium Features:</strong> Advanced filtering, priority support, and exclusive job listings</li>
        </ul>

        <h2>2. 💳 Subscription and Billing Terms</h2>
        
        <h3>2.1 Free Tier</h3>
        <ul>
            <li>Limited job searches per day</li>
            <li>Basic profile features</li>
            <li>Standard job recommendations</li>
            <li>Community support</li>
        </ul>

        <h3>2.2 Premium Subscriptions</h3>
        <ul>
            <li><strong>Monthly Subscription:</strong> Billed monthly, cancel anytime</li>
            <li><strong>Annual Subscription:</strong> Billed yearly with significant savings</li>
            <li><strong>Auto-renewal:</strong> Subscriptions automatically renew unless cancelled</li>
            <li><strong>Currency:</strong> All prices displayed in USD unless otherwise specified</li>
        </ul>

        <div class="important">
            <strong>⚠️ Billing Important:</strong>
            <ul>
                <li>Payments are charged to your chosen payment method immediately upon subscription</li>
                <li>Auto-renewal occurs 24 hours before the current period expires</li>
                <li>You can cancel at any time through your account settings</li>
                <li>Cancellation takes effect at the end of the current billing period</li>
                <li>No partial refunds for unused portions of subscription periods</li>
            </ul>
        </div>

        <h2>3. 🔄 Refund Policy</h2>
        <ul>
            <li><strong>14-Day Money-Back Guarantee:</strong> Full refund within 14 days of initial subscription</li>
            <li><strong>Exceptional Circumstances:</strong> Refunds may be considered for technical issues preventing service use</li>
            <li><strong>Processing Time:</strong> Approved refunds processed within 5-10 business days</li>
            <li><strong>Refund Method:</strong> Refunds issued to original payment method</li>
            <li><strong>Abuse Prevention:</strong> Repeated refund requests may result in account restrictions</li>
        </ul>

        <h2>4. 👤 User Obligations and Prohibited Uses</h2>
        
        <h3>4.1 You Agree To:</h3>
        <ul>
            <li>Provide accurate and up-to-date profile information</li>
            <li>Use the service for legitimate job searching purposes</li>
            <li>Respect intellectual property rights</li>
            <li>Comply with all applicable laws and regulations</li>
            <li>Maintain the confidentiality of your account credentials</li>
        </ul>

        <h3>4.2 Prohibited Activities:</h3>
        <ul>
            <li>Creating fake profiles or using false information</li>
            <li>Automated scraping or data extraction</li>
            <li>Spamming employers or other users</li>
            <li>Circumventing subscription limitations</li>
            <li>Reverse engineering our AI algorithms</li>
            <li>Using the service for illegal activities</li>
        </ul>

        <h2>5. 🛡️ Data Protection and Privacy (GDPR Compliance)</h2>
        
        <div class="highlight">
            <strong>🇪🇺 For EU Residents:</strong> We are fully committed to GDPR compliance and your privacy rights.
        </div>

        <h3>5.1 Your Rights Under GDPR:</h3>
        <ul>
            <li><strong>Right to Access:</strong> Request access to your personal data</li>
            <li><strong>Right to Rectification:</strong> Correct inaccurate personal data</li>
            <li><strong>Right to Erasure:</strong> Request deletion of your personal data</li>
            <li><strong>Right to Portability:</strong> Receive your data in a structured format</li>
            <li><strong>Right to Object:</strong> Object to processing of your personal data</li>
            <li><strong>Right to Restriction:</strong> Restrict processing of your personal data</li>
        </ul>

        <h3>5.2 Data Processing Lawful Basis:</h3>
        <ul>
            <li><strong>Contract Performance:</strong> Processing necessary for service delivery</li>
            <li><strong>Legitimate Interest:</strong> Service improvement and job matching</li>
            <li><strong>Consent:</strong> Marketing communications (opt-in only)</li>
            <li><strong>Legal Obligation:</strong> Compliance with applicable laws</li>
        </ul>

        <h2>6. 🚫 Liability and Disclaimers</h2>
        <ul>
            <li><strong>Service Availability:</strong> We strive for 99.9% uptime but cannot guarantee uninterrupted service</li>
            <li><strong>Job Accuracy:</strong> While we verify job postings, we cannot guarantee accuracy of all information</li>
            <li><strong>Employment Outcomes:</strong> We facilitate connections but do not guarantee job placement</li>
            <li><strong>Third-Party Content:</strong> Not responsible for content from external employers or partners</li>
            <li><strong>Force Majeure:</strong> Not liable for delays due to circumstances beyond our control</li>
        </ul>

        <h2>7. 📝 Account Termination</h2>
        
        <h3>7.1 You May Terminate:</h3>
        <ul>
            <li>Cancel subscription anytime through account settings</li>
            <li>Delete account and all associated data</li>
            <li>Export your data before termination</li>
        </ul>

        <h3>7.2 We May Terminate:</h3>
        <ul>
            <li>Accounts violating these terms</li>
            <li>Accounts with suspicious or fraudulent activity</li>
            <li>Accounts with repeated payment failures</li>
            <li>With 30 days notice for service changes</li>
        </ul>

        <h2>8. 🌍 International Users</h2>
        <ul>
            <li><strong>Global Service:</strong> Available worldwide except where prohibited by law</li>
            <li><strong>Local Laws:</strong> Users responsible for compliance with local employment laws</li>
            <li><strong>Currency:</strong> Pricing may vary by region</li>
            <li><strong>Tax Obligations:</strong> Users responsible for applicable taxes</li>
        </ul>

        <h2>9. 🔄 Changes to Terms</h2>
        <ul>
            <li>We may update these terms periodically</li>
            <li>Material changes will be communicated via email</li>
            <li>Continued use constitutes acceptance of updated terms</li>
            <li>Previous versions available upon request</li>
        </ul>

        <h2>10. ⚖️ Governing Law and Disputes</h2>
        <ul>
            <li><strong>Governing Law:</strong> These terms are governed by the laws of Delaware, USA</li>
            <li><strong>Dispute Resolution:</strong> First attempt good faith negotiation</li>
            <li><strong>Arbitration:</strong> Binding arbitration for unresolved disputes</li>
            <li><strong>Class Action Waiver:</strong> No class action lawsuits permitted</li>
            <li><strong>EU Users:</strong> Nothing affects your statutory rights under EU law</li>
        </ul>

        <div class="contact">
            <h2>📞 Contact Information</h2>
            <p>For questions about these Terms and Conditions:</p>
            <ul>
                <li><strong>Email:</strong> legal@buzz2remote.com</li>
                <li><strong>Address:</strong> Buzz2Remote, Inc., 123 Remote Work Blvd, San Francisco, CA 94105, USA</li>
                <li><strong>Response Time:</strong> We respond to all inquiries within 48 hours</li>
                <li><strong>EU Representative:</strong> For EU-specific matters, contact gdpr@buzz2remote.com</li>
            </ul>
        </div>

        <div class="highlight">
            <p><strong>🤝 Thank you for choosing Buzz2Remote!</strong></p>
            <p>We're committed to helping you find your perfect remote opportunity while protecting your rights and privacy every step of the way.</p>
        </div>

        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 0.9em;">
            <p>© {datetime.now().year} Buzz2Remote, Inc. All rights reserved. | Version {TERMS_VERSION} | Last Updated: {LAST_UPDATED}</p>
        </footer>
    </body>
    </html>
    """
    
    return html_content

@router.get("/privacy", response_class=HTMLResponse)
async def get_privacy_policy():
    """
    **Privacy Policy Page**
    
    Comprehensive privacy policy with detailed GDPR compliance information,
    data processing procedures, and user rights protection.
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Privacy Policy - Buzz2Remote</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 40px; max-width: 800px; margin: 0 auto; color: #333; }}
            h1 {{ color: #2d3748; border-bottom: 3px solid #4299e1; padding-bottom: 10px; }}
            h2 {{ color: #4a5568; margin-top: 30px; }}
            h3 {{ color: #718096; }}
            .highlight {{ background-color: #ebf8ff; padding: 15px; border-left: 4px solid #4299e1; margin: 20px 0; }}
            .important {{ background-color: #fed7d7; padding: 15px; border-left: 4px solid #e53e3e; margin: 20px 0; }}
            .gdpr {{ background-color: #f0fff4; padding: 15px; border-left: 4px solid #38a169; margin: 20px 0; }}
            .contact {{ background-color: #e6fffa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            ul, ol {{ padding-left: 20px; }}
            li {{ margin: 8px 0; }}
            .version {{ color: #718096; font-size: 0.9em; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
            th {{ background-color: #f7fafc; font-weight: 600; }}
        </style>
    </head>
    <body>
        <h1>🔒 Buzz2Remote - Privacy Policy</h1>
        
        <div class="version">
            <strong>Version:</strong> {PRIVACY_VERSION} | <strong>Last Updated:</strong> {LAST_UPDATED}
        </div>

        <div class="highlight">
            <strong>🛡️ Privacy Commitment:</strong> Your privacy is fundamental to our service. This policy explains 
            how we collect, use, and protect your personal information in full compliance with GDPR and international privacy laws.
        </div>

        <h2>1. 📊 Information We Collect</h2>
        
        <h3>1.1 Information You Provide</h3>
        <table>
            <thead>
                <tr>
                    <th>Data Type</th>
                    <th>Examples</th>
                    <th>Purpose</th>
                    <th>Legal Basis (GDPR)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Account Information</strong></td>
                    <td>Name, email, password</td>
                    <td>Account creation and authentication</td>
                    <td>Contract Performance</td>
                </tr>
                <tr>
                    <td><strong>Profile Data</strong></td>
                    <td>Skills, experience, education</td>
                    <td>Job matching and recommendations</td>
                    <td>Contract Performance</td>
                </tr>
                <tr>
                    <td><strong>Contact Information</strong></td>
                    <td>Phone, address, LinkedIn profile</td>
                    <td>Communication and verification</td>
                    <td>Legitimate Interest</td>
                </tr>
                <tr>
                    <td><strong>Payment Information</strong></td>
                    <td>Credit card details, billing address</td>
                    <td>Subscription processing</td>
                    <td>Contract Performance</td>
                </tr>
                <tr>
                    <td><strong>CV/Resume Data</strong></td>
                    <td>Work history, qualifications</td>
                    <td>Enhanced job matching</td>
                    <td>Consent</td>
                </tr>
            </tbody>
        </table>

        <h3>1.2 Information We Automatically Collect</h3>
        <ul>
            <li><strong>Usage Data:</strong> Pages visited, features used, time spent</li>
            <li><strong>Device Information:</strong> Browser type, operating system, device identifiers</li>
            <li><strong>Location Data:</strong> IP address for regional job matching (with consent)</li>
            <li><strong>Cookies and Tracking:</strong> Essential for functionality, analytics with consent</li>
        </ul>

        <h3>1.3 Information from Third Parties</h3>
        <ul>
            <li><strong>OAuth Providers:</strong> Google, LinkedIn authentication data</li>
            <li><strong>Job Boards:</strong> Public job posting information</li>
            <li><strong>Social Media:</strong> Public profile information (when you connect accounts)</li>
        </ul>

        <h2>2. 🎯 How We Use Your Information</h2>

        <h3>2.1 Primary Service Functions</h3>
        <ul>
            <li><strong>AI Job Matching:</strong> Analyzing your profile to suggest relevant opportunities</li>
            <li><strong>Account Management:</strong> Providing access to your personalized dashboard</li>
            <li><strong>Communication:</strong> Sending job alerts, updates, and support responses</li>
            <li><strong>Payment Processing:</strong> Managing subscriptions and billing</li>
            <li><strong>Customer Support:</strong> Resolving issues and providing assistance</li>
        </ul>

        <h3>2.2 Service Improvement</h3>
        <ul>
            <li><strong>Analytics:</strong> Understanding user behavior to improve features</li>
            <li><strong>A/B Testing:</strong> Testing new features and improvements</li>
            <li><strong>AI Training:</strong> Improving matching algorithms (anonymized data only)</li>
            <li><strong>Performance Monitoring:</strong> Ensuring optimal service performance</li>
        </ul>

        <h3>2.3 Legal and Security Purposes</h3>
        <ul>
            <li><strong>Fraud Prevention:</strong> Detecting and preventing unauthorized access</li>
            <li><strong>Legal Compliance:</strong> Meeting regulatory requirements</li>
            <li><strong>Safety:</strong> Protecting users from harmful content or behavior</li>
        </ul>

        <div class="gdpr">
            <h2>3. 🇪🇺 GDPR Rights (EU Residents)</h2>
            
            <h3>3.1 Your Data Rights</h3>
            <ul>
                <li><strong>Right of Access (Article 15):</strong> Get a copy of your personal data</li>
                <li><strong>Right to Rectification (Article 16):</strong> Correct inaccurate data</li>
                <li><strong>Right to Erasure (Article 17):</strong> Delete your personal data</li>
                <li><strong>Right to Restrict Processing (Article 18):</strong> Limit how we use your data</li>
                <li><strong>Right to Data Portability (Article 20):</strong> Transfer your data to another service</li>
                <li><strong>Right to Object (Article 21):</strong> Object to certain types of processing</li>
            </ul>

            <h3>3.2 How to Exercise Your Rights</h3>
            <ul>
                <li><strong>Email:</strong> gdpr@buzz2remote.com</li>
                <li><strong>Response Time:</strong> Within 30 days (may extend to 60 days for complex requests)</li>
                <li><strong>Verification:</strong> We may request identity verification for security</li>
                <li><strong>Free of Charge:</strong> Exercising rights is free (except for excessive requests)</li>
            </ul>

            <h3>3.3 Data Protection Officer</h3>
            <p>Our Data Protection Officer oversees GDPR compliance:</p>
            <ul>
                <li><strong>Email:</strong> dpo@buzz2remote.com</li>
                <li><strong>Role:</strong> Ensures privacy compliance and handles data protection inquiries</li>
            </ul>
        </div>

        <h2>4. 🔄 Data Sharing and Disclosure</h2>

        <h3>4.1 We DO NOT Sell Your Personal Data</h3>
        <div class="important">
            <strong>⚠️ Important:</strong> We never sell, rent, or trade your personal information to third parties for their marketing purposes.
        </div>

        <h3>4.2 When We Share Data</h3>
        <ul>
            <li><strong>With Your Consent:</strong> When you explicitly authorize sharing</li>
            <li><strong>Service Providers:</strong> Trusted partners who help us operate our service
                <ul>
                    <li>Payment processors (Stripe, PayPal)</li>
                    <li>Email service providers (SendGrid)</li>
                    <li>Analytics providers (Google Analytics - anonymized)</li>
                    <li>Cloud hosting providers (AWS, Google Cloud)</li>
                </ul>
            </li>
            <li><strong>Legal Requirements:</strong> When required by law or legal process</li>
            <li><strong>Business Transfers:</strong> In case of merger, acquisition, or sale (with notice)</li>
            <li><strong>Safety and Security:</strong> To protect rights, safety, or property</li>
        </ul>

        <h3>4.3 International Data Transfers</h3>
        <ul>
            <li><strong>Adequacy Decisions:</strong> We transfer data to countries with adequate protection</li>
            <li><strong>Safeguards:</strong> Standard contractual clauses for other transfers</li>
            <li><strong>Data Localization:</strong> EU data processed within EU when possible</li>
        </ul>

        <h2>5. 🛡️ Data Security and Retention</h2>

        <h3>5.1 Security Measures</h3>
        <ul>
            <li><strong>Encryption:</strong> Data encrypted in transit (TLS 1.3) and at rest (AES-256)</li>
            <li><strong>Access Controls:</strong> Role-based access with multi-factor authentication</li>
            <li><strong>Regular Audits:</strong> Security assessments and penetration testing</li>
            <li><strong>Incident Response:</strong> 24/7 monitoring and rapid response procedures</li>
            <li><strong>Staff Training:</strong> Regular privacy and security training for all employees</li>
        </ul>

        <h3>5.2 Data Retention Periods</h3>
        <table>
            <thead>
                <tr>
                    <th>Data Type</th>
                    <th>Retention Period</th>
                    <th>Reason</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Account Information</td>
                    <td>Until account deletion + 30 days</td>
                    <td>Service provision and security</td>
                </tr>
                <tr>
                    <td>Profile Data</td>
                    <td>Until account deletion</td>
                    <td>Job matching functionality</td>
                </tr>
                <tr>
                    <td>Payment Information</td>
                    <td>7 years after last transaction</td>
                    <td>Tax and legal requirements</td>
                </tr>
                <tr>
                    <td>Usage Analytics</td>
                    <td>26 months (anonymized after 14 months)</td>
                    <td>Service improvement</td>
                </tr>
                <tr>
                    <td>Support Tickets</td>
                    <td>3 years</td>
                    <td>Quality assurance and training</td>
                </tr>
            </tbody>
        </table>

        <h2>6. 🍪 Cookies and Tracking</h2>

        <h3>6.1 Types of Cookies We Use</h3>
        <ul>
            <li><strong>Essential Cookies:</strong> Required for basic functionality (no consent needed)</li>
            <li><strong>Functional Cookies:</strong> Remember your preferences (with consent)</li>
            <li><strong>Analytics Cookies:</strong> Help us understand usage patterns (with consent)</li>
            <li><strong>Marketing Cookies:</strong> Personalize content and ads (with explicit consent)</li>
        </ul>

        <h3>6.2 Cookie Management</h3>
        <ul>
            <li><strong>Cookie Banner:</strong> Clear options to accept or reject non-essential cookies</li>
            <li><strong>Cookie Settings:</strong> Granular control in your account preferences</li>
            <li><strong>Browser Controls:</strong> You can also manage cookies through browser settings</li>
        </ul>

        <h2>7. 👶 Children's Privacy</h2>
        <ul>
            <li><strong>Age Requirement:</strong> Our service is intended for users 16 years and older</li>
            <li><strong>No Collection:</strong> We do not knowingly collect data from children under 16</li>
            <li><strong>Parental Rights:</strong> Parents can request deletion of child's data</li>
            <li><strong>Verification:</strong> We may verify age before account creation</li>
        </ul>

        <h2>8. 🔔 Changes to Privacy Policy</h2>
        <ul>
            <li><strong>Notification:</strong> Material changes communicated via email and in-app notices</li>
            <li><strong>Effective Date:</strong> Changes take effect 30 days after notification</li>
            <li><strong>Consent:</strong> Continued use implies acceptance (explicit consent for significant changes)</li>
            <li><strong>Version History:</strong> Previous versions available upon request</li>
        </ul>

        <div class="contact">
            <h2>📞 Privacy Contact Information</h2>
            
            <h3>General Privacy Inquiries:</h3>
            <ul>
                <li><strong>Email:</strong> privacy@buzz2remote.com</li>
                <li><strong>Response Time:</strong> Within 48 hours for general inquiries</li>
            </ul>

            <h3>GDPR and EU-Specific Matters:</h3>
            <ul>
                <li><strong>Email:</strong> gdpr@buzz2remote.com</li>
                <li><strong>DPO:</strong> dpo@buzz2remote.com</li>
                <li><strong>Response Time:</strong> Within 30 days (GDPR requirement)</li>
            </ul>

            <h3>Data Security Incidents:</h3>
            <ul>
                <li><strong>Email:</strong> security@buzz2remote.com</li>
                <li><strong>Response Time:</strong> Immediate acknowledgment, investigation within 24 hours</li>
            </ul>

            <h3>Postal Address:</h3>
            <p>Buzz2Remote, Inc.<br>
            Attn: Privacy Team<br>
            123 Remote Work Blvd<br>
            San Francisco, CA 94105<br>
            United States</p>
        </div>

        <h2>9. 🏛️ Supervisory Authority</h2>
        <p>EU residents have the right to lodge a complaint with their local supervisory authority if they believe their data protection rights have been violated.</p>

        <div class="highlight">
            <h2>🤝 Our Privacy Commitment</h2>
            <p>We believe privacy is a fundamental right. Our commitment includes:</p>
            <ul>
                <li><strong>Transparency:</strong> Clear communication about our data practices</li>
                <li><strong>Control:</strong> Giving you meaningful choices about your data</li>
                <li><strong>Security:</strong> Implementing industry-leading security measures</li>
                <li><strong>Accountability:</strong> Taking responsibility for protecting your privacy</li>
                <li><strong>Innovation:</strong> Continuously improving our privacy practices</li>
            </ul>
        </div>

        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 0.9em;">
            <p>© {datetime.now().year} Buzz2Remote, Inc. All rights reserved. | Version {PRIVACY_VERSION} | Last Updated: {LAST_UPDATED}</p>
            <p><strong>Questions?</strong> We're here to help with any privacy-related questions at privacy@buzz2remote.com</p>
        </footer>
    </body>
    </html>
    """
    
    return html_content

@router.get("/cookie-policy", response_class=HTMLResponse)
async def get_cookie_policy():
    """
    **Cookie Policy Page**
    
    Detailed cookie policy with GDPR compliance and granular cookie management options.
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cookie Policy - Buzz2Remote</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 40px; max-width: 800px; margin: 0 auto; color: #333; }}
            h1 {{ color: #2d3748; border-bottom: 3px solid #ed8936; padding-bottom: 10px; }}
            h2 {{ color: #4a5568; margin-top: 30px; }}
            h3 {{ color: #718096; }}
            .highlight {{ background-color: #fef5e7; padding: 15px; border-left: 4px solid #ed8936; margin: 20px 0; }}
            .important {{ background-color: #fed7d7; padding: 15px; border-left: 4px solid #e53e3e; margin: 20px 0; }}
            .cookie-table {{ background-color: #f7fafc; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .contact {{ background-color: #e6fffa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            ul, ol {{ padding-left: 20px; }}
            li {{ margin: 8px 0; }}
            .version {{ color: #718096; font-size: 0.9em; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
            th {{ background-color: #f7fafc; font-weight: 600; }}
            .cookie-toggle {{ background: #48bb78; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }}
            .cookie-toggle.disabled {{ background: #e53e3e; }}
            .consent-controls {{ background: #ebf8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>🍪 Buzz2Remote - Cookie Policy</h1>
        
        <div class="version">
            <strong>Version:</strong> {PRIVACY_VERSION} | <strong>Last Updated:</strong> {LAST_UPDATED}
        </div>

        <div class="highlight">
            <strong>🍪 Cookie Summary:</strong> We use cookies to provide essential functionality, 
            enhance your experience, and analyze usage patterns. You have full control over non-essential cookies.
        </div>

        <h2>1. 🎯 What Are Cookies?</h2>
        <p>Cookies are small text files stored on your device when you visit websites. They help websites remember your preferences, keep you logged in, and provide personalized experiences.</p>

        <h3>1.1 Types of Cookies We Use</h3>
        <ul>
            <li><strong>Session Cookies:</strong> Temporary cookies that expire when you close your browser</li>
            <li><strong>Persistent Cookies:</strong> Remain on your device for a set period or until deleted</li>
            <li><strong>First-Party Cookies:</strong> Set directly by Buzz2Remote</li>
            <li><strong>Third-Party Cookies:</strong> Set by external services we use (with your consent)</li>
        </ul>

        <h2>2. 🔧 Cookies We Use</h2>

        <div class="cookie-table">
            <h3>Essential Cookies (Always Active)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Cookie Name</th>
                        <th>Purpose</th>
                        <th>Expires</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>access_token</code></td>
                        <td>User authentication and session management</td>
                        <td>30 days (if "Remember Me" enabled)</td>
                        <td>HTTP-Only, Secure</td>
                    </tr>
                    <tr>
                        <td><code>session_id</code></td>
                        <td>Admin panel session management</td>
                        <td>Session</td>
                        <td>HTTP-Only, Secure</td>
                    </tr>
                    <tr>
                        <td><code>csrf_token</code></td>
                        <td>Security protection against cross-site attacks</td>
                        <td>Session</td>
                        <td>Secure</td>
                    </tr>
                    <tr>
                        <td><code>cookie_consent</code></td>
                        <td>Remember your cookie preferences</td>
                        <td>1 year</td>
                        <td>Persistent</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="cookie-table">
            <h3>Functional Cookies (Optional)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Cookie Name</th>
                        <th>Purpose</th>
                        <th>Expires</th>
                        <th>Third Party</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>user_preferences</code></td>
                        <td>Remember your language, theme, and display preferences</td>
                        <td>6 months</td>
                        <td>No</td>
                    </tr>
                    <tr>
                        <td><code>job_search_filters</code></td>
                        <td>Save your recent job search criteria</td>
                        <td>30 days</td>
                        <td>No</td>
                    </tr>
                    <tr>
                        <td><code>location_preferences</code></td>
                        <td>Remember your preferred job locations</td>
                        <td>90 days</td>
                        <td>No</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="cookie-table">
            <h3>Analytics Cookies (Optional)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Purpose</th>
                        <th>Cookies Set</th>
                        <th>Privacy Policy</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Google Analytics 4</strong></td>
                        <td>Website usage analysis, user behavior insights</td>
                        <td>_ga, _ga_*, _gid</td>
                        <td><a href="https://policies.google.com/privacy" target="_blank">Google Privacy Policy</a></td>
                    </tr>
                    <tr>
                        <td><strong>Hotjar</strong></td>
                        <td>User experience analysis, heatmaps</td>
                        <td>_hjSessionUser_*, _hjSession_*</td>
                        <td><a href="https://www.hotjar.com/legal/policies/privacy/" target="_blank">Hotjar Privacy Policy</a></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="cookie-table">
            <h3>Marketing Cookies (Optional)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Purpose</th>
                        <th>Cookies Set</th>
                        <th>Privacy Policy</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Google Ads</strong></td>
                        <td>Personalized advertising, conversion tracking</td>
                        <td>_gcl_*, _gac_*</td>
                        <td><a href="https://policies.google.com/privacy" target="_blank">Google Privacy Policy</a></td>
                    </tr>
                    <tr>
                        <td><strong>Facebook Pixel</strong></td>
                        <td>Social media advertising, audience insights</td>
                        <td>_fbp, _fbc</td>
                        <td><a href="https://www.facebook.com/privacy/policy/" target="_blank">Facebook Privacy Policy</a></td>
                    </tr>
                    <tr>
                        <td><strong>LinkedIn Insight</strong></td>
                        <td>Professional network advertising</td>
                        <td>bcookie, bscookie</td>
                        <td><a href="https://www.linkedin.com/legal/privacy-policy" target="_blank">LinkedIn Privacy Policy</a></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <h2>3. 🎛️ Cookie Management & Your Choices</h2>

        <div class="consent-controls">
            <h3>Manage Your Cookie Preferences</h3>
            <p>You can control which cookies we use. Essential cookies cannot be disabled as they're required for basic functionality.</p>
            
            <table style="margin-top: 15px;">
                <tr>
                    <td><strong>Essential Cookies</strong></td>
                    <td>Always Active</td>
                    <td><span style="background: #48bb78; color: white; padding: 4px 8px; border-radius: 4px;">Required</span></td>
                </tr>
                <tr>
                    <td><strong>Functional Cookies</strong></td>
                    <td>Enhance your experience</td>
                    <td><button class="cookie-toggle" onclick="toggleCookies('functional')">Enable</button></td>
                </tr>
                <tr>
                    <td><strong>Analytics Cookies</strong></td>
                    <td>Help us improve our service</td>
                    <td><button class="cookie-toggle" onclick="toggleCookies('analytics')">Enable</button></td>
                </tr>
                <tr>
                    <td><strong>Marketing Cookies</strong></td>
                    <td>Personalized advertising</td>
                    <td><button class="cookie-toggle" onclick="toggleCookies('marketing')">Enable</button></td>
                </tr>
            </table>
            
            <p style="margin-top: 15px;"><small>Changes take effect immediately. Some features may be limited if certain cookies are disabled.</small></p>
        </div>

        <h2>4. 🌐 Browser Cookie Controls</h2>

        <h3>4.1 Managing Cookies in Your Browser</h3>
        <ul>
            <li><strong>Chrome:</strong> Settings > Privacy and Security > Cookies and other site data</li>
            <li><strong>Firefox:</strong> Settings > Privacy & Security > Cookies and Site Data</li>
            <li><strong>Safari:</strong> Preferences > Privacy > Manage Website Data</li>
            <li><strong>Edge:</strong> Settings > Cookies and site permissions > Cookies and site data</li>
        </ul>

        <h3>4.2 Global Privacy Controls</h3>
        <ul>
            <li><strong>Do Not Track:</strong> We respect DNT browser signals</li>
            <li><strong>Global Privacy Control (GPC):</strong> Automatically respected</li>
            <li><strong>Cookie Banners:</strong> Control preferences directly on our site</li>
        </ul>

        <h2>5. 🛡️ Cookie Security & Privacy</h2>

        <h3>5.1 Security Measures</h3>
        <ul>
            <li><strong>Secure Flag:</strong> Cookies transmitted only over HTTPS</li>
            <li><strong>HttpOnly Flag:</strong> Prevents JavaScript access to authentication cookies</li>
            <li><strong>SameSite Attribute:</strong> Protects against cross-site request forgery</li>
            <li><strong>Encryption:</strong> Sensitive cookie data is encrypted</li>
        </ul>

        <h3>5.2 Data Retention</h3>
        <ul>
            <li><strong>Session Cookies:</strong> Deleted when browser closes</li>
            <li><strong>Persistent Cookies:</strong> Automatically expire after set period</li>
            <li><strong>Manual Deletion:</strong> Users can delete cookies anytime</li>
            <li><strong>Account Deletion:</strong> All associated cookies invalidated</li>
        </ul>

        <h2>6. 🇪🇺 GDPR & International Compliance</h2>

        <div class="important">
            <h3>Your Rights Under GDPR</h3>
            <ul>
                <li><strong>Consent:</strong> We ask for explicit consent before setting non-essential cookies</li>
                <li><strong>Withdraw Consent:</strong> You can withdraw consent anytime</li>
                <li><strong>Data Access:</strong> Request information about cookies and data collected</li>
                <li><strong>Data Portability:</strong> Export your cookie preferences</li>
                <li><strong>Right to Object:</strong> Object to cookie-based processing</li>
            </ul>
        </div>

        <h3>6.1 Legal Basis for Cookie Processing</h3>
        <table>
            <thead>
                <tr>
                    <th>Cookie Type</th>
                    <th>Legal Basis</th>
                    <th>GDPR Article</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Essential Cookies</td>
                    <td>Legitimate Interest</td>
                    <td>Article 6(1)(f)</td>
                </tr>
                <tr>
                    <td>Functional Cookies</td>
                    <td>Consent</td>
                    <td>Article 6(1)(a)</td>
                </tr>
                <tr>
                    <td>Analytics Cookies</td>
                    <td>Consent</td>
                    <td>Article 6(1)(a)</td>
                </tr>
                <tr>
                    <td>Marketing Cookies</td>
                    <td>Consent</td>
                    <td>Article 6(1)(a)</td>
                </tr>
            </tbody>
        </table>

        <h2>7. 🔄 Third-Party Services</h2>

        <h3>7.1 Authentication Services</h3>
        <ul>
            <li><strong>Google OAuth:</strong> Sign in with Google (sets authentication cookies)</li>
            <li><strong>LinkedIn OAuth:</strong> Sign in with LinkedIn (sets authentication cookies)</li>
            <li><strong>GitHub OAuth:</strong> Sign in with GitHub (sets authentication cookies)</li>
        </ul>

        <h3>7.2 Analytics & Monitoring</h3>
        <ul>
            <li><strong>Google Analytics:</strong> Website usage analytics (optional)</li>
            <li><strong>Hotjar:</strong> User experience insights (optional)</li>
            <li><strong>Sentry:</strong> Error monitoring (essential for service reliability)</li>
        </ul>

        <h3>7.3 Payment Processing</h3>
        <ul>
            <li><strong>Stripe:</strong> Secure payment processing (essential for subscriptions)</li>
            <li><strong>PayPal:</strong> Alternative payment method (essential when used)</li>
        </ul>

        <h2>8. 📱 Mobile App Cookies</h2>
        <p>Our mobile applications may use similar tracking technologies:</p>
        <ul>
            <li><strong>Mobile SDKs:</strong> Analytics and crash reporting</li>
            <li><strong>Push Notifications:</strong> Device tokens for job alerts</li>
            <li><strong>Local Storage:</strong> App preferences and cached data</li>
            <li><strong>Advertising IDs:</strong> Personalized advertising (with consent)</li>
        </ul>

        <h2>9. 🔔 Updates to Cookie Policy</h2>
        <ul>
            <li><strong>Notification:</strong> We'll notify you of significant changes via email</li>
            <li><strong>Consent Refresh:</strong> You may need to update cookie preferences</li>
            <li><strong>Version History:</strong> Previous versions available upon request</li>
            <li><strong>Effective Date:</strong> Changes take effect 30 days after notification</li>
        </ul>

        <div class="contact">
            <h2>📞 Cookie Policy Contact</h2>
            <p>Questions about our cookie usage?</p>
            <ul>
                <li><strong>Email:</strong> cookies@buzz2remote.com</li>
                <li><strong>Privacy Team:</strong> privacy@buzz2remote.com</li>
                <li><strong>GDPR Officer:</strong> dpo@buzz2remote.com</li>
                <li><strong>Response Time:</strong> Within 48 hours</li>
            </ul>
        </div>

        <div class="highlight">
            <h2>🎯 Cookie Preferences Center</h2>
            <p>Want to change your cookie settings? Visit our <a href="/cookie-preferences" style="color: #ed8936; font-weight: bold;">Cookie Preferences Center</a> anytime to:</p>
            <ul>
                <li>Enable or disable cookie categories</li>
                <li>View detailed cookie information</li>
                <li>Export your preferences</li>
                <li>Clear all cookies and data</li>
            </ul>
        </div>

        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 0.9em;">
            <p>© {datetime.now().year} Buzz2Remote, Inc. All rights reserved. | Version {PRIVACY_VERSION} | Last Updated: {LAST_UPDATED}</p>
            <p><strong>🍪 Remember:</strong> Your privacy matters to us. You're always in control of your data and cookie preferences.</p>
        </footer>

        <script>
            function toggleCookies(type) {{
                const button = event.target;
                const isEnabled = !button.classList.contains('disabled');
                
                if (isEnabled) {{
                    button.textContent = 'Disabled';
                    button.classList.add('disabled');
                    // Set cookie preference
                    document.cookie = `cookies_${{type}}=false; path=/; max-age=31536000`;
                }} else {{
                    button.textContent = 'Enabled';
                    button.classList.remove('disabled');
                    // Set cookie preference
                    document.cookie = `cookies_${{type}}=true; path=/; max-age=31536000`;
                }}
                
                // In a real implementation, this would reload page or update tracking scripts
                console.log(`${{type}} cookies: ${{!isEnabled ? 'enabled' : 'disabled'}}`);
            }}
            
            // Load current preferences on page load
            document.addEventListener('DOMContentLoaded', function() {{
                const types = ['functional', 'analytics', 'marketing'];
                types.forEach(type => {{
                    const cookieValue = getCookie(`cookies_${{type}}`);
                    const button = document.querySelector(`button[onclick="toggleCookies('${{type}}')"]`);
                    if (cookieValue === 'false') {{
                        button.textContent = 'Disabled';
                        button.classList.add('disabled');
                    }}
                }});
            }});
            
            function getCookie(name) {{
                const value = `; ${{document.cookie}}`;
                const parts = value.split(`; ${{name}}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content

@router.get("/gdpr-info")
async def get_gdpr_info():
    """GDPR Rights Information (JSON format)"""
    return {
        "gdpr_rights": {
            "right_of_access": {
                "description": "Request access to your personal data",
                "how_to_exercise": "Email gdpr@buzz2remote.com",
                "response_time": "30 days"
            },
            "right_to_rectification": {
                "description": "Correct inaccurate personal data",
                "how_to_exercise": "Update in account settings or email gdpr@buzz2remote.com",
                "response_time": "30 days"
            },
            "right_to_erasure": {
                "description": "Request deletion of your personal data",
                "how_to_exercise": "Delete account or email gdpr@buzz2remote.com",
                "response_time": "30 days"
            },
            "right_to_portability": {
                "description": "Receive your data in structured format",
                "how_to_exercise": "Email gdpr@buzz2remote.com with export request",
                "response_time": "30 days"
            },
            "right_to_object": {
                "description": "Object to processing of your personal data",
                "how_to_exercise": "Email gdpr@buzz2remote.com",
                "response_time": "30 days"
            }
        },
        "contact": {
            "dpo_email": "dpo@buzz2remote.com",
            "gdpr_email": "gdpr@buzz2remote.com",
            "general_privacy": "privacy@buzz2remote.com"
        }
    } 