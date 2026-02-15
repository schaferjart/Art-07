# Model Strategy for Art + Technology Research

## Current Setup (OpenRouter)

| Model | Best For | Avoid For |
|-------|----------|-----------|
| **Kimi K2.5** (Primary) | Technical architecture, coding, math proportions, historical art pre-1900 | Contemporary Chinese political art, dissident artists, Taiwan/HK topics |
| **Claude Sonnet 4.5** | Contemporary art criticism, politically engaged work, sensitive cultural heritage, academic writing | - |
| **Gemini Flash** | Quick lookups, basic art facts, image-heavy research | Deep analysis, coding |

## When to Switch Models

### Use Kimi for:
- Blender/Python scripting
- Palladian proportions, classical architecture
- Technical art history (materials, techniques)
- General European art history

### Switch to Claude for:
- Ai Weiwei and contemporary Chinese dissident artists
- Art involving Taiwan, Hong Kong, Tibet, Xinjiang
- Cultural heritage destruction (e.g., Taliban, ISIS)
- Art criticism with political dimensions
- Anything touching 1989 Tiananmen Square

## How to Switch

Just tell me explicitly:
- "Use Claude for this" 
- "Switch to Western model"
- "This is politically sensitive"

Or I'll detect keywords and suggest the switch.

## Example Test Case

**Topic:** "Ai Weiwei's Sunflower Seeds at Tate Modern - cultural significance"

- **Kimi response:** Likely factual but may avoid political context of his detention, passport confiscation
- **Claude response:** Full context including political persecution, relationship to Chinese government

## European Compliance Note

- Claude (Anthropic) > Better GDPR alignment
- Kimi (Moonshot) > Data processed in China
- For sensitive client work: Default to Claude
