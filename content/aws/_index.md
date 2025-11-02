+++
title = "AWS Cloud Practitioner Notes — Core Concepts Explained Simply"
date = 2025-11-02
draft = false
tags = ["aws"]
+++

# AWS Cloud Practitioner Core Concepts Explained Simply
 
## EC2 vs Lambda

### EC2 (Elastic Compute Cloud)
- A virtual server in the cloud.
- You choose CPU, RAM, and Operating System.
- **You pay while it is running**, even if idle.
- You are responsible for configuration and maintenance.

**Use when:**  
The application must stay running continuously with stable, predictable traffic.

**Analogy:**  
Like renting an apartment: you pay for it even when you’re not there.

---

### Lambda (AWS Lambda)
- You write **functions**, not servers.
- AWS manages the underlying infrastructure.
- **Runs only when triggered.**
- **You pay only for execution time**.

**Use when:**  
Workloads are event-based or have variable traffic patterns.

**Analogy:**  
Like taking a taxi: you pay only when you use it.

---

## RDS vs DynamoDB

### RDS (Relational Database Service)
- SQL relational databases (e.g., PostgreSQL, MySQL).
- Structured tables with relationships.
- Good when data integrity and relations matter.

**Use for:**  
E-commerce, CRMs, financial systems, and traditional business applications.

---

### DynamoDB
- NoSQL key-value and document database.
- Automatically scales to very high loads.
- Very fast read/write performance.

**Use for:**  
High-traffic systems like gaming, IoT apps, chats, session data.

---

## S3 Storage Classes (Simplified)

| Storage Class | Meaning | Best Use Case | Cost |
|--------------|---------|---------------|------|
| **S3 Standard** | Frequently accessed data | Active files and assets | Medium |
| **S3 Infrequent Access (IA)** | Occasionally accessed data | Backups / archives accessed sometimes | Lower (reads cost extra) |
| **S3 Glacier** | Long-term storage | Archives that rarely need retrieval | Very low (retrieval is slow) |

**Key idea:**  
- Standard = frequent  
- IA = occasional  
- Glacier = long-term archive

---

## CloudWatch vs CloudTrail

| Service | Purpose | Think of it as… |
|--------|---------|----------------|
| **CloudWatch** | Metrics, logs, performance monitoring | Dashboard of how the system runs |
| **CloudTrail** | Records *who did what* in the AWS account | Security camera for user actions |

**Summary:**  
- CloudWatch → System behavior  
- CloudTrail → User and API actions

---

## VPC Basics

A **Virtual Private Cloud (VPC)** is your network space in AWS.

### Subnet
A segment of the VPC network.
- **Public subnets** allow access from the internet.
- **Private subnets** are isolated and internal.

### Security Group (SG)
Rules applied **to an instance**.
- Controls *who can connect in or out*.
- Stateful: if traffic is allowed in, return traffic is automatically allowed out.

### Network ACL (NACL)
Rules applied **to a subnet**.
- Can explicitly allow or deny traffic.
- Stateless: inbound and outbound rules must be configured separately.

**Analogy:**
- Subnet = neighborhood
- Security Group = lock/guard on your house
- NACL = gate rules for the entire neighborhood
 