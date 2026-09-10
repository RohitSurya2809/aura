# Phase 3: Dynamic Model Discovery & Fallback

## Overview

Instead of hardcoding model names, Aura will:

1. **Discover available models** at startup from each provider (OpenRouter, Gemini)
2. **Rank models** by latency, speed, cost
3. **Store in ordered list** (priority queue)
4. **Auto-fallback** if primary model is unavailable

## Architecture

```python
class ModelRegistry:
    """Discovers and manages available models from all providers."""
    
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.models: list[AvailableModel] = []  # Ordered by speed/cost
        self.last_refresh: datetime = None
        self.refresh_ttl: timedelta = timedelta(hours=1)
    
    async def discover_models(self) -> list[AvailableModel]:
        """Query each provider for available models."""
        models = []
        
        # OpenRouter: Call /models endpoint
        models.extend(await self._discover_openrouter_models())
        
        # Gemini: Call ListModels
        models.extend(await self._discover_gemini_models())
        
        # Sort by: latency → cost → speed
        models.sort(key=lambda m: (m.latency_ms, m.cost_per_1m, -m.tokens_per_second))
        
        self.models = models
        self.last_refresh = datetime.now()
        return models
    
    async def get_best_available_model(self) -> AvailableModel:
        """Get the best available model, respecting TTL cache."""
        if self.last_refresh is None or \
           datetime.now() - self.last_refresh > self.refresh_ttl:
            await self.discover_models()
        
        for model in self.models:
            if await self._test_model_availability(model):
                return model
        
        raise NoAvailableModelsError("All models are currently unavailable")
    
    async def _test_model_availability(self, model: AvailableModel) -> bool:
        """Test if a model responds to a ping request."""
        try:
            response = await self._send_test_request(model)
            return response.status == 200
        except Exception:
            return False
```

## Data Models

```python
@dataclass
class AvailableModel:
    name: str
    provider: str  # "openrouter", "gemini"
    latency_ms: int  # Average response time
    tokens_per_second: float
    cost_per_1m: float  # Cost per 1M tokens
    context_window: int
    reasoning_tokens: bool
    supported_roles: list[str]
    last_tested: datetime
```

## Implementation Plan

### Step 1: Model Registry Service
- Create `ModelRegistry` class
- Implement `discover_models()` for each provider
- Cache results with TTL

### Step 2: Provider API Integration
- **OpenRouter**: `GET /api/v1/models` → parse available models
- **Gemini**: `genai.list_models()` → filter for generation capability

### Step 3: CLI Integration
```python
# At startup
registry = await ModelRegistry(router).discover_models()
best_model = await registry.get_best_available_model()

# In ConversationService
request = LLMRequest(
    messages=context,
    model=best_model.name,  # Auto-selected
)
```

### Step 4: Graceful Fallback
```python
try:
    response = await llm_service.generate(request)
except ProviderError:
    # Try next best model
    next_model = await registry.get_next_available_model()
    request.model = next_model.name
    response = await llm_service.generate(request)
```

## Benefits

✅ **Always uses best available model**  
✅ **No manual model selection needed**  
✅ **Automatic fallback on provider outage**  
✅ **Cost-aware routing** (prefer cheaper models)  
✅ **Latency-aware routing** (prefer faster models)  
✅ **Cached discovery** (refreshes hourly)

## Configuration

```env
# New in Phase 3
AURA_MODEL_DISCOVERY_ENABLED=true
AURA_MODEL_REFRESH_TTL_HOURS=1
AURA_MODEL_RANKING_STRATEGY=latency  # or "cost", "speed"
AURA_MODEL_MIN_CONTEXT_TOKENS=8000
```

## Testing

```python
# Unit tests
async def test_model_discovery():
    registry = ModelRegistry(mock_router)
    models = await registry.discover_models()
    assert len(models) > 0
    assert models[0].latency_ms <= models[1].latency_ms

async def test_fallback_to_next_model():
    registry = ModelRegistry(mock_router)
    await registry.discover_models()
    
    # First model fails
    models[0].availability = False
    
    best = await registry.get_best_available_model()
    assert best.name == models[1].name
```

## Timeline

- **Phase 3a**: Implement ModelRegistry + OpenRouter discovery
- **Phase 3b**: Add Gemini model discovery
- **Phase 3c**: Integrate with ConversationService
- **Phase 3d**: Add cost-based routing options

---

This feature will make Aura production-ready by handling model availability changes automatically.
