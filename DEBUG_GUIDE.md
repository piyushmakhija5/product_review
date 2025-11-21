# Debugging & Reviewing Results

## Enable Debug Mode

To see raw search results and debug information:

1. Edit your `.env` file:
```bash
DEBUG=true
```

2. Run the application:
```bash
npm start
```

3. After the research phase completes, you'll see:
```
🐛 Debug data saved to: debug-research-2025-11-21T12-30-45.json
```

## Debug File Contents

The debug file contains:

- **requirements**: What the user asked for
- **searchQueries**: The actual queries sent to Parallel AI
- **rawSearchResults**: Complete response from Parallel AI (including all e-commerce data)
- **analysis**: How Claude analyzed the search results
- **finalResults**: The structured product information extracted

## Review Search Results

```bash
# View the debug file
cat debug-research-*.json | jq .

# Check what queries were used
cat debug-research-*.json | jq .searchQueries

# See raw Parallel AI response
cat debug-research-*.json | jq .rawSearchResults

# Check extracted products
cat debug-research-*.json | jq .finalResults.products_found
```

## Common Issues

### No E-commerce Results

Check the raw search results to see if Parallel AI returned e-commerce data:
```bash
cat debug-research-*.json | jq '.rawSearchResults[].content' | grep -i "amazon\|walmart\|bestbuy"
```

### Wrong Year in Results

Check the search queries to ensure they include 2025:
```bash
cat debug-research-*.json | jq .searchQueries
```

Should see: `"best sports watch 2025 Amazon"` NOT `"best sports watch 2024"`

### JSON Parsing Errors

If you see JSON parsing errors, check the console output for the exact error message and the problematic JSON string.
