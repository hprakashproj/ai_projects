# PDF Parser Utility

## Project Overview
The PDF Parser Utility is a powerful tool designed to simplify the process of extracting and manipulating data from PDF files. It allows developers to efficiently read and parse PDFs, making it ideal for applications that require interaction with document content.

## Features
- **Extract Text and Images**: Easily retrieve text and images from PDF documents.
- **Search Functionality**: Search for specific text within a PDF and retrieve contextual information.
- **Data Manipulation**: Modify, annotate, and save changes to existing PDF files.
- **Support for Various PDF Formats**: Works with standard PDF files and encrypted documents.

## Installation Instructions
To install the PDF Parser Utility, follow the steps below:
1. Ensure you have [Node.js](https://nodejs.org/) installed on your machine.
2. Clone the repository:
   ```bash
   git clone https://github.com/hprakashproj/ai_projects.git
   cd ai_projects/pdfParserUtil
   ```
3. Install the required dependencies:
   ```bash
   npm install
   ```

## Usage Examples
Here are some examples of how to use the PDF Parser Utility:

### Extracting Text from a PDF
```javascript
const PDFParser = require('pdfParserUtil');

const pdfParser = new PDFParser();

pdfParser.parse('path_to_pdf_file.pdf', function(err, data) {
    if (err) {
        console.error('Error parsing PDF:', err);
    } else {
        console.log('Parsed PDF data:', data);
    }
});
```

### Searching for Text
```javascript
const pdfParser = new PDFParser();

pdfParser.search('keyword_to_search', function(err, results) {
    if (err) {
        console.error('Error searching PDF:', err);
    } else {
        console.log('Search results:', results);
    }
});
```

## API Reference
### PDFParser
#### `new PDFParser()`
Creates a new instance of the PDFParser.

#### `pdfParser.parse(filePath, callback)`
Parses the PDF located at `filePath`; calls `callback` with either an error or the parsed data.

#### `pdfParser.search(keyword, callback)`
Searches the PDF for `keyword`; calls `callback` with either an error or the search results.

---
For more information and additional examples, please refer to the official documentation and source code.
