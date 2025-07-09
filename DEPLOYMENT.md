# Deployment Guide

## Quick Start: Add Vector Capabilities in 15 Minutes

This guide provides step-by-step instructions for adding automatic vector ingestion to your existing FalkorDB FastMCP Proxy setup.

## Prerequisites

- Existing FalkorDB FastMCP Proxy deployment
- OpenAI API key (or other embedding service)
- Docker and docker-compose

## Step 1: Clone and Setup

```bash
git clone https://github.com/Dragonatorul/FalkorDB-Async-Vectorizer.git
cd FalkorDB-Async-Vectorizer

# Copy environment template
cp .env.example .env
```

## Step 2: Configure Environment

Edit `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional (adjust as needed)
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
EMBEDDING_MODEL=text-embedding-3-small
BATCH_SIZE=50
SLEEP_INTERVAL=300
```

## Step 3: Deploy

### Option A: Standalone Deployment

```bash
# Build and start the vector job
docker-compose up -d

# Check logs
docker-compose logs -f vector-job
```

### Option B: Integration with Existing Stack

Add to your existing `docker-compose.yml`:

```yaml
services:
  # ... your existing services ...
  
  vector-job:
    build: ./FalkorDB-Async-Vectorizer
    environment:
      - FALKORDB_HOST=falkordb
      - FALKORDB_PORT=6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - EMBEDDING_MODEL=text-embedding-3-small
      - BATCH_SIZE=50
      - SLEEP_INTERVAL=300
    depends_on:
      - falkordb
    restart: unless-stopped
```

## Step 4: Test the System

### Add Test Data
Use your existing `falkordb_query` tool:

```cypher
CREATE (d:Document {
  id: 1,
  text: "FalkorDB is a graph database with vector search capabilities",
  created_at: datetime()
})
```

### Create Vector Index
```cypher
CREATE VECTOR INDEX FOR (d:Document) ON (d.embedding) 
OPTIONS {dimension:1536, similarityFunction:'cosine'}
```

### Wait and Check
After 5 minutes, check if the vector was added:

```cypher
MATCH (d:Document {id: 1}) 
RETURN d.text, d.embedding IS NOT NULL as has_embedding
```

### Test Vector Search
```cypher
CALL db.idx.vector.queryNodes(
  'Document', 'embedding', 5, 
  vecf32([0.1, 0.2, 0.3])  -- dummy query vector
) YIELD node, score
RETURN node.text, score
```

## Monitoring and Troubleshooting

### Check Job Status
```bash
# View recent logs
docker-compose logs --tail=50 vector-job

# Check if container is running
docker-compose ps vector-job

# Run job manually once
docker-compose exec vector-job python vector_backfill_job.py --once
```

### Common Issues

**Issue: "OPENAI_API_KEY environment variable required"**
```bash
# Solution: Set the API key
echo "OPENAI_API_KEY=sk-your-key" >> .env
docker-compose up -d vector-job
```

**Issue: "Failed to connect to FalkorDB"**
```bash
# Solution: Check FalkorDB is running and accessible
docker-compose ps
# Verify FALKORDB_HOST and FALKORDB_PORT in .env
```

**Issue: "No nodes need vectors"**
```bash
# Solution: Add test data with text property
# Use falkordb_query tool to create nodes with 'text' property
```

**Issue: Rate limiting from OpenAI**
```bash
# Solution: Reduce batch size and increase interval
# Edit .env:
# BATCH_SIZE=25
# SLEEP_INTERVAL=600
docker-compose up -d vector-job
```

## Configuration Options

### Embedding Models

```bash
# Fast and cost-effective
EMBEDDING_MODEL=text-embedding-3-small

# Higher quality, more expensive  
EMBEDDING_MODEL=text-embedding-3-large
```

### Performance Tuning

```bash
# For high-volume processing
BATCH_SIZE=100
SLEEP_INTERVAL=60

# For rate-limited APIs
BATCH_SIZE=25
SLEEP_INTERVAL=600

# For development/testing
BATCH_SIZE=10
SLEEP_INTERVAL=30
```

## Production Considerations

### Security
- Use Docker secrets for API keys
- Implement proper network isolation
- Regular security updates

### Monitoring
- Add health checks
- Implement structured logging
- Set up alerting for failures

### Resource Management
- Set appropriate CPU/memory limits
- Monitor API usage and costs
- Implement retry logic for failures

## Integration with Existing Workflows

### Manual Triggering
```bash
# Trigger immediate processing
docker-compose exec vector-job python vector_backfill_job.py --once
```

### Scheduled Processing
```bash
# Add to crontab for additional control
0 */6 * * * docker-compose -f /path/to/docker-compose.yml exec vector-job python vector_backfill_job.py --once
```

## Summary

You now have a fully functional automatic vector ingestion system that:

✅ **Works with existing setup** - No changes to current services  
✅ **Processes automatically** - Nodes get vectors within 5 minutes  
✅ **Easy to deploy** - Single Docker container  
✅ **Easy to monitor** - Standard Docker logging  
✅ **Cost effective** - Only runs when needed  
✅ **Configurable** - Environment variables for all settings  

The system transforms your existing vector-capable FalkorDB setup into a fully autonomous vector search platform while maintaining simplicity and reliability.