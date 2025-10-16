# eSIM Security and Privacy Guide

## eSIM Security Overview

### How Secure Are eSIMs?

eSIMs use the same security standards as physical SIM cards:
- ✅ **Encryption**: 128-256 bit encryption
- ✅ **Authentication**: Secure carrier authentication
- ✅ **Tamper-Resistant**: Cannot be physically removed or cloned
- ✅ **Remote Management**: Secure over-the-air provisioning
- ✅ **Industry Standard**: GSMA certified technology

### eSIM vs Physical SIM Security

| Security Aspect | eSIM | Physical SIM |
|----------------|------|--------------|
| Physical Theft | Cannot be removed ✅ | Can be removed ❌ |
| SIM Swapping | More difficult ✅ | Easier to perform ❌ |
| Cloning | Not possible ✅ | Rare but possible ❌ |
| Lost Device | Remotely disable ✅ | Requires carrier call ⚠️ |
| Encryption | Same standard | Same standard |
| OTA Updates | Secure provisioning ✅ | Not applicable |

**Verdict**: eSIMs are generally **more secure** than physical SIMs

## Security Best Practices

### Device Security

#### Lock Your Device

**Set Strong Passcode/Password:**
- ✅ Minimum 6 digits (numeric)
- ✅ Better: 8+ character alphanumeric
- ✅ Best: Biometric (Face ID, Touch ID, Fingerprint) + passcode
- ❌ Avoid: Simple patterns, birthdates, 1234

**Enable Find My Device:**
- **iPhone**: Settings > [Your Name] > Find My > Find My iPhone > ON
- **Android**: Settings > Security > Find My Device > ON

**Benefits:**
- Locate lost device
- Remotely lock device
- Remotely erase device
- Prevent unauthorized eSIM changes

#### Automatic Lock

**Configure Auto-Lock:**
- **iPhone**: Settings > Display & Brightness > Auto-Lock > 30 seconds - 1 minute
- **Android**: Settings > Display > Screen timeout > 30 seconds - 1 minute

**Why**: Prevents unauthorized access if you leave device unattended

#### Two-Factor Authentication (2FA)

**Enable 2FA for:**
- Apple ID / Google Account
- Email accounts
- Banking apps
- Social media
- Any account with sensitive data

**Why**: Protects accounts even if someone accesses your device

### eSIM-Specific Security

#### Protect Your QR Code

**QR Code Security:**
- 🔒 **Treat like a password**: Anyone with QR code can install eSIM
- 🔒 **Store securely**: Password-protected files or secure note app
- 🔒 **Don't share publicly**: Never post QR code online or social media
- 🔒 **Secure email**: QR codes sent via email should be in secure account
- 🔒 **Delete after use**: Remove QR code from email after installation (optional)

**What Can Someone Do With Your QR Code?**
- Install eSIM on their device (if unused)
- Access your data plan
- Use your data allowance
- Potentially access accounts tied to phone number (if voice-enabled)

#### Secure eSIM Management

**Prevent Unauthorized Changes:**

**iPhone:**
- Settings > Screen Time > Use Screen Time Passcode
- Settings > Screen Time > Content & Privacy Restrictions
- Enable restrictions for "Cellular Data Changes"
- Requires passcode to add/remove eSIMs

**Android:**
- Settings > Security > SIM card lock
- Set PIN for SIM changes
- Varies by device manufacturer

**Carrier PIN/PUK:**
- Some carriers require PIN to manage eSIM
- Keep PUK code in secure location
- Never share with anyone

#### Verify eSIM Source

**Only Buy eSIMs From:**
- ✅ Reputable, established providers
- ✅ Official carrier websites
- ✅ Verified app stores (Apple App Store, Google Play)
- ✅ Well-reviewed companies

**Avoid:**
- ❌ Unverified third-party resellers
- ❌ Social media marketplace sellers
- ❌ Too-good-to-be-true prices
- ❌ Websites without HTTPS/SSL

