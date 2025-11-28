# Srujan Policy Engine User Guide

The Advanced Policy Engine allows you to define granular network access rules based on device context, trust scores, and behavior.

## Core Concepts

### 1. Policies
A policy is a rule that defines:
- **Source**: Who is making the request (Device MAC, Category, or Zone).
- **Destination**: Where they are going (IP, CIDR, or "Any").
- **Conditions**: Additional criteria (Time, Trust Score, etc.).
- **Action**: What to do (Allow, Block, Quarantine, etc.).

### 2. Trust Scores
Every device has a dynamic trust score (0-100) based on:
- **Positive Factors**: Known device, clean history, trusted manufacturer.
- **Negative Factors**: Threats detected, anomalies, weak encryption.

Trust Levels:
- **Highly Trusted (90+)**: Full access.
- **Trusted (70-89)**: Normal access.
- **Neutral (50-69)**: Standard monitoring.
- **Low Trust (30-49)**: Restricted access.
- **Untrusted (<30)**: Quarantine recommended.

## Creating Policies

### Using the Policy Builder
1. Navigate to **Policies > Create Policy**.
2. Enter a **Name** and **Description**.
3. Select **Source** (e.g., "IoT Devices") and **Destination** (e.g., "Internet").
4. Add **Conditions**:
   - **Time Range**: e.g., "22:00 to 06:00".
   - **Trust Score**: e.g., "Less than 50".
5. Choose an **Action** (e.g., "Block").
6. Click **Create Policy**.

### Example Scenarios

#### Block IoT Devices at Night
- **Source**: Category: IoT
- **Condition**: Time Range 22:00 - 06:00
- **Action**: Block

#### Quarantine Low Trust Devices
- **Source**: Any
- **Condition**: Trust Score <= 30
- **Action**: Quarantine

## Testing Policies
Use the **Policy Tester** to simulate scenarios before applying rules.
1. Go to a policy and click **Test**.
2. Enter hypothetical context (e.g., "Time: 23:00", "Trust Score: 20").
3. Click **Run Test** to see if the policy would apply.

## Monitoring
- **Policy List**: View active policies and hit counts.
- **Trust Dashboard**: Monitor device scores and trends.
- **Logs**: View detailed execution logs for each policy.
