# AWS Config & Network Firewall Lab
**AWS Certified Cloud Practitioner / Associate Level**  
Learn AWS Config compliance monitoring and Network Firewall security controls through the AWS Management Console.

---

## Lab Overview
Build a comprehensive security and compliance system that:
1. **Monitors S3 compliance** with AWS Config and automatic remediation
2. **Controls network traffic** with AWS Network Firewall to block specific DNS resolvers

**Architecture Flow:**
- S3 Bucket → AWS Config → Compliance Rule → Auto Remediation
- Private EC2 → Network Firewall → NAT Gateway → Internet (with DNS blocking)

---

## Prerequisites
- AWS account with Administrator access
- **Web browser** with access to AWS Management Console
- **Region**: All tasks must be done in **us-west-2** for consistency

---

## Task 1: AWS Config Setup and S3 Compliance

### Step 1: Enable AWS Config
1. **Navigate** to AWS Config service
2. **Click** "Get started"
3. **Resource types to record**: Choose specific resource types
4. **Select** "AWS S3 Bucket" from the list
5. **Recording frequency**: Continuous
6. **AWS Config role**: Select "Create AWS Config service-linked role"
7. **Delivery channel**: Keep default settings
8. **Click "Next"**

### Step 2: Add Managed Config Rule
1. **Click** "Add rule"
2. **Search** for "s3-bucket-versioning-enabled"
3. **Select** the rule and click "Next"
4. **Keep** default parameters
5. **Click "Save"**

### Step 3: Create Test S3 Bucket (Without Versioning)
1. **Navigate** to S3 service
2. **Click** "Create bucket"
3. **Bucket name**: `config-test-bucket-[YOUR-INITIALS]-[RANDOM-NUMBER]`
4. **Region**: us-west-2
5. **Versioning**: Keep disabled (default)
6. **Click "Create bucket"**

### Step 4: Verify Config Detection
1. **Navigate** back to AWS Config
2. **Click** "Rules" in left panel
3. **Wait** 5-10 minutes for evaluation
4. **Verify** your bucket appears as "Noncompliant"

### Step 5: Create IAM Role for Remediation
1. **Navigate** to IAM service
2. **Click** "Roles" → "Create role"
3. **Select** "AWS service" → "Systems Manager"
4. **Click "Next"** → **Attach policies**:
   - Search and select `AmazonS3FullAccess`
5. **Role name**: `Config-S3-Remediation-Role`
6. **Click "Create role"**

### Step 6: Setup Automatic Remediation
1. **Navigate** back to AWS Config → Rules
2. **Click** on "s3-bucket-versioning-enabled" rule
3. **Click** "Actions" → "Manage remediation"
4. **Remediation action**: Select "AWS-ConfigureS3BucketVersioning"
5. **Parameters**:
   - **BucketName**: Your bucket name
   - **AutomationAssumeRole**: `arn:aws:iam::ACCOUNT-ID:role/Config-S3-Remediation-Role`
     (Replace ACCOUNT-ID with your AWS account ID)
6. **Click "Save"**

### Step 7: Verify Automatic Remediation
1. **Wait** 5-10 minutes for remediation to execute
2. **Navigate** to S3 service
3. **Click** on your bucket
4. **Click** "Properties" tab
5. **Verify** "Bucket Versioning" is now "Enabled"
6. **Navigate** back to Config Rules
7. **Verify** bucket status changed to "Compliant"

---

## Task 2: Network Firewall Setup

### Step 1: Create Private Subnet
1. **Navigate** to VPC service
2. **Click** "Subnets" → "Create subnet"
3. **VPC**: Select default VPC
4. **Subnet settings**:
   - **Name**: `Private-Subnet`
   - **Availability Zone**: us-west-2a
   - **IPv4 CIDR block**: `172.31.64.0/20`
5. **Click "Create subnet"**

