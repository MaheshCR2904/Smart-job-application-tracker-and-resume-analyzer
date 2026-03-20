"""
Platform Fix for WMI Timeout Issue
This file must be imported BEFORE any other modules that might import pymongo.
Place this at the very top of run.py, before any other imports.

Usage: Add this as the FIRST import in run.py:
    import platform_fix
"""
import sys

if sys.platform == 'win32':
    import platform
    
    # Store original functions
    _original_system = platform.system
    _original_release = platform.release
    _original_version = platform.version
    _original_win32_ver = platform.win32_ver
    _original_uname = platform.uname
    
    # Cache for platform info
    _cached_info = {}
    
    def _get_cached_info(key, func, *args, **kwargs):
        """Get cached platform info or compute and cache it"""
        if key not in _cached_info:
            try:
                _cached_info[key] = func(*args, **kwargs)
            except Exception:
                # Return safe defaults on error
                if key == 'system':
                    _cached_info[key] = 'Windows'
                elif key == 'release':
                    _cached_info[key] = '10'
                elif key == 'version':
                    _cached_info[key] = '10.0.0'
                elif key == 'win32_ver':
                    _cached_info[key] = ('10', '', '', 'Professional')
                elif key == 'uname':
                    _cached_info[key] = platform.uname_result(
                        system='Windows',
                        node='localhost',
                        release='10',
                        version='10.0.0',
                        machine='AMD64',
                        processor='AMD64'
                    )
        return _cached_info[key]
    
    # Patch platform functions with caching
    def patched_system():
        return _get_cached_info('system', _original_system)
    
    def patched_release():
        return _get_cached_info('release', _original_release)
    
    def patched_version():
        return _get_cached_info('version', _original_version)
    
    def patched_win32_ver():
        return _get_cached_info('win32_ver', _original_win32_ver)
    
    def patched_uname():
        return _get_cached_info('uname', _original_uname)
    
    # Apply patches
    platform.system = patched_system
    platform.release = patched_release
    platform.version = patched_version
    platform.win32_ver = patched_win32_ver
    platform.uname = patched_uname
    
    # Also patch the module-level functions
    sys.modules['platform'].system = patched_system
    sys.modules['platform'].release = patched_release
    sys.modules['platform'].version = patched_version
    sys.modules['platform'].win32_ver = patched_win32_ver
    sys.modules['platform'].uname = patched_uname

print("Platform fix applied for Windows WMI timeout issue")
