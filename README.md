# 🛍️ Electronics Product Review Assistant

An AI-powered product research assistant that helps you find the perfect electronics by searching the web, analyzing products, and generating comprehensive comparison reports.

## Features

- **Smart Requirements Collection**: Conversational interface that asks the right questions
- **Web Research**: Automatically searches for products across the internet
- **Intelligent Analysis**: Analyzes products and generates detailed comparison reports
- **Unknown Unknowns**: Identifies important factors you might not have considered
- **Top 5 Recommendations**: Provides ranked recommendations with ratings and reasoning

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up API Keys

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
ANTHROPIC_API_KEY=your-actual-api-key-here
PARALLEL_API_KEY=your-parallel-api-key-here
```

Get your API keys from:
- Anthropic: https://console.anthropic.com/
- Parallel AI: https://parallel.ai

### 3. Build the Application

```bash
npm run build
```

### 4. Run the Application

```bash
npm start
```

Or for development with auto-reload:

```bash
npm run dev
```

## Usage

1. **Start the application** - Run `npm start`
2. **Describe what you're looking for** - Example: "I need a gaming laptop under $1500"
3. **Answer follow-up questions** - The assistant will ask 3-4 focused questions
4. **Wait for research** - The assistant searches the web for products
5. **Review your report** - Get a detailed comparison report with ratings and recommendations

### Example Session

```
🛍️  ELECTRONICS PRODUCT REVIEW ASSISTANT  🛍️

Tell me what electronics product you're looking for:
You: I need a laptop for video editing

🎯 Phase 1: Understanding Your Needs

Got it! What's your budget?
You: around $2000

Cool. What specs are most important to you?
You: Good CPU, lots of RAM, and a nice display

✅ Requirements collected successfully!

🔍 Phase 2: Researching Products
   [Searching the web...]

✅ Found 8 products to analyze!

📊 Phase 3: Analyzing Products & Generating Report

✅ Analysis complete!

[Full detailed report with ratings and recommendations...]
```

## Project Structure

```
product_review/
├── src/
│   ├── agents/           # AI agents
│   │   ├── PlannerAgent.ts      # Collects requirements
│   │   ├── ResearchAgent.ts     # Web research
│   │   └── AnalyzerAgent.ts     # Analysis & reporting
│   ├── orchestrator/     # Workflow coordination
│   │   └── WorkflowOrchestrator.ts
│   ├── types/            # TypeScript type definitions
│   │   └── index.ts
│   └── main.ts           # CLI entry point
├── dist/                 # Compiled JavaScript (generated)
├── .env                  # Environment variables (create this)
├── .env.example          # Example environment file
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
└── README.md            # This file
```

## How It Works

The application uses a 3-agent workflow:

1. **Planner Agent**
   - Conversationally collects user requirements
   - Asks focused follow-up questions (max 3-4)
   - Validates completeness before proceeding

2. **Research Agent**
   - Generates optimized search queries
   - Uses Claude's web search tool to find products
   - Extracts product information
   - Identifies "unknown unknowns"

3. **Analyzer Agent**
   - Ranks products against user requirements
   - Generates ratings (0-10 scale)
   - Calculates match scores (0-100%)
   - Creates detailed comparison report
   - Provides final recommendation

## Configuration

The application requires two API keys:

- `ANTHROPIC_API_KEY` - Your Anthropic API key (required) - For AI agents
- `PARALLEL_API_KEY` - Your Parallel AI API key (required) - For web search

Optional:
- `DEBUG=true` - Enable debug logging

## Requirements

- Node.js 18+
- npm or yarn
- Anthropic API key (for Claude AI)
- Parallel AI API key (for web search)

## Development

```bash
# Install dependencies
npm install

# Run in development mode (with auto-reload)
npm run dev

# Build for production
npm run build

# Run built version
npm start

# Clean build artifacts
npm run clean
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found" or "PARALLEL_API_KEY not found"
- Make sure you've created a `.env` file
- Check that both API keys are correctly set
- Verify the `.env` file is in the root directory
- Get Anthropic key from: https://console.anthropic.com/
- Get Parallel AI key from: https://parallel.ai

### Build Errors
```bash
# Clean and rebuild
npm run clean
npm run build
```

### TypeScript Errors
- Make sure all dependencies are installed: `npm install`
- Check Node.js version: `node --version` (should be 18+)

## Future Enhancements

- [ ] Web UI (React/Next.js frontend)
- [ ] Save/load previous searches
- [ ] Price tracking and alerts
- [ ] Multi-category support
- [ ] Export reports to PDF
- [ ] Comparison mode (compare specific products)

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
