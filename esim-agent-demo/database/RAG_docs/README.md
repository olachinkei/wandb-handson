# eSIM Knowledge Base

This directory contains the knowledge base documents for the RAG (Retrieval-Augmented Generation) system.

## 📚 Documents

| File | Description | Topics Covered |
|------|-------------|----------------|
| `what_is_esim.md` | Introduction to eSIM | Definition, benefits, how it works, comparison with physical SIM |
| `device_compatibility.md` | Device support | Compatible devices (iPhone, Android, iPad, smartwatches), checking compatibility |
| `activation_setup.md` | Setup instructions | Activation steps for iPhone, Android, dual SIM setup |
| `managing_esims.md` | Management guide | Switching between eSIMs, managing multiple profiles, disabling/removing eSIMs |
| `troubleshooting.md` | Problem solving | Common issues and solutions, error messages, connectivity problems |
| `travel_tips.md` | Travel guidance | Before trip planning, usage tips, regional advice, data saving strategies |
| `security_privacy.md` | Security best practices | Device security, network security, privacy protection, scam awareness |
| `faq.md` | Frequently asked questions | Comprehensive Q&A covering all aspects of eSIM usage |
| `coverage_networks.md` | Network information | Coverage by region, network selection, speed expectations |

## 📊 Statistics

- **Total documents**: 9
- **Total lines**: ~4,000+
- **File format**: Markdown (.md)
- **Language**: English

## 🎯 Usage

These documents are uploaded to OpenAI Vector Store and used by the RAG Agent to answer user questions about eSIM technology.

### RAG Preparation

To upload these documents to the vector store:

```bash
uv run python rag_prep.py
```

This will:
1. Create/retrieve OpenAI Vector Store
2. Upload all markdown files
3. Wait for processing
4. Test retrieval functionality
5. Save vector store information

### Configuration

Vector store settings are defined in `config/config.yaml`:

```yaml
rag:
  vector_store:
    name: "esim-knowledge-base"
    chunk_size: 1000
    chunk_overlap: 200
```

## 📝 Content Guidelines

### Structure
- Clear headings and subheadings
- Bullet points for lists
- Tables for comparisons
- Code blocks for instructions

### Tone
- Professional yet friendly
- Easy to understand
- Technical but accessible
- Practical and actionable

### Coverage
- Comprehensive information
- Step-by-step instructions
- Troubleshooting guidance
- Regional considerations

## 🔍 Search Optimization

Documents are optimized for semantic search:
- Clear section headings
- Descriptive subheadings
- Relevant keywords
- Practical examples
- Cross-references

## 🚫 Excluded Files

The following files in this directory are NOT uploaded:
- `reference_page_list_delete_later.md` - Reference links only
- `README.md` - This documentation file

See `config/config.yaml` for the complete exclusion list.

## 🔄 Updates

To update the knowledge base:

1. Edit or add markdown files in this directory
2. Run `rag_prep.py` again to re-upload
3. Test with new queries
4. Update evaluations if content changed significantly

## 📊 Evaluation

The RAG Agent is evaluated on:
- **faithfulness**: Response accuracy to retrieved context
- **answer_relevancy**: Response relevance to user question
- **source_citation**: Proper file name references
- **out_of_scope_handling**: Declining non-eSIM questions
- **accuracy**: Overall correctness

See `evaluation/scenarios/` for test cases.

## 🔗 Related Files

- `../../rag_prep.py` - RAG preparation script
- `../../config/config.yaml` - RAG configuration
- `../../src/agents/rag_agent.py` - RAG Agent implementation (coming soon)
- `../../tests/test_rag_prep.py` - RAG preparation tests

