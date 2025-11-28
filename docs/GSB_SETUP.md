# Google Safe Browsing Setup

## Overview
Srujan now uses the `pysafebrowsing` library to integrate with Google Safe Browsing API v4. This provides real-time threat detection for DNS queries.

## Getting an API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Safe Browsing API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Safe Browsing API"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key

## Configuration

1. Open `src/lib/config.py`
2. Replace `YOUR_GSB_API_KEY` with your actual API key:
   ```python
   GSB_API_KEY = 'your-actual-api-key-here'
   ```
3. Ensure `GSB_ENABLE` is set to `True`:
   ```python
   GSB_ENABLE = True
   ```

## Important Notes

- **Non-Commercial Use Only**: The Safe Browsing API is intended for non-commercial use. For commercial applications, use the [Web Risk API](https://cloud.google.com/web-risk) instead.
- **Privacy**: The `pysafebrowsing` library uses the Lookup API, which sends URLs directly to Google's servers (not hashed). This is a privacy trade-off for simplicity and lower resource usage.
- **Rate Limits**: Be aware of Google's API rate limits. For high-volume applications, consider implementing caching or using the Update API (requires `afilipovich/gglsbl` library).

## Testing

To test the GSB integration:

```python
from lib.utils import gsb_init, gsb_lookup

# Initialize client
sbl = gsb_init()

# Test with a known malicious URL
result = gsb_lookup('http://malware.testing.google.test/testing/malware/')
print(result)  # Should return threat information
```
