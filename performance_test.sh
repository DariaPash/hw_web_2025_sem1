#!/bin/bash
# Performance testing script using Apache Benchmark (ab) or wrk
# Make sure nginx and gunicorn are running before executing tests

echo "=========================================="
echo "Performance Testing Script"
echo "=========================================="
echo ""

# Check if ab is available
if command -v ab &> /dev/null; then
    BENCHMARK_TOOL="ab"
    BENCHMARK_ARGS="-n 1000 -c 10"
elif command -v wrk &> /dev/null; then
    BENCHMARK_TOOL="wrk"
    BENCHMARK_ARGS="-t 4 -c 10 -d 10s"
else
    echo "Error: Neither 'ab' nor 'wrk' is installed."
    echo "Install ab: sudo apt-get install apache2-utils (Ubuntu) or brew install httpd (macOS)"
    echo "Install wrk: brew install wrk (macOS) or sudo apt-get install wrk (Ubuntu)"
    exit 1
fi

echo "Using benchmark tool: $BENCHMARK_TOOL"
echo ""

# Test 1: Static document directly through nginx
echo "=========================================="
echo "Test 1: Static document directly through nginx"
echo "=========================================="
if [ "$BENCHMARK_TOOL" = "ab" ]; then
    ab -n 1000 -c 10 http://localhost/sample.html
else
    wrk -t 4 -c 10 -d 10s http://localhost/sample.html
fi
echo ""

# Test 2: Static document directly through gunicorn
echo "=========================================="
echo "Test 2: Static document directly through gunicorn"
echo "=========================================="
echo "Note: Start gunicorn with: gunicorn -c gunicorn_static_config.py test_static:application"
echo "Then run this test manually:"
if [ "$BENCHMARK_TOOL" = "ab" ]; then
    echo "ab -n 1000 -c 10 http://localhost:8001/sample.html"
else
    echo "wrk -t 4 -c 10 -d 10s http://localhost:8001/sample.html"
fi
echo ""

# Test 3: Dynamic document directly through gunicorn
echo "=========================================="
echo "Test 3: Dynamic document directly through gunicorn"
echo "=========================================="
echo "Note: Start gunicorn with: gunicorn -c gunicorn_dynamic_config.py test_dynamic:application"
if [ "$BENCHMARK_TOOL" = "ab" ]; then
    ab -n 1000 -c 10 http://localhost:8000/
else
    wrk -t 4 -c 10 -d 10s http://localhost:8000/
fi
echo ""

# Test 4: Dynamic document through nginx proxy (without cache)
echo "=========================================="
echo "Test 4: Dynamic document through nginx proxy (without cache)"
echo "=========================================="
echo "Note: Clear nginx cache first: rm -rf /tmp/nginx_cache/*"
echo "Then run:"
if [ "$BENCHMARK_TOOL" = "ab" ]; then
    ab -n 1000 -c 10 http://localhost/
else
    wrk -t 4 -c 10 -d 10s http://localhost/
fi
echo ""

# Test 5: Dynamic document through nginx proxy (with cache)
echo "=========================================="
echo "Test 5: Dynamic document through nginx proxy (with cache)"
echo "=========================================="
echo "Note: Run after Test 4 to warm up cache, then:"
if [ "$BENCHMARK_TOOL" = "ab" ]; then
    ab -n 1000 -c 10 http://localhost/
else
    wrk -t 4 -c 10 -d 10s http://localhost/
fi
echo ""

echo "=========================================="
echo "Testing completed!"
echo "=========================================="
