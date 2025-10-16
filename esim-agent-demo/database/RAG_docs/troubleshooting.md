# eSIM Troubleshooting Guide

## Common Issues and Solutions

### Activation Issues

#### Problem: QR Code Won't Scan

**Possible Causes:**
- Poor lighting conditions
- Damaged or blurry QR code
- Camera focus issues
- QR code too small/large on screen

**Solutions:**
1. **Adjust Display Brightness**
   - Increase screen brightness to 100%
   - Reduce glare and reflections
   
2. **Adjust Distance**
   - Move device closer or further from QR code
   - Try 6-12 inches distance
   
3. **Use Different Display**
   - Display QR code on laptop/tablet instead of phone
   - Print QR code on paper
   
4. **Clean Camera Lens**
   - Wipe camera lens with soft cloth
   - Remove any protective film
   
5. **Manual Activation**
   - Use SM-DP+ address and activation code instead
   - Enter details manually in settings

#### Problem: "Unable to Complete Cellular Plan Change"

**Possible Causes:**
- Poor internet connection
- Carrier server issues
- Invalid activation code
- eSIM already activated on another device

**Solutions:**
1. **Check Internet Connection**
   - Connect to stable Wi-Fi
   - Ensure strong signal
   - Try different Wi-Fi network
   
2. **Wait and Retry**
   - Wait 10-30 minutes
   - Server might be temporarily unavailable
   
3. **Restart Device**
   - Power off completely
   - Wait 30 seconds
   - Power on and try again
   
4. **Request New QR Code**
   - Contact eSIM provider
   - Code may have been used or expired
   
5. **Check Device Lock Status**
   - Ensure device is unlocked (not carrier-locked)
   - Contact carrier to unlock if needed

#### Problem: "Cellular Plan Cannot Be Added"

**Possible Causes:**
- eSIM storage full
- Software version outdated
- Carrier restrictions
- Device incompatibility

**Solutions:**
1. **Remove Old eSIM Profiles**
   - Delete unused eSIM profiles
   - Free up eSIM storage slots
   
2. **Update Software**
   - iPhone: Settings > General > Software Update
   - Android: Settings > System > System update
   
3. **Check Compatibility**
   - Verify device supports eSIM
   - Check regional restrictions
   - Confirm carrier supports eSIM
   
4. **Factory Reset (Last Resort)**
   - ⚠️ Backup data first
   - Settings > General > Reset
   - Restore from backup after reset

### Connection Issues

#### Problem: No Service / No Signal

**Possible Causes:**
- eSIM not properly activated
- Network coverage issues
- Airplane mode enabled
- Incorrect network selection

**Solutions:**
1. **Toggle Airplane Mode**
   - Turn Airplane Mode ON
   - Wait 10 seconds
   - Turn Airplane Mode OFF
   
2. **Restart Device**
   - Simple restart often fixes connection issues
   
3. **Check eSIM Status**
   - Settings > Cellular/Mobile Network
   - Ensure eSIM is turned ON
   - Verify eSIM is selected for data
   
4. **Verify Coverage Area**
   - Check provider's coverage map
   - Move to different location if in poor coverage area
   
5. **Manual Network Selection**
   - Turn off automatic network selection
   - Manually select available network
   - Try different network operators if available
   
6. **Wait for Activation**
   - Some eSIMs take up to 24 hours to activate
   - Check with provider for activation status

#### Problem: Data Not Working

**Possible Causes:**
- Data roaming disabled
- Incorrect APN settings
- Data plan exhausted
- Cellular data disabled

**Solutions:**
1. **Enable Data Roaming**
   - **iPhone**: Settings > Cellular > [eSIM] > Data Roaming > ON
   - **Android**: Settings > Network > SIMs > [eSIM] > Roaming > ON
   - ⚠️ Travel eSIMs require data roaming enabled
   
2. **Check Cellular Data Settings**
   - **iPhone**: Settings > Cellular > Cellular Data
   - Ensure correct eSIM is selected for data
   - **Android**: Settings > Network & Internet > Mobile network
   
3. **Verify Data Balance**
   - Check if data allowance is depleted
   - Use provider's app or website
   - Top up if necessary
   