**Red Flags:**
- Extremely low prices (50%+ below market)
- No company information or contact details
- Poor website security (no HTTPS)
- Requests for excessive personal information
- Payment only via non-reversible methods (crypto, gift cards)

### Network Security

#### Public Wi-Fi Risks

**Common Threats:**
- Man-in-the-middle attacks
- Fake Wi-Fi hotspots
- Unencrypted networks
- Data interception

**Safe Wi-Fi Practices:**

✅ **Verify Network Name**
- Ask staff for official network name
- Beware of similar names ("Airport_WiFi" vs "Airport-WiFi")

✅ **Use HTTPS Websites Only**
- Look for padlock icon in browser
- Avoid sites without encryption

✅ **Disable Auto-Connect**
- iPhone: Settings > Wi-Fi > Auto-Join Hotspot > Never
- Android: Settings > Network & Internet > Wi-Fi > Wi-Fi preferences > Turn on Wi-Fi automatically > OFF

✅ **Use VPN (Recommended)**
- Encrypts all traffic
- Protects on any network
- See VPN section below

❌ **Never on Public Wi-Fi:**
- Banking transactions
- Password entry for important accounts
- Shopping without VPN
- Accessing sensitive work documents

#### Use a VPN (Virtual Private Network)

**What VPN Does:**
- Encrypts all internet traffic
- Hides your IP address and location
- Protects data from interception
- Bypasses geographic restrictions
- Secures connection on any network

**When to Use VPN:**
- ✅ Always on public Wi-Fi
- ✅ When accessing sensitive information
- ✅ In countries with restricted internet
- ✅ For privacy-conscious browsing
- ✅ When using untrusted networks

**Recommended VPN Providers:**
- NordVPN
- ExpressVPN
- ProtonVPN
- Surfshark
- Mullvad

**Cost**: $3-12/month typically

**Free VPNs**: Use with caution
- Often sell user data
- Slower speeds
- Limited data
- Some are legitimate (ProtonVPN free tier)

**Setup:**
1. Subscribe to VPN service
2. Download VPN app
3. Install on device
4. Connect before browsing

### Privacy Protection

#### Data Collection

**What eSIM Providers May Collect:**
- Email address
- Phone number (sometimes)
- Device information (EID, ICCID)
- Usage data (data consumed, connection logs)
- Payment information

**What They Should NOT Collect:**
- Browsing history in detail
- App usage
- Message contents
- Call contents

**Check Privacy Policy:**
- What data is collected
- How data is used
- If data is shared/sold
- Data retention period
- Your rights (access, deletion)

#### Minimize Data Sharing

**Purchase Practices:**
- ✅ Use email alias for eSIM purchases
- ✅ Pay with privacy-focused methods (virtual cards, privacy.com)
- ✅ Provide only required information
- ❌ Avoid linking unnecessary accounts

**App Permissions:**
- Review app permissions for provider's app
- Deny unnecessary permissions (camera, microphone, contacts)
- iOS: Settings > Privacy > [Permission Type]
- Android: Settings > Apps > [App] > Permissions

#### Browser Privacy

**Privacy-Focused Browsing:**
- Use Private/Incognito mode
- Clear cookies and cache regularly
- Use privacy-focused browsers (Brave, Firefox Focus)
- Install tracking blockers
- Disable location services when not needed

