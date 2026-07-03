# D6: Agent Development Kit (ADK) Integration

## Overview

This document outlines the integration of Google's Agent Development Kit (ADK) into the Northwind Support Co-pilot system to replace the current manual LLM pipeline orchestration with a more robust, scalable agent-based architecture.

## Current Architecture

### Pipeline Flow
```
raw_ticket → Stage1 (classify) → Stage2 (extract) → Stage3 (ground) → Stage4 (critique) → final_reply
```

### Current Implementation
- **Manual orchestration**: `src/pipeline.py` chains 4 sequential LLM calls
- **Custom LLM client**: `src/llm_client.py` handles API calls with retry logic
- **Stage processing**: `src/stages.py` manages prompt loading and JSON parsing
- **Prompt templates**: `prompts/*.md` files contain stage-specific instructions
- **Token management**: Fixed `max_tokens=3000` to prevent truncation

### Performance Metrics (Current)
- Average total time: ~14.79s per ticket
- Stage breakdown: S1=2.84s, S2=2.91s, S3=3.43s, S4=5.61s
- Error rate: Occasional Stage 4 JSON parsing failures on long tickets
- Token usage: High due to full ticket context passed through all stages

## Proposed ADK Integration

### Architecture Options

#### Option A: Multi-Agent Workflow (current approach)
```
┌─────────────────────────────────────┐
│          ADK Workflow               │
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Classify    │→ │ Extract     │   │
│  │ Agent       │  │ Agent       │   │
│  └─────────────┘  └─────────────┘   │
│           │                │        │
│           ▼                ▼        │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Ground      │→ │ Critique    │   │
│  │ Agent       │  │ Agent       │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────┘
```

