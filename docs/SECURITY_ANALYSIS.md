# Security and Stability Analysis Report

## Executive Summary
This report identifies **critical vulnerabilities**, **memory leaks**, and **crash scenarios** in the Srujan codebase. Issues range from **HIGH** to **LOW** severity.

---

## 🔴 CRITICAL VULNERABILITIES

### 1. **Command Injection via `os.system()`**
**Severity:** HIGH  
**Files:** `src/lib/utils.py` (lines 183, 191), `src/sfw_dhcp.py` (lines 73, 78)

**Issue:**
```python
os.system("service dnsmasq stop")
os.system("service dnsmasq restart")
```

**Risk:** If an attacker can control environment variables or the PATH, they could execute arbitrary commands.

**Recommendation:**
```python
import subprocess
subprocess.run(["systemctl", "stop", "dnsmasq"], check=True)
subprocess.run(["systemctl", "restart", "dnsmasq"], check=True)
```

---

### 2. **Path Traversal in `write_config()`**
**Severity:** HIGH  
**File:** `src/lib/utils.py` (line 74)

**Issue:**
```python
os.rename(config_file,"/tmp/" + file.stem)
```

**Risk:** If `config_file` contains path traversal characters (`../`), files could be moved to unintended locations.

**Recommendation:**
```python
import os
safe_stem = os.path.basename(file.stem)
os.rename(config_file, os.path.join("/tmp", safe_stem))
```

---

### 3. **Unvalidated Input in Regex Matching**
**Severity:** MEDIUM  
**File:** `src/sfw.py` (lines 61, 117-150)

**Issue:**
```python
ip_class = ipaddress.IPv4Address(ip)  # Can raise ValueError
```

**Risk:** Malformed log entries can crash the main loop.

**Recommendation:**
```python
try:
    ip_class = ipaddress.IPv4Address(ip)
except ValueError:
    print(f"Invalid IP address: {ip}")
    return
```

---

### 4. **Unclosed File Handle**
**Severity:** MEDIUM (Memory Leak)  
**File:** `src/sfw.py` (line 115)

**Issue:**
```python
for logline in tailer.follow(open(DNSMASQ_LOG_FILE)):
```

**Risk:** File handle is never closed, leading to resource exhaustion over time.

**Recommendation:**
```python
with open(DNSMASQ_LOG_FILE) as log_file:
    for logline in tailer.follow(log_file):
        # ... process
```

---

### 5. **Bare `except` Clauses**
**Severity:** MEDIUM  
**Files:** `src/sfw_dhcp.py` (line 76), `src/sfw_nmap_scan.py` (line 159)

**Issue:**
```python
except:
    pass
```

**Risk:** Silently swallows all exceptions, including `KeyboardInterrupt` and `SystemExit`, making debugging impossible.

**Recommendation:**
```python
except Exception as e:
    print(f"Error: {e}")
```

---

## 🟡 MODERATE ISSUES

### 6. **Race Condition in `write_config()`**
**Severity:** MEDIUM  
**File:** `src/lib/utils.py` (lines 72-74)

**Issue:**
```python
if file.exists():
    os.rename(config_file,"/tmp/" + file.stem)
```

**Risk:** Between `exists()` check and `rename()`, another process could delete the file, causing a crash.

**Recommendation:**
```python
try:
    os.rename(config_file, os.path.join("/tmp", safe_stem))
except FileNotFoundError:
    pass  # File was already deleted
```

---

### 7. **Unhandled JSON Parsing Errors**
**Severity:** MEDIUM  
**Files:** `src/sfw_dhcp.py` (line 158), `src/sfw_dns.py` (line 24), `src/sfw_setup.py` (line 107)

**Issue:**
```python
vendor_category_mapping = json.loads(read_config(MANUFACTURER_CATEGORY_MAPPING))
```

**Risk:** If `read_config()` returns `None` or malformed JSON, `json.loads()` will crash.

**Recommendation:**
```python
config_content = read_config(MANUFACTURER_CATEGORY_MAPPING)
if config_content is None:
    return DEFAULT_DEVICE_CATEGORY
try:
    vendor_category_mapping = json.loads(config_content)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    return DEFAULT_DEVICE_CATEGORY
```

---

### 8. **Potential Index Out of Bounds**
**Severity:** MEDIUM  
**Files:** `src/sfw_nmap_scan.py` (lines 52, 85, 88)

**Issue:**
```python
tmp_host = host.hostnames.pop()  # Crashes if list is empty after check
mcpe = cpelist.pop()
jdata['os_name'] = host.os.osmatches[0].name  # IndexError if empty
```

**Risk:** If lists are empty, `pop()` or `[0]` will raise `IndexError`.

**Recommendation:**
```python
tmp_host = host.hostnames[0] if host.hostnames else host.address
if cpelist:
    mcpe = cpelist[0]
    jdata['vendor'] = mcpe.get_vendor()
if host.os.osmatches:
    jdata['os_name'] = host.os.osmatches[0].name
```

---

### 9. **Global Mutable State**
**Severity:** MEDIUM (Memory Leak)  
**File:** `src/sfw.py` (lines 44-45, 47-51)

**Issue:**
```python
sbl = None
ti_tag = []
redis_conn = Redis()
new_device_queue = Queue('dhcp', connection=redis_conn)
```

