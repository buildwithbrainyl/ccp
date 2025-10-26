# Amazon Lex Builder's Day - Mentorship Booking Chatbot Lab
**AWS Certified Cloud Practitioner**  
*Hands-on lab with Amazon Lex V2, Lambda integration, and conversational AI*

---

## Prerequisites
- AWS Account with admin access
- All resources will be created in **us-west-2**
- Basic understanding of conversational interfaces

## Lab Overview
You'll build a conversational AI chatbot that helps users book AWS mentorship sessions. The bot validates user inputs (program type and commitment duration) and provides a complete booking flow with confirmation.

**Important:** In Amazon Lex V2, slot types are scoped to individual bots, so you must create the bot first before creating custom slot types.

---

## Task 1: Create Lex Bot

### 1.1 Navigate to Amazon Lex
1. **Sign in to AWS Console**
2. **Search for "Lex" in the search bar** and select **Amazon Lex**
3. **Ensure you're in us-west-2 region** (check top-right corner)

### 1.2 Create Bot
1. **In left menu: Bots**
2. **Click "Create bot"**

**Creation method:**
3. **Select "Traditional"** (default)
4. **Select "Create a blank bot"**

**Bot configuration:**
5. **Bot name:** `MentorshipBot`
6. **Description (optional):** `AWS mentorship booking assistant`

**IAM permissions:**
7. **Runtime role:** Select **"Create a role with basic Amazon Lex permissions"** (default)

8. **Click "Next"** (to go to page 2)

**Page 2 - Children's Online Privacy Protection Act (COPPA):**
9. **Select "No"**

**Idle session timeout:**
10. **Leave as default:** `5` `minute(s)`

**Add language to bot:**
11. **Select language:** **English (US)** (default)
12. **Description:** Leave blank (optional)
13. **Voice interaction:** Leave as **Danielle** (default)
14. **Intent classification confidence score threshold:** Leave as **0.40** (default)

15. **Click "Done"**
16. **You'll be automatically taken to the intent builder for a default "NewIntent"**

---

## Task 2: Rename Default Intent

### 2.1 Rename NewIntent to BookAWSMentorship
1. **You'll see "Intent: NewIntent" at the top of the page**
2. **Scroll down to "Intent details" section**
3. **In "Intent name" field, change `NewIntent` to `BookAWSMentorship`**
4. **Scroll to the bottom and click "Save intent"**

---

## Task 3: Create Custom Slot Type

### 3.1 Create Custom Slot Type for Program Types
1. **In left menu: Slot types**
2. **Click "Add slot type" → "Add blank slot type"**
3. **Slot type configuration:**
   - Slot type name: `ProgramType`
   - Description: `AWS mentorship program types`
   - Slot value resolution: **Restrict to slot values**
4. **Add slot type values:**
   - Click "Add slot value"
   - Value: `CCP` (press Enter)
   - Value: `SA` (press Enter)
   - Value: `GenAI` (press Enter)
5. **Click "Save slot type"**

---

## Task 4: Configure Intent with Slots and Utterances

### 4.1 Return to BookAWSMentorship Intent
1. **In left menu: Intents**
2. **Click on "BookAWSMentorship"**

### 4.2 Add Sample Utterances
1. **In "Sample utterances" section, click "Add utterance"**
2. **Add the following utterance:**
   - `Book AWS mentorship`

3. **Press Enter to add**

### 4.3 Add Slots
1. **Scroll down to "Slots" section**
2. **Click "Add slot"**

**First Slot - ProgramType:**
- Name: `ProgramType`
- Slot type: Select **`ProgramType`** (the custom type you created)
- Prompts: `Which program are you interested in? CCP, SA, or GenAI?`
- Click "Add"

3. **Click "Add slot" again**

**Second Slot - StartDate:**
- Name: `StartDate`
- Slot type: Search and select **`AMAZON.Date`**
- Prompts: `When do you want to start?`
- Click "Add"

4. **Click "Add slot" again**