4. **Check APN Settings**
   - Usually configured automatically
   - Contact provider for correct APN settings if needed
   - **iPhone**: Settings > Cellular > Cellular Data Network
   - **Android**: Settings > Network > Access Point Names
   
5. **Reset Network Settings**
   - ⚠️ This will delete Wi-Fi passwords
   - **iPhone**: Settings > General > Reset > Reset Network Settings
   - **Android**: Settings > System > Reset > Reset Wi-Fi, mobile & Bluetooth

#### Problem: Slow Data Speeds

**Possible Causes:**
- Network congestion
- Weak signal strength
- Wrong network band
- Data throttling
- Device limitations

**Solutions:**
1. **Check Signal Strength**
   - Move to area with better coverage
   - Go outdoors if inside building
   
2. **Test at Different Time**
   - Network may be congested during peak hours
   - Try early morning or late night
   
3. **Check Network Type**
   - Ensure connected to 4G/LTE or 5G
   - Not 3G or slower
   
4. **Switch Network Operator**
   - Try different partner network
   - Manually select alternative operator
   
5. **Restart Device**
   - Clear network cache
   - Re-establish connection
   
6. **Check Data Balance**
   - Some plans throttle after reaching limit
   - Verify remaining high-speed data

### Calling Issues

#### Problem: Cannot Make or Receive Calls

**Possible Causes:**
- eSIM for data only (no voice)
- Wrong default voice line
- Network registration issue
- VoLTE not supported

**Solutions:**
1. **Verify Plan Type**
   - Check if your eSIM includes voice calls
   - Many travel eSIMs are data-only
   - Use WhatsApp/FaceTime for calls if data-only
   
2. **Check Default Voice Line**
   - **iPhone**: Settings > Cellular > Default Voice Line
   - Ensure correct eSIM is selected
   
3. **VoLTE Settings**
   - **iPhone**: Settings > Cellular > [eSIM] > Voice & Data > LTE
   - Enable VoLTE if available
   
4. **Wi-Fi Calling**
   - Enable as backup: Settings > Cellular > Wi-Fi Calling
   - May not work with all eSIM providers

#### Problem: Poor Call Quality

**Solutions:**
1. Check signal strength (need at least 2-3 bars)
2. Disable VoLTE and use regular voice network
3. Move to area with better coverage
4. Use Wi-Fi calling if available
5. Contact provider if issue persists

### SMS/Text Message Issues

#### Problem: Cannot Send/Receive SMS

**Possible Causes:**
- Data-only eSIM plan
- Wrong default SMS line
- SMS center number incorrect

**Solutions:**
1. **Verify Plan Includes SMS**
   - Many travel eSIMs don't include SMS
   - Use iMessage/WhatsApp instead
   
2. **Check Default SMS Line**
   - **iPhone**: Messages app uses iMessage automatically when possible
   - For SMS, check Settings > Messages > Send & Receive
   - **Android**: Settings > Network > SIMs > SMS
   
3. **Use Alternative Messaging**
   - iMessage (iPhone to iPhone)
   - WhatsApp, Signal, Telegram
   - These use data, not SMS

### Device-Specific Issues

#### iPhone-Specific Issues

**Problem: eSIM Disappeared After iOS Update**

**Solutions:**
1. Go to Settings > Cellular
2. Check if eSIM is just disabled (toggle back on)
3. If completely gone, check Settings > General > About for EID
4. Contact carrier to get new QR code
5. Reinstall eSIM profile

**Problem: "SIM Not Supported" Error**

**Solutions:**
1. Verify iPhone is unlocked
2. Update to latest iOS version
3. Remove and reinsert physical SIM (if using dual SIM)
4. Contact carrier for unlock status
5. Restore iPhone from backup

#### Android-Specific Issues

**Problem: eSIM Option Missing**

**Solutions:**
1. Update to Android 9 or later
2. Check if device model supports eSIM
3. Verify not carrier-locked
4. Contact manufacturer for support

**Problem: eSIM Won't Stay Active**

**Solutions:**
1. Disable battery optimization for carrier services
2. Settings > Apps > Show system apps > Carrier Services
3. Turn off battery optimization
4. Restart device