#### Option B: Single Agent with Tools (alternative approach)
```
┌─────────────────────────────────────┐
│        Single ADK Agent             │
│                                     │
│  Tools Available:                   │
│  • classify_tool()                  │
│  • extract_tool()                   │
│  • ground_tool()                    │
│  • critique_tool()                  │
│                                     │
│  Agent decides when/how to use tools│
└─────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Setup and Basic Integration

#### 1.1 Dependencies
- ✅ Install ADK: `pip install google-adk`
- ✅ Update requirements.txt
- Environment variables for model configuration

#### 1.2 Environment Configuration
```
# .env file additions
ADK_MODEL=gemini-2.5-flash
ADK_TEMPERATURE=0.3
ADK_MAX_TOKENS=3000
ADK_BASE_URL=https://api.gemini.com/v1
USE_ADK_PIPELINE=false          # Feature flag for gradual rollout
```

#### 1.3 Directory Structure
```
src/
├── agents/                    # New ADK agents
│   ├── __init__.py
│   ├── classify_agent.py
│   ├── extract_agent.py
│   ├── ground_agent.py
│   ├── critique_agent.py
│   └── workflow.py
├── tools/                     # New ADK tools (Option B)
│   ├── __init__.py
│   ├── classify_tool.py
│   ├── extract_tool.py
│   ├── ground_tool.py
│   └── critique_tool.py
├── adk_agent.py              # Single agent (Option B)
├── pipeline.py               # Keep existing - add ADK integration
├── stages.py                 # Keep existing - may be used by tools
└── llm_client.py             # Keep existing - fallback option
```

### Phase 2: Agent Development

#### 2.1 Multi-Agent Approach (Option A - current approach)

**Agent Specifications:**
- **Classify Agent**: Uses Stage 1 prompt, configured with environment variables for model/temperature
- **Extract Agent**: Uses Stage 2 prompt, inherits configuration from .env
- **Ground Agent**: Uses Stage 3 prompt, includes policy lookup capabilities
- **Critique Agent**: Uses Stage 4 prompt, validates and corrects responses

**Workflow Configuration:**
- Sequential execution: Classify → Extract → Ground → Critique
- Data passing between agents through ADK workflow state
- Error handling and retry logic built into ADK framework

#### 2.2 Single Agent + Tools Approach (Option B - alternative approach)

**Tool Implementation:**
- **classify_tool**: Wraps existing Stage 1 logic from `src/stages.py`
- **extract_tool**: Wraps existing Stage 2 logic with structured output
- **ground_tool**: Integrates policy.md lookup with Stage 3 logic
- **critique_tool**: Implements Stage 4 validation and correction

**Agent Configuration:**
- Single agent with comprehensive instructions covering all 4 stages
- Tools called sequentially based on agent's decision-making
- Model and parameters controlled via environment variables

### Phase 3: Integration

#### 3.1 Backend Integration
**Route Updates:**
- Modify `backend/routes.py` to support both legacy and ADK pipelines
- Use `USE_ADK_PIPELINE` environment variable to toggle between implementations
- Maintain existing API contract with `PipelineResponse` model
- Add result mapping function to convert ADK output to expected format

#### 3.2 Startup Configuration
**Application Initialization:**
- Update `backend/main.py` to initialize ADK agents on startup
- Load configuration from environment variables
- Initialize agents/workflow based on selected approach
- Add health check for ADK system readiness

### Phase 4: Migration Strategy

#### 4.1 Dual Mode Operation
- Keep existing pipeline as fallback
- Add feature flag to switch between ADK/legacy
- Environment variable: `USE_ADK_PIPELINE=true/false`

#### 4.2 A/B Testing
- Route percentage of requests to ADK pipeline
- Compare performance metrics
- Gradual rollout based on success rate

#### 4.3 Legacy Cleanup
- Move current files to `src/legacy/`
- Update imports and references
- Remove when ADK proven stable

## Expected Benefits

### Performance Improvements
- **Automatic retries**: No manual JSON repair logic needed
- **Better context management**: ADK optimizes token usage
- **Parallel processing**: Some stages could run concurrently
- **Reduced latency**: Optimized LLM calls

### Developer Experience  
- **Built-in tracing**: See agent interactions and timing
- **Dev UI**: `adk web` for interactive testing
- **Better error handling**: Structured exception management
- **Monitoring**: OpenTelemetry integration

### Scalability
- **Cloud deployment**: One-command deploy to Google Cloud
- **Auto-scaling**: ADK runtime handles load
- **Multi-model support**: Easy to switch LLM providers
- **Agent composition**: Reuse agents in different workflows

## Risk Mitigation

### Compatibility Risks
- **Dependency conflicts**: ADK adds many dependencies
- **API changes**: ADK is new, APIs may evolve
- **Model compatibility**: Ensure Gemini integration works

### Performance Risks
- **Latency increase**: Additional abstraction layers
- **Resource usage**: ADK overhead vs manual pipeline
- **Token consumption**: Monitor usage patterns

### Migration Risks
- **Breaking changes**: Maintain API compatibility
- **Data consistency**: Ensure output format matches
- **Testing coverage**: Comprehensive validation needed

## Testing Strategy

### Unit Tests
- Test individual agents/tools in isolation
- Mock LLM responses for deterministic testing
- Validate input/output schemas

### Integration Tests  
- End-to-end pipeline testing with real tickets
- Compare ADK vs legacy pipeline outputs
- Performance benchmarking

### Evaluation Framework
- Reuse existing `eval/` scripts
- Test against 14-ticket test set
- Validate behavior correctness and citation accuracy

## Success Metrics

### Performance Targets
- **Latency**: ≤ current 14.79s average
- **Error rate**: < 1% Stage 4 failures
- **Throughput**: Handle concurrent requests
- **Token efficiency**: Reduce usage by 20%

### Quality Targets
- **Accuracy**: Match current Stage 1-3 performance
- **Citations**: Maintain valid policy references
- **Behavior**: Correct escalate/reply decisions
- **Consistency**: Reproducible outputs

## Implementation Timeline

- **Week 1**: Basic ADK setup and agent creation
- **Week 2**: Integration with existing backend
- **Week 3**: Testing and validation
- **Week 4**: Documentation and deployment prep

## Conclusion

ADK integration offers significant benefits in maintainability, scalability, and developer experience. The tool-based approach (Option B) provides more flexibility while the multi-agent workflow (Option A) offers better structure and traceability. 

The migration will be done incrementally with comprehensive testing to ensure no regression in functionality or performance.
