#!/usr/bin/env python3
import httpx

def test_frontend():
    try:
        response = httpx.get('http://localhost:3002', timeout=10.0)
        content = response.text

        print('Status:', response.status_code)
        print('Content-Type:', response.headers.get('content-type', 'unknown'))
        print('Has React root div:', 'id="root"' in content)
        print('Has main.tsx script:', 'main.tsx' in content)
        print('Has Vite client:', '@vite/client' in content)

        # Check for common error patterns
        error_indicators = [
            'error',
            'Error',
            'failed',
            'Failed',
            'cannot resolve',
            'Cannot resolve'
        ]

        found_errors = []
        for error in error_indicators:
            if error in content.lower():
                # Get context around error
                start = max(0, content.lower().find(error) - 100)
                end = min(len(content), content.lower().find(error) + 200)
                found_errors.append(content[start:end])

        if found_errors:
            print('Potential errors found:')
            for error in found_errors[:3]:  # Show first 3 errors
                print('  ', error.replace('\n', ' ')[:200] + '...')
        else:
            print('No obvious errors detected in HTML')

    except Exception as e:
        print(f'Error testing frontend: {e}')

if __name__ == "__main__":
    test_frontend()