# GitHub Pages Setup Guide

## Domain Name Suggestions

For hosting this restricted accounts search page, here are suitable domain name suggestions:

### Recommended Options:
1. **restricted-accounts.co.il** - Israeli domain, professional
2. **restricted-accounts-search.co.il** - More descriptive
3. **bank-restrictions.co.il** - Clear purpose
4. **accounts-search.co.il** - Simple and clear

### International Options:
1. **restricted-accounts.israel** - New TLD, modern
2. **bank-restrictions.info** - Informational site
3. **restricted-accounts.online** - Generic but available

### GitHub Pages Default URL:
- **https://amirlabai.github.io/Corporate-Restricted-Accounts-File/**

## Setup Instructions

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings**
3. Scroll down to **Pages** section
4. Under **Source**, select:
   - **Branch**: `main` (or `master`)
   - **Folder**: `/ (root)`
5. Click **Save**

### 2. File Structure

Ensure your repository has this structure:
```
Corporate-Restricted-Accounts-File/
├── index.html          (main search page)
├── output/
│   └── appended/
│       └── חשבונות_מוגבלים_YYYY_MM_DD.csv
└── README.md
```

### 3. Update index.html

The `index.html` file is already configured to:
- Load CSV files from `output/appended/` directory
- Use GitHub API as fallback to find latest CSV file
- Work with GitHub Pages static hosting

### 4. Custom Domain Setup (Optional)

If you purchase a custom domain:

1. **Add CNAME file**:
   Create a file named `CNAME` in the root directory with your domain:
   ```
   restricted-accounts.co.il
   ```

2. **Configure DNS**:
   Add these DNS records to your domain provider:
   - **Type**: CNAME
   - **Name**: @ (or www)
   - **Value**: amirlabai.github.io

3. **Enable HTTPS**:
   GitHub Pages automatically enables HTTPS for custom domains

### 5. Update CSV File Path

The HTML file automatically tries to:
1. Load from `output/appended/` directory
2. Use GitHub API to find the latest CSV file
3. Fall back to hardcoded file names

To ensure it always finds the latest file, you can:
- Update the `findLatestCSV()` function with actual file names
- Or rely on GitHub API (already implemented)

### 6. Testing

1. Push `index.html` to your repository
2. Wait a few minutes for GitHub Pages to build
3. Visit: `https://amirlabai.github.io/Corporate-Restricted-Accounts-File/`
4. Test the search functionality

## Features

The search page includes:
- ✅ Search by account number (digits only)
- ✅ Search by date (greater than or equal)
- ✅ Combined search (both criteria)
- ✅ Results table with all columns
- ✅ Download results as CSV
- ✅ RTL (Hebrew) support
- ✅ Responsive design
- ✅ Auto-advance date inputs
- ✅ Input validation

## Maintenance

### Updating the CSV File

When a new CSV file is added to `output/appended/`:
1. The page will automatically find it via GitHub API
2. Or update the `possibleFiles` array in `findLatestCSV()` function
3. The latest file (by name) will be used automatically

### Performance Considerations

- Large CSV files (>10MB) may load slowly
- Consider converting to JSON for better performance
- Or implement server-side search (requires backend)

## Security Notes

- The page is client-side only (no backend)
- All data is public (GitHub repository)
- CSV files are served as static files
- No authentication required (by design)

## Troubleshooting

### CSV Not Loading
- Check file path in browser console
- Verify file exists in `output/appended/`
- Check GitHub API rate limits

### Search Not Working
- Open browser console (F12) for errors
- Verify CSV format matches expected columns
- Check that data loaded successfully

### Custom Domain Not Working
- Verify CNAME file is in root directory
- Check DNS propagation (can take 24-48 hours)
- Ensure DNS points to `amirlabai.github.io`