### Step 2: Create Private Route Table
1. **Click** "Route tables" → "Create route table"
2. **Name**: `Private-Route-Table`
3. **VPC**: Select default VPC
4. **Click "Create route table"**
5. **Select** the new route table
6. **Click** "Subnet associations" tab → "Edit subnet associations"
7. **Select** `Private-Subnet`
8. **Click "Save associations"**

### Step 3: Create NAT Gateway
1. **Click** "NAT gateways" → "Create NAT gateway"
2. **Name**: `Lab-NAT-Gateway`
3. **Subnet**: Select public subnet in us-west-2a
4. **Connectivity type**: Public
5. **Click** "Allocate Elastic IP"
6. **Click "Create NAT gateway"**
7. **Wait** for NAT gateway to become "Available"

### Step 4: Update Private Route Table
1. **Navigate** to Route tables
2. **Select** `Private-Route-Table`
3. **Click** "Routes" tab → "Edit routes"
4. **Click "Add route"**:
   - **Destination**: `0.0.0.0/0`
   - **Target**: NAT Gateway → Select your NAT gateway
5. **Click "Save changes"**

### Step 5: Create IAM Role for EC2
1. **Navigate** to IAM service
2. **Click** "Roles" → "Create role"
3. **Select** "AWS service" → "EC2"
4. **Click "Next"** → **Attach policies**:
   - Search and select `AmazonSSMManagedInstanceCore`
5. **Role name**: `EC2-SSM-Role`
6. **Click "Create role"**

### Step 6: Launch EC2 in Private Subnet
1. **Navigate** to EC2 service → **Click "Launch Instance"**
2. **Configuration**:
   - **Name**: `Private-Test-Instance`
   - **AMI**: Amazon Linux 2023 AMI
   - **Instance type**: t3.micro
   - **Key pair**: Proceed without a key pair (not needed for SSM)
   - **Network settings**: Edit
     - **VPC**: Default VPC
     - **Subnet**: `Private-Subnet`
     - **Auto-assign public IP**: Disable
   - **Security group**: Create new with default settings
   - **IAM instance profile**: Select `EC2-SSM-Role`
3. **Click "Launch instance"**

### Step 7: Test Internet Connectivity
1. **Navigate** to Systems Manager service
2. **Click** "Session Manager" in left panel
3. **Click "Start session"**
4. **Select** your `Private-Test-Instance`
5. **Click "Start session"**
6. **Test** connectivity:
```bash
ping -c 4 google.com
ping -c 4 8.8.8.8
dig @8.8.8.8 tiktok.com
```
7. **Verify** all commands work successfully

### Step 8: Create Firewall Subnet
1. **Navigate** to VPC → Subnets
2. **Click "Create subnet"**
3. **Subnet settings**:
   - **Name**: `Firewall-Subnet`
   - **Availability Zone**: us-west-2a
   - **IPv4 CIDR block**: `172.31.80.0/28`
4. **Click "Create subnet"**

### Step 9: Create Firewall Route Table
1. **Click** "Route tables" → "Create route table"
2. **Name**: `Firewall-Subnet-Route-Table`
3. **VPC**: Select default VPC
4. **Click "Create route table"**
5. **Associate** with `Firewall-Subnet`
6. **Add route**:
   - **Destination**: `0.0.0.0/0`
   - **Target**: NAT Gateway → Select your NAT gateway

### Step 10: Create Network Firewall
1. **Navigate** to VPC → Network Firewall
2. **Click "Create firewall"**
3. **Firewall details**:
   - **Name**: `DNS-Blocking-Firewall`
   - **VPC**: Default VPC
4. **Subnet mappings**:
   - **Availability Zone**: us-west-2a
   - **Subnet**: `Firewall-Subnet`
5. **Firewall policy**: Create and associate an empty firewall policy
6. **Policy settings**:
   - **Name**: `DNS-Block-Policy`
   - **Default actions**: Drop action to "None"
7. **Advanced settings**:
   - **Delete protection**: Disabled
   - **Subnet change protection**: Disabled
