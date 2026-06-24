# Security Policy

## Supported Versions

This repository is pre-1.0. Security fixes target the current `main` branch.

## Reporting A Vulnerability

Do not open public issues with real merchant data, customer data, access tokens, or marketplace credentials.

For private reporting, contact the repository maintainer through the profile email listed on GitHub. Include:

- A short description of the issue
- Reproduction steps using synthetic data
- Impact assessment
- Suggested mitigation, if known

## Data Handling

ShopSheet is local-first. The repository uses synthetic examples only and should not contain:

- Real merchant exports
- Customer phone numbers or addresses
- Marketplace tokens
- Payment credentials
- Private business reports

## Current Security Boundary

The current app is intended for local development and portfolio demonstration. It does not provide authentication, multi-user tenancy, or internet-facing hardening.
