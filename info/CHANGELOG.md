# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Desktop packaging with PyInstaller
- GitHub Actions workflow for automated releases
- Cross-platform builds (macOS, Windows, Linux)
- Downloads page auto-refresh functionality

### Changed
- Consolidated password hashing to bcrypt with legacy SHA-256 migration
- Enhanced security headers and CSRF protection
- Improved rate limiting with environment-driven configuration

### Fixed
- Structured logging implementation
- Health check endpoints with version information
- Request ID propagation across all logs

### Security
- Added Content Security Policy (CSP) headers
- Implemented CSRF token validation
- Enhanced session security with secure cookies
- Added Sentry error tracking integration

## [0.1.0] - 2024-12-19

### Added
- Desktop packaging with PyInstaller for macOS, Windows, and Linux
- Security headers middleware with CSP and HSTS
- Bcrypt password hashing with automatic legacy SHA-256 migration
- CSRF protection with JSON error handling
- Environment-driven rate limiting configuration
- Sentry error tracking integration
- Comprehensive smoke test suite
- Render deployment validation script
- GitHub Actions workflow for automated desktop app releases
- Downloads page with auto-refresh functionality
- Release drafter for automated changelog generation

### Changed
- Unified password hashing across all authentication endpoints
- Enhanced logging with structured JSON output in production
- Improved health check endpoints with version information
- Consolidated security configuration

### Fixed
- Request ID propagation in all log entries
- Rate limiting exemptions for media endpoints
- CSRF token validation for API endpoints
- Database connection handling in health checks

### Security
- Added comprehensive security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Implemented Content Security Policy with violation reporting
- Enhanced session security with secure cookie settings
- Added Sentry integration for production error tracking
- Consolidated authentication with bcrypt password hashing