**Third Slot - Months:**
- Name: `Months`
- Slot type: Search and select **`AMAZON.Number`**
- Prompts: `How many months do you want to commit to? (3-6 months)`
- Click "Add"

### 4.4 Configure All Slots as Required
1. **In the Slots section, check the "Required" checkbox for all three slots:**
   - ✅ ProgramType
   - ✅ StartDate
   - ✅ Months

### 4.5 Configure Confirmation
1. **Scroll down to "Confirmation" section**
2. **Toggle "Confirmation" to ON**
3. **Confirmation prompt:** 
   - Click "Add message"
   - Message: `Great! Just to confirm - you want to book {ProgramType} mentorship starting {StartDate} for {Months} months. Is that correct?`
4. **Decline response:**
   - Click "Add message" under "Decline responses"
   - Message: `No problem. Let's start over. What can I help you with?`

### 4.6 Save Intent
1. **Click "Save intent" button** (bottom of page)

### 4.7 Build Bot (Initial Version)
1. **Click "Build" button** (top-right)
2. **Wait for build to complete** (takes 30-60 seconds)

### 4.8 Test Bot (Without Lambda)
1. **Click "Test" button** (top-right) to open test window
2. **In the chat window, type:** `Book AWS mentorship`
3. **Follow the prompts:**
   - Program: `CCP`
   - Start date: `tomorrow`
   - Months: `5`
   - Confirmation: `yes`
4. **Expected Result:** Bot collects all slots and confirms (no validation yet - any month value will be accepted)

---

## Task 5: Create Lambda Function for Validation

### 5.1 Create Lambda Function
1. **Open new tab and navigate to Lambda service**
2. **Click "Create function"**
3. **Function configuration:**
   - Select **"Author from scratch"**
   - Function name: `LexMentorshipValidator`
   - Runtime: **Python 3.12**
   - Architecture: **x86_64**
4. **Expand "Change default execution role":**
   - Select **"Create a new role with basic Lambda permissions"**
5. **Click "Create function"**

### 5.2 Add Lambda Code
1. **In the "Code" tab, scroll to "Code source" section**
2. **Delete existing code in `lambda_function.py`**
3. **Open the Lambda code in a new tab:**
   - URL: https://github.com/buildwithbrainyl/ccp/blob/main/builders-day/lex/mentorship_lambda.py
   - Copy the entire code
4. **Paste the code into the Lambda editor**
5. **Click "Deploy"** (above the code editor)
6. **Wait for "Successfully deployed" message**

---

## Task 6: Integrate Lambda with Lex

### 6.1 Enable Lambda Code Hooks in Intent
1. **Go back to Amazon Lex tab**
2. **In left menu: Intents → BookAWSMentorship**
3. **Scroll to "Code hooks - optional" section**
4. **Check "Use a Lambda function for initialization and validation"**
5. **Scroll to "Fulfillment" section**
6. **Expand "Advanced options"**
7. **Check "Use a Lambda function for fulfillment"**
8. **Click "Save intent"**

### 6.2 Set Lambda Function at Alias Level
1. **In left menu: Deployment → Aliases**
2. **Click on the first alias** (TestBotAlias)
3. **Click "English (US)"**
4. **Under "Lambda function - optional":**
   - Select `LexMentorshipValidator` from dropdown
5. **Click "Save"**

### 6.3 Build Bot
1. **Click "Build"** (top-right)
2. **Wait for build to complete** (30-60 seconds)

---

## Task 7: Test Complete Conversational Flow

### 7.1 Test Valid Scenario
1. **Click "Test"** (top-right)
2. **Type:** `Book AWS mentorship`
3. **Test conversation:**
   - Program: `SA`
   - Start date: `next Monday`
   - Months: `4`
   - Confirmation: `yes`
4. **Expected Result:** 
   - All validations pass
   - Final message: "Thanks! I have booked your AWS mentorship session. You'll receive a confirmation email shortly."

### 7.2 Test Invalid Month Range
1. **In test window, click "Clear chat"**
2. **Type:** `I want mentorship`
3. **Test conversation:**
   - Program: `GenAI`
   - Start date: `tomorrow`
   - Months: `2` (invalid - less than 3)