8. **Click "Create firewall"**
9. **Wait** for firewall to become "Ready"

### Step 11: Create Stateless Rule Group
1. **Navigate** to VPC → Network Firewall → Rule groups
2. **Click "Create rule group"**
3. **Rule group details**:
   - **Name**: `Block-Google-DNS`
   - **Type**: Stateless
   - **Capacity**: 3
4. **Rules**:
   - **Priority**: 1
   - **Source**: All IPv4 addresses (0.0.0.0/0)
   - **Destination**: Custom → `8.8.8.8/32`
   - **Protocol**: Any
   - **Action**: Drop
5. **Click "Add rule"** → **Next**
6. **Accept** other defaults
7. **Click "Create rule group"**

### Step 12: Add Rule Group to Firewall Policy
1. **Navigate** to Network Firewall → Firewall policies
2. **Click** on `DNS-Block-Policy`
3. **Click** "Stateless rule groups" tab
4. **Click "Add rule groups"**
5. **Select** `Block-Google-DNS`
6. **Priority**: 1
7. **Click "Add rule groups"**

### Step 13: Update Private Subnet Routing
1. **Navigate** to VPC → Route tables
2. **Select** `Private-Route-Table`
3. **Click** "Routes" tab → "Edit routes"
4. **Modify** the 0.0.0.0/0 route:
   - **Target**: Gateway Load Balancer Endpoint → Select firewall endpoint
5. **Click "Save changes"**

### Step 14: Test Firewall Blocking
1. **Navigate** to Systems Manager → Session Manager
2. **Connect** to `Private-Test-Instance`
3. **Test** blocked traffic:
```bash
ping -c 4 8.8.8.8
dig @8.8.8.8 tiktok.com
```
4. **Verify** both commands fail/timeout
5. **Test** allowed traffic:
```bash
ping -c 4 google.com
```
6. **Verify** this still works (uses different DNS)

---

## Verification Steps

### Task 1 Verification
- ✅ AWS Config enabled and monitoring S3 buckets
- ✅ S3 bucket initially non-compliant for versioning
- ✅ Automatic remediation enabled versioning
- ✅ Bucket status changed to compliant

### Task 2 Verification  
- ✅ Private subnet with NAT gateway connectivity
- ✅ EC2 instance can reach internet initially
- ✅ Network Firewall blocks 8.8.8.8 DNS queries
- ✅ General internet access still works

---

## Cleanup

### Step 1: Delete Network Firewall
1. **Navigate** to VPC → Network Firewall
2. **Delete** firewall and associated policy
3. **Delete** rule group

### Step 2: Delete VPC Resources
1. **Terminate** EC2 instance
2. **Delete** NAT gateway
3. **Release** Elastic IP
4. **Delete** custom subnets and route tables

### Step 3: Delete Config Resources
1. **Navigate** to AWS Config
2. **Delete** configuration recorder
3. **Delete** S3 bucket
4. **Delete** IAM role

---

## Key Takeaways

### AWS Config Benefits
- **Continuous compliance monitoring** of AWS resources
- **Automated remediation** reduces manual intervention
- **Historical configuration tracking** for audit purposes

### Network Firewall Benefits
- **Granular traffic control** at the network level
- **Stateful and stateless filtering** capabilities
- **Integration with VPC routing** for transparent operation

### Best Practices Demonstrated
- ✅ **Automated compliance** with Config rules and remediation
- ✅ **Defense in depth** with network-level security controls
- ✅ **Least privilege** IAM roles for automation
- ✅ **Network segmentation** with private subnets and controlled routing

---

**🎯 Learning Objectives Achieved:**
- ✅ Configure AWS Config for compliance monitoring
- ✅ Implement automatic remediation workflows
- ✅ Deploy Network Firewall for traffic filtering
- ✅ Create secure network architectures with private subnets
- ✅ Block specific network traffic while maintaining connectivity