**Search Engines:**
- DuckDuckGo (doesn't track)
- StartPage
- Brave Search

### Account Security

#### Protect Accounts Tied to Phone Number

**Accounts Using SMS 2FA:**
- Banking apps
- Email accounts
- Social media
- Cryptocurrency exchanges

**Security Measures:**

✅ **Use Authenticator Apps** (more secure than SMS)
- Google Authenticator
- Microsoft Authenticator
- Authy
- 1Password

✅ **Backup Codes**
- Save backup codes for all 2FA accounts
- Store in password manager or secure location

✅ **Multiple 2FA Methods**
- Authenticator app + backup codes + SMS
- Don't rely solely on phone number

⚠️ **Be Aware**: Travel eSIMs are temporary
- May not receive SMS on data-only eSIMs
- Plan for 2FA without SMS access

#### SIM Swapping Protection

**What is SIM Swapping?**
Attacker convinces carrier to transfer your number to their device, gaining access to SMS-based accounts.

**eSIM Advantage:**
- Harder to perform than physical SIM swapping
- Requires device access or QR code
- Additional authentication layers

**Additional Protection:**

✅ **Carrier PIN/Password**
- Set account PIN with carrier
- Required for any SIM/eSIM changes

✅ **Notification Alerts**
- Enable alerts for account changes
- Immediate notification of suspicious activity

✅ **Don't Use SMS for Critical 2FA**
- Use authenticator apps instead
- SMS less secure than app-based 2FA

### Travel-Specific Security

#### International Security Concerns

**Country-Specific Risks:**

**High Surveillance Countries:**
- Be aware: China, Russia, UAE, etc.
- Use VPN for privacy
- Avoid sensitive communications
- Separate device for travel (if very concerned)

**High Theft Areas:**
- Tourist hotspots
- Public transportation
- Crowded markets

**Precautions:**
- Keep device in front pocket or secure bag
- Use anti-theft backpacks
- Enable Find My Device before traveling
- Regular backups

#### Emergency Preparation

**Before You Travel:**

✅ **Backup Everything**
- iCloud/Google Photos
- Important documents
- Contact information
- Password manager sync

✅ **Note Important Numbers**
- Save in separate secure location:
  - Device EID
  - eSIM ICCID
  - Provider support number
  - Embassy contact
  - Bank phone numbers

✅ **Enable Remote Wipe**
- iOS: Find My iPhone > Erase iPhone
- Android: Find My Device > Erase Device
- Last resort if device stolen

**If Device is Lost/Stolen:**

1. **Use Find My Device**
   - Locate device
   - Mark as lost
   - Display message with contact info

2. **Secure Your Accounts**
   - Change passwords immediately
   - Log out all sessions
   - Notify bank if payment apps on device

3. **Contact eSIM Provider**
   - Report loss
   - Suspend service
   - Request replacement eSIM for new device

4. **Contact Carrier (Home Number)**
   - Suspend service
   - Prevent unauthorized use

5. **File Police Report**
   - May be required for insurance
   - Get report copy

### Scam Awareness

#### Common eSIM Scams

**1. Fake Provider Websites**
- Look-alike URLs (airalo.com vs airlao.com)
- Collect payment, never deliver eSIM
- May steal payment information

**Protection:**
- Verify URL carefully
- Look for HTTPS/SSL certificate
- Check reviews and ratings
- Use official app stores

**2. Phishing Emails**
- "Your eSIM will expire, click to renew"
- "Problem with your eSIM, verify account"
- Link to fake login page

**Protection:**
- Don't click links in unsolicited emails
- Go directly to provider's website
- Verify sender email address
- Check for spelling/grammar errors

**3. Social Engineering**
- "Customer service" calls asking for QR code
- "Verification" requests for account details
- Pressure tactics ("urgent", "immediate action")

**Protection:**
- Never share QR code with anyone
- Legitimate support won't ask for QR code
- Hang up and call official number
- Verify caller identity

**4. Too-Good-To-Be-True Offers**
- "Free eSIM, just pay shipping"
- "Lifetime unlimited data $10"
- "Beta tester unlimited access"

**Protection:**
- If it sounds too good to be true, it probably is
- Research company thoroughly
- Check independent reviews

### Data Usage Security

#### Monitoring for Suspicious Activity

**Check for:**
- Unexpected data usage spikes
- Apps using data when they shouldn't
- Data usage when device was off
- Unknown background processes

**Actions:**
- Review app-by-app data usage
- Uninstall suspicious apps
- Reset network settings if needed
- Contact provider if major discrepancies

#### Secure App Usage

**App Store Only:**
- ✅ Download apps from official stores only
- ❌ Avoid sideloaded apps (Android)
- ❌ No jailbroken devices for security

**App Permissions:**
- Review before granting
- Deny unnecessary permissions
- Regularly audit permissions

**App Updates:**
- Keep all apps updated
- Updates include security patches
- Enable automatic updates on Wi-Fi

### Regulatory Compliance

#### GDPR (Europe)

**Your Rights:**
- Right to access your data
- Right to deletion
- Right to data portability
- Right to correct inaccurate data

**How to Exercise:**
- Contact provider's privacy team
- Submit formal request
- Provider must respond within 30 days

#### Other Privacy Laws

- **CCPA** (California, USA)
- **PIPEDA** (Canada)
- **LGPD** (Brazil)
- Various country-specific laws

**Check:**
- Provider's privacy policy
- Where company is registered
- Which laws apply to you

## Security Checklist

### Before Purchasing eSIM
- [ ] Verify provider legitimacy
- [ ] Read privacy policy
- [ ] Check reviews and ratings
- [ ] Confirm secure payment (HTTPS)
- [ ] Use strong, unique password for account

### Upon Receiving eSIM
- [ ] Save QR code securely
- [ ] Store in password manager or encrypted note
- [ ] Note provider support contact
- [ ] Install eSIM on secure Wi-Fi
- [ ] Delete QR code email (optional)

### Device Security
- [ ] Strong passcode/biometric lock
- [ ] Auto-lock set to 30-60 seconds
- [ ] Find My Device enabled
- [ ] Two-factor authentication on accounts
- [ ] Screen Time restrictions (iPhone) or SIM lock (Android)
- [ ] Regular backups enabled

### While Traveling
- [ ] VPN installed and active
- [ ] Careful with public Wi-Fi
- [ ] Monitor data usage
- [ ] Disable auto-connect to Wi-Fi
- [ ] Keep device physically secure
- [ ] Regular backups

### If Something Goes Wrong
- [ ] Contact provider immediately
- [ ] Secure all accounts
- [ ] Change passwords
- [ ] Use Find My Device
- [ ] File police report if stolen
- [ ] Request replacement eSIM

## Red Flags and Warning Signs

🚩 **Immediate Red Flags:**
- Provider requests QR code back
- Unexpected charges
- Cannot contact support
- eSIM stops working suddenly
- Unusual data usage patterns
- Suspicious account activity
- Unexpected SMS messages about eSIM

**Action:** Contact provider immediately, secure your accounts, change passwords

## Frequently Asked Questions

**Q: Can someone hack my eSIM?**
A: eSIMs use strong encryption. Hacking is extremely difficult. Main risks are QR code theft or device compromise, not eSIM technology itself.

**Q: Is eSIM safer than physical SIM?**
A: Yes, generally. Cannot be physically removed, harder to swap, and includes secure remote management.

**Q: What if I lose my device with eSIM?**
A: Use Find My Device to locate/lock/erase. Contact provider to suspend service. Your eSIM data is encrypted and cannot be easily accessed.

**Q: Should I use VPN with eSIM?**
A: Yes, especially on public Wi-Fi and in countries with restricted internet. VPN adds layer of security and privacy.

**Q: Can provider see my browsing history?**
A: Provider can see data usage amounts and connection logs, but not detailed browsing history (websites, pages viewed) if using HTTPS. Use VPN for complete privacy.

**Q: Is my payment information safe?**
A: Reputable providers use secure payment processing (Stripe, PayPal). Your card details are not stored by the eSIM provider.

**Q: What happens if someone gets my QR code?**
A: They could install the eSIM on their device if not already activated. Keep QR codes private and secure.

**Q: How do I know if provider is trustworthy?**
A: Check: Years in business, reviews, company information, privacy policy, customer support responsiveness, HTTPS website, official app store presence.