**Risk:** 
- `ti_tag` list is never used but persists in memory
- Redis connections are created at module import, not closed on exit

**Recommendation:**
```python
# Remove unused ti_tag
# Implement connection cleanup
def cleanup():
    redis_conn.close()

import atexit
atexit.register(cleanup)
```

---

### 10. **Missing Input Validation in `mac_to_oui()`**
**Severity:** MEDIUM  
**File:** `src/sfw_dhcp.py` (lines 53-54)

**Issue:**
```python
mac_tmp = mac.split(":")
mac_oui = mac_tmp[0] + ":" + mac_tmp[1] + ":" + mac_tmp[2] + ":*:*:*"
```

**Risk:** If MAC address format is invalid (not enough colons), `IndexError` will crash the worker.

**Recommendation:**
```python
def mac_to_oui(mac):
    mac_tmp = mac.split(":")
    if len(mac_tmp) < 3:
        raise ValueError(f"Invalid MAC address format: {mac}")
    return ":".join(mac_tmp[:3]) + ":*:*:*"
```

---

## 🟢 LOW SEVERITY ISSUES

### 11. **Inefficient String Concatenation**
**Severity:** LOW (Performance)  
**Files:** Multiple

**Issue:**
```python
tag_data = "dhcp-mac=set:" + tag.strip() + "," + mac_oui + "\n"
```

**Recommendation:**
```python
tag_data = f"dhcp-mac=set:{tag.strip()},{mac_oui}\n"
```

---

### 12. **Hardcoded Sleep Values**
**Severity:** LOW  
**Files:** `src/sfw.py` (lines 133, 144), `src/sfw_nmap_scan.py` (lines 96, 153)

**Issue:**
```python
time.sleep(1)
time.sleep(20)
```

**Risk:** Arbitrary delays can slow down processing unnecessarily.

**Recommendation:** Make sleep durations configurable via `config.py`.

---

### 13. **Missing Null Checks**
**Severity:** LOW  
**File:** `src/sfw_dhcp.py` (line 145)

**Issue:**
```python
vendor = mac_to_vendor(mac)
return vendor_to_category(vendor)  # vendor could be None
```

**Recommendation:**
```python
vendor = mac_to_vendor(mac)
if vendor is None:
    return DEFAULT_DEVICE_CATEGORY
return vendor_to_category(vendor)
```

---

### 14. **Logic Error in `seed_dhcp__tags()`**
**Severity:** LOW (Bug)  
**File:** `src/sfw_dhcp.py` (line 35)

**Issue:**
```python
for non_iot_mac in mac_tags["non_iot"]:
    add_mac_tag("iot", non_iot_mac)  # Should be "non_iot", not "iot"
```

**Recommendation:**
```python
add_mac_tag("non_iot", non_iot_mac)
```

---

## 📊 MEMORY LEAK ANALYSIS

### Confirmed Leaks:
1. **Unclosed file handle** in `sfw.py:115` (main loop)
2. **Redis connections** never closed
3. **Elasticsearch connections** created per call in `send2es()` without connection pooling
4. **Unused global variable** `ti_tag` persists forever

### Potential Leaks:
1. **Regex compilation** inside `run_sfw()` - should be module-level constants
2. **ManufParser** instantiated on every `mac_to_vendor()` call (line 203)

---

## 🚨 CRASH SCENARIOS

### Guaranteed Crashes:
1. **Invalid IP in log** → `ValueError` in `add_dns_query_q()`
2. **Malformed MAC** → `IndexError` in `mac_to_oui()`
3. **Empty nmap results** → `IndexError` in `process_report()`
4. **Missing JSON files** → `FileNotFoundError` in `seed_dhcp__tags()`
5. **Invalid JSON** → `JSONDecodeError` in `vendor_to_category()`

### Likely Crashes:
1. **Redis connection failure** → Unhandled exception on queue operations
2. **Elasticsearch down** → Partial failure (caught, but logs errors)
3. **dnsmasq log rotation** → `tailer.follow()` continues reading old file

---

## 🛠️ RECOMMENDED FIXES (Priority Order)

### Immediate (Critical):
1. Replace `os.system()` with `subprocess.run()`
2. Add try-except around `ipaddress.IPv4Address()`
3. Fix unclosed file handle in `sfw.py`
4. Replace bare `except:` with `except Exception:`

### Short-term (High):
5. Add input validation to `mac_to_oui()`
6. Add null checks for `mac_to_vendor()` return value
7. Fix path traversal in `write_config()`
8. Add JSON parsing error handling

### Medium-term (Moderate):
9. Implement connection pooling for Elasticsearch
10. Add Redis connection cleanup
11. Move regex compilation to module level
12. Fix logic bug in `seed_dhcp__tags()`

### Long-term (Low):
13. Refactor string concatenation to f-strings
14. Make sleep durations configurable
15. Add comprehensive logging framework
16. Implement graceful shutdown handlers

---

## 📝 NOTES

- **No SQL injection risks** (no SQL database used)
- **No XSS risks** (no web interface in this codebase)
- **Authentication**: Hardcoded API keys should be moved to environment variables
- **Logging**: Currently uses `print()` - should use proper logging module

---

**Generated:** 2025-11-28  
**Analyzer:** Antigravity Security Analysis