### Billing and Account Issues

#### Problem: Charged But eSIM Not Working

**Solutions:**
1. Check spam folder for activation email
2. Verify order status on provider's website
3. Allow up to 24 hours for processing
4. Contact provider's customer support with order number
5. Check if QR code was sent to correct email

#### Problem: Data Depleted Too Quickly

**Solutions:**
1. **Check Data Usage**
   - Identify apps consuming most data
   - Settings > Cellular/Mobile Data
   
2. **Restrict Background Data**
   - **iPhone**: Settings > General > Background App Refresh > OFF
   - **Android**: Settings > Network > Data Saver > ON
   
3. **Disable Auto-Updates**
   - Turn off automatic app updates over cellular
   - Download updates on Wi-Fi only
   
4. **Disable Video Autoplay**
   - Social media apps
   - Video streaming settings
   
5. **Monitor Streaming Quality**
   - Lower video quality settings
   - Use Wi-Fi for high-quality streaming

### Transfer and Compatibility Issues

#### Problem: Cannot Transfer eSIM to New Device

**Solutions:**
1. **Verify Transfer Compatibility**
   - Both devices must support eSIM transfer
   - Requires iOS 16+ for iPhone
   - Most Android devices don't support transfer
   
2. **Contact Provider**
   - Request new QR code for new device
   - Some carriers allow remote provisioning
   
3. **Remove from Old Device First**
   - Delete eSIM from old device
   - Then activate on new device

#### Problem: eSIM Not Working After Device Switch

**Solutions:**
1. Wait 24 hours for activation
2. Check if old device still has eSIM active (remove it)
3. Contact provider to reset activation
4. Request new QR code
5. Verify new device is unlocked

### Error Messages

#### "This Code Is No Longer Valid"

**Causes & Solutions:**
- QR code already used → Request new code
- QR code expired → Request new code
- Wrong code format → Verify you have correct code

#### "Unable to Activate Cellular Plan"

**Causes & Solutions:**
- Server issue → Wait and retry
- Invalid credentials → Verify SM-DP+ address
- Network problem → Check internet connection

#### "Cellular Plan Error"

**Causes & Solutions:**
- Corrupted profile → Remove and reinstall
- Software bug → Update device
- Carrier issue → Contact provider

#### "Carrier Settings Update Failed"

**Causes & Solutions:**
- Poor connection → Connect to Wi-Fi
- Retry update: Settings > General > About
- Restart device and try again

## Advanced Troubleshooting

### Network Diagnostics

#### iPhone Field Test Mode
1. Dial `*3001#12345#*`
2. View detailed network information
3. Check signal strength (RSRP values)
4. Note cell tower information

#### Android Network Info
1. Dial `*#*#4636#*#*`
2. Select Phone Information
3. View network type and signal
4. Run Ping test

### Logging for Support

If contacting support, prepare this information:
- Device model and OS version
- EID number
- ICCID number
- Error messages (screenshots)
- Network operator name
- Location/country
- Steps that triggered the issue
- Time issue started

## When to Contact Support

Contact eSIM provider support if:
- ✅ Issue persists after all troubleshooting steps
- ✅ Error messages appear repeatedly
- ✅ QR code doesn't work after multiple attempts
- ✅ Data depleting faster than expected
- ✅ Activation takes longer than 24 hours
- ✅ Cannot remove stuck eSIM profile
- ✅ Charged but no service received

## Preventive Measures

### Before Installing eSIM
- ✅ Update device to latest OS
- ✅ Check device is unlocked
- ✅ Verify eSIM compatibility
- ✅ Connect to stable Wi-Fi
- ✅ Save QR code and activation details

### Regular Maintenance
- ✅ Remove expired eSIM profiles
- ✅ Monitor data usage
- ✅ Keep software updated
- ✅ Restart device periodically
- ✅ Clear cache if device slows down

### For Travelers
- ✅ Activate eSIM before departure (if possible)
- ✅ Test eSIM while still in home country
- ✅ Save provider's contact information
- ✅ Download offline maps
- ✅ Keep backup: physical SIM or second eSIM

