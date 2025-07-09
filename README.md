# FalkorDB Async Vectorizer

Async background job for automatic vector embedding generation and ingestion into FalkorDB graphs.

## Overview

This project provides a standalone solution for adding vector embedding capabilities to FalkorDB graphs. While FalkorDB 4.0+ has full native vector support for querying and indexing, this async job handles the missing piece: automatic embedding generation and ingestion.

## Problem Statement

The upstream [FalkorDB MCPServer v1.1.0](https://github.com/FalkorDB/FalkorDB-MCPServer) provides excellent graph querying capabilities but lacks vector embedding generation tools. This creates a gap for users who want to:

- Automatically generate embeddings for text content
- Perform semantic search on graph data
- Add vector capabilities to existing graphs without architectural changes

## Solution Approach

**Simple Async Job Pattern**: A lightweight Python background service that:

1. **Monitors** FalkorDB graphs for new content
2. **Generates** embeddings using OpenAI/local models
3. **Updates** nodes with vector data
4. **Maintains** vector indices automatically

## Key Benefits

- ✅ **Zero architectural changes** - works with existing FalkorDB setups
- ✅ **KISS principle** - single Python file, minimal complexity
- ✅ **Immediate value** - can be deployed in 15 minutes
- ✅ **Retroactive vectors** - adds embeddings to existing data
- ✅ **Production ready** - Docker deployment with monitoring

## Architecture

```
FalkorDB Graph ←→ Async Vectorizer Job ←→ Embedding API (OpenAI/Local)
     (4.0+)           (Python Service)         (Text → Vectors)
```

The job runs independently and enhances your existing FalkorDB deployment without requiring changes to your current MCP server or proxy setup.

## Quick Start

### 1. Clone and Configure
```bash
git clone https://github.com/Dragonatorul/FalkorDB-Async-Vectorizer.git
cd FalkorDB-Async-Vectorizer
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### 2. Deploy
```bash
docker-compose up -d
```

### 3. Test
Add data with text properties to your FalkorDB graphs - the job will automatically generate embeddings within 5 minutes.

📖 **Complete Setup Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed step-by-step instructions.

## Related Projects

- **[FalkorDB-FastMCP-Proxy](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy)** - Remote MCP server for Claude Desktop integration
- **[FalkorDB MCPServer](https://github.com/FalkorDB/FalkorDB-MCPServer)** - Official MCP server backend
- **[Vector Analysis Documentation](https://github.com/Dragonatorul/FalkorDB-FastMCP-Proxy/tree/main/docs/exploratory-analysis)** - Comprehensive analysis of vector implementation options

## Implementation Files

- **[vector_backfill_job.py](vector_backfill_job.py)** - Complete async job implementation (~150 lines)
- **[Dockerfile](Dockerfile)** - Container configuration for deployment
- **[docker-compose.yml](docker-compose.yml)** - Standalone deployment configuration
- **[requirements.txt](requirements.txt)** - Python dependencies
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide with troubleshooting

## Status

✅ **Ready for Deployment** - Complete implementation with Docker deployment ready.

## License

MIT License - see [LICENSE](LICENSE) file for details.