4. **Expected Result:**
   - Bot should reject and display: "Commitment must be between 3 and 6 months. Please choose a valid duration."
   - Bot re-prompts for Months
5. **Type:** `5`
6. **Confirmation:** `yes`
7. **Expected Result:** Booking should complete successfully

### 7.3 Test Invalid Month Range (Upper Bound)
1. **In test window, click "Clear chat"**
2. **Type:** `Book a mentorship session`
3. **Test conversation:**
   - Program: `CCP`
   - Start date: `2025-02-01`
   - Months: `12` (invalid - more than 6)
4. **Expected Result:**
   - Bot should reject with validation message
   - Bot re-prompts for Months
5. **Type:** `6`
6. **Confirmation:** `yes`
7. **Expected Result:** Booking should complete successfully

### 7.4 Test Decline Confirmation
1. **In test window, click "Clear chat"**
2. **Type:** `Schedule mentorship`
3. **Provide valid inputs:**
   - Program: `SA`
   - Start date: `next week`
   - Months: `3`
   - Confirmation: `no`
4. **Expected Result:**
   - Bot should show decline message
   - Conversation should restart

---

## Testing Summary
✅ **Task 1:** Bot `MentorshipBot` created successfully  
✅ **Task 2:** Default intent renamed to `BookAWSMentorship`  
✅ **Task 3:** Custom slot type `ProgramType` created with CCP, SA, GenAI values  
✅ **Task 4:** Intent configured with slots, utterances, and confirmation  
✅ **Task 5:** Lambda function validates month range (3-6) and program types  
✅ **Task 6:** Lambda integrated with Lex for validation and fulfillment  
✅ **Task 7:** Complete conversation flow with validation working  

---

## Clean Up (Optional)

### Delete in Order:
1. **Amazon Lex:**
   - Navigate to Bots
   - Select `MentorshipBot` → Actions → Delete
   - Type bot name to confirm deletion
   - Navigate to Slot types
   - Select `ProgramType` → Delete

2. **Lambda:**
   - Navigate to Lambda service
   - Select `LexMentorshipValidator`
   - Actions → Delete
   - Confirm deletion

3. **IAM Roles (Auto-created):**
   - Navigate to IAM → Roles
   - Search for roles containing "MentorshipBot" or "LexMentorshipValidator"
   - Delete the auto-created roles

---

## Troubleshooting

### Bot Not Validating Inputs
- Verify Lambda is deployed after pasting code
- Check "Advanced options" is enabled for validation
- Rebuild bot after making Lambda configuration changes
- Check Lambda CloudWatch logs for errors

### Lambda Permission Errors
- Ensure resource-based policy is added to Lambda
- Principal must be `lexv2.amazonaws.com` (not lex.amazonaws.com)
- Rebuild bot to automatically grant permissions

### Slot Values Not Being Captured
- Ensure all three slots are marked as "Required"
- Check slot names match exactly: `ProgramType`, `StartDate`, `Months`
- Verify slot types are correct (custom type for ProgramType, AMAZON.Date, AMAZON.Number)

### Validation Logic Not Triggering
- Check Lambda CloudWatch logs (Monitor tab → View logs in CloudWatch)
- Verify Lambda code is deployed successfully
- Ensure months value is outside 3-6 range to test validation
- Rebuild bot after Lambda integration changes

### Bot Doesn't Show Fulfillment Message
- Verify fulfillment Lambda code hook is enabled
- Check FulfillmentCodeHook section in Lambda code
- Ensure bot is rebuilt after configuration changes

---

## What You've Learned
- Created custom slot types for controlled user inputs
- Built a multi-turn conversational bot with Amazon Lex V2
- Implemented business logic validation with Lambda
- Integrated Lambda code hooks for dialog management and fulfillment
- Tested conversational AI flows with various scenarios

---

**Lab Complete! You've successfully built an AWS Mentorship booking chatbot with intelligent validation!**

