# Nanopublication Generator

A reusable system for generating nanopublications from JSON configuration files, designed for systematic reviews and research documentation.

## Quick Start

1. **Copy an example config** from `config/` and edit it for your paper/review
2. **Update the `CONFIG_FILE`** variable in the appropriate notebook
3. **Run the notebook** to generate `.trig` files
4. **Sign and publish** using `sign_and_publish_nanopub.ipynb`

## Directory Structure

```
nanopub_generator/
├── README.md                    # This file
├── nanopub_utils.py            # Shared utility functions
├── notebooks/
│   ├── create_aida_nanopub.ipynb      # AIDA sentence nanopublications
│   ├── create_software_nanopub.ipynb  # Software description nanopublications
│   ├── create_dataset_nanopub.ipynb   # Dataset nanopublications
│   ├── create_cito_nanopub.ipynb      # CiTO citation nanopublications
│   ├── create_comment_nanopub.ipynb   # Paper annotation nanopublications
│   ├── create_wikidata_nanopub.ipynb  # Wikidata statement nanopublications
│   └── sign_and_publish_nanopub.ipynb # Sign & publish to Nanopub network
├── config/
│   └── vbae208_*.json          # Example configs (use as templates)
└── output/
    └── {type}/                 # Generated nanopubs by type
```

---

## Configuration for Your Systematic Review

All nanopublications are generated from JSON configuration files. **Nothing is hardcoded** - you control everything through your config files.

### Complete Config Structure

```json
{
  "metadata": {
    "source_paper": {
      "title": "Your Paper Title",
      "doi": "10.xxxx/xxxxx"
    },
    "creator_orcid": "0000-0002-XXXX-XXXX",
    "creator_name": "Your Name",
    "is_part_of": {
      "uri": "https://w3id.org/np/YOUR-REVIEW-NANOPUB-ID/your-review-slug",
      "label": "Your Systematic Review Title"
    }
  },
  "nanopublications": [
    {
      "id": "unique_id_for_output_file",
      // ... type-specific fields
    }
  ]
}
```

### Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `source_paper.title` | Title of the paper being annotated | "QOMIC: Quantum Optimization..." |
| `source_paper.doi` | DOI of the paper | "10.1093/bioadv/vbae208" |
| `creator_orcid` | Your ORCID (without https prefix) | "0000-0002-1784-2920" |
| `creator_name` | Your name for attribution | "Anne Fouilloux" |
| `is_part_of.uri` | Nanopub URI of your systematic review | See below |
| `is_part_of.label` | Human-readable title of your review | "My Review - Systematic Review" |

### Linking to Your Systematic Review

The `is_part_of` field links generated nanopublications to your systematic review. The location of this link depends on the nanopublication type:

**Entity-level linking (in assertion graph):**
- **AIDA**: Links the AIDA sentence entity to the review
- **Software**: Links the software entity to the review
- **Dataset**: Links the dataset entity to the review
- **Comment**: Links the annotated paper to the review

**Nanopub-level linking (in pubinfo graph):**
- **CiTO**: Links the nanopublication itself to the review
- **Wikidata**: Links the nanopublication itself to the review

This distinction matters for SPARQL queries:
- Assertion-level: "Find all AIDA sentences that are part of review X"
- Pubinfo-level: "Find all nanopubs that are part of review X"

**Example for different reviews:**

```json
// Review 1: Quantum Computing for Biodiversity
"is_part_of": {
  "uri": "https://w3id.org/np/RAvk9pmoZ2IberoDe7zUWV0bVithiy6CnbSG5y06YuKM0/quantum-computing-applications-for-biodiversity-re",
  "label": "Quantum Computing Applications for Biodiversity Research - Systematic Review"
}

// Review 2: Climate Change Impacts
"is_part_of": {
  "uri": "https://w3id.org/np/RAxxxxxxxxxxxxx/climate-change-biodiversity",
  "label": "Climate Change Impacts on Biodiversity - Systematic Review"
}

// Review 3: Machine Learning in Ecology
"is_part_of": {
  "uri": "https://w3id.org/np/RAyyyyyyyyyyyyy/ml-ecology-review",
  "label": "Machine Learning Applications in Ecology - Systematic Review"
}
```

**Generated output includes:**
```turtle
sub:pubinfo {
  # Human-readable label for display in Nanodash
  <https://w3id.org/np/.../your-review> 
    nt:hasLabelFromApi "Your Systematic Review Title" .

  this: 
    dct:isPartOf <https://w3id.org/np/.../your-review> ;
    ...
}
```

---

## Workflow: Adding a New Paper to Your Review

### Step 1: Create Config Files

For each paper in your systematic review, create config files:

```
config/
├── paper1_aida.json
├── paper1_cito.json
├── paper1_comment.json
├── paper2_aida.json
├── paper2_cito.json
└── ...
```

### Step 2: Edit Metadata

In each config file, set your review information:

```json
{
  "metadata": {
    "source_paper": {
      "title": "Paper Title from Your Review",
      "doi": "10.xxxx/xxxxx"
    },
    "creator_orcid": "YOUR-ORCID",
    "creator_name": "Your Name",
    "is_part_of": {
      "uri": "YOUR-REVIEW-NANOPUB-URI",
      "label": "Your Review Title"
    }
  },
  "nanopublications": [...]
}
```

### Step 3: Run Notebooks

1. Open the appropriate notebook (e.g., `create_aida_nanopub.ipynb`)
2. Change `CONFIG_FILE` to your config:
   ```python
   CONFIG_FILE = "../config/paper1_aida.json"
   ```
3. Run all cells
4. Check output in `output/{type}/`

### Step 4: Sign and Publish

1. Open `sign_and_publish_nanopub.ipynb`
2. Set input path:
   ```python
   INPUT_PATH = "../output/aida/"  # or specific file
   ```
3. Run to sign and publish to the Nanopub network

---

## Nanopublication Types

### 1. AIDA Sentences (`create_aida_nanopub.ipynb`)

Express scientific claims as AIDA sentences:
- **A**tomic: One thought per sentence
- **I**ndependent: Stands alone without external references  
- **D**eclarative: Complete sentence that could be true or false
- **A**bsolute: Core claim without uncertainty markers

```json
{
  "id": "aida_claim_01",
  "aida_sentence": "Quantum algorithms outperform classical methods for network motif detection.",
  "related_publication": "10.1093/bioadv/vbae208",
  "topics": [
    {"uri": "http://www.wikidata.org/entity/Q47536", "label": "quantum computing"},
    {"uri": "http://www.wikidata.org/entity/Q17137535", "label": "network motif"}
  ]
}
```

### 2. Software (`create_software_nanopub.ipynb`)

Document research software:

```json
{
  "id": "software_mytool",
  "title": "My Research Tool",
  "repository_uri": "https://github.com/user/repo",
  "license_uri": "https://w3id.org/np/...",
  "related_publications": ["10.xxxx/xxxxx"],
  "related_resources": ["https://doi.org/10.xxxx/dataset"]
}
```

### 3. Dataset (`create_dataset_nanopub.ipynb`)

Document datasets following FAIR principles:

```json
{
  "id": "dataset_mydata",
  "label": "My Dataset Name",
  "description": "Description of the dataset",
  "dataset_uri": "https://doi.org/10.xxxx/dataset",
  "access_url": "https://example.com/download"
}
```

### 4. CiTO Citations (`create_cito_nanopub.ipynb`)

Create typed citations:

```json
{
  "id": "cito_paper_refs",
  "citing_article": "10.1093/bioadv/vbae208",
  "citations": [
    {"cited_article": "10.xxxx/xxxxx", "citation_type": "cito:usesDataFrom"},
    {"cited_article": "10.yyyy/yyyyy", "citation_type": "cito:usesMethodIn"}
  ]
}
```

Available citation types: `cito:cites`, `cito:usesDataFrom`, `cito:usesMethodIn`, `cito:extends`, `cito:confirms`, `cito:citesAsDataSource`, `cito:obtainsBackgroundFrom`

### 5. Comments/Annotations (`create_comment_nanopub.ipynb`)

Annotate papers with quotations:

```json
{
  "id": "comment_finding_01",
  "paper_doi": "10.1093/bioadv/vbae208",
  "quotation": "Exact quote from the paper...",
  "comment": "Your interpretation and relevance to the review..."
}
```

### 6. Wikidata Statements (`create_wikidata_nanopub.ipynb`)

Express structured relationships:

```json
{
  "id": "wikidata_software_type",
  "statements": [
    {
      "subject": {"uri": "https://github.com/user/repo", "label": "My Tool"},
      "property": {"id": "P31", "label": "instance of"},
      "object": {"id": "Q7397", "label": "software"}
    }
  ]
}
```

---

## Publishing Nanopublications

### Prerequisites

1. Install the nanopub library:
   ```bash
   pip install nanopub
   ```

2. Set up your profile (links to your ORCID):
   ```bash
   np setup
   ```

### Using the Sign & Publish Notebook

```python
# Configuration options
INPUT_PATH = "../output/aida/"   # Directory, single file, or list
PUBLISH = True                    # False = sign only, don't publish
USE_TEST_SERVER = True            # True = test network (recommended first)
```

### Alternative Methods

1. **Nanodash Web Interface**: Upload `.trig` files to https://nanodash.knowledgepixels.com/
2. **Command Line**:
   ```bash
   np sign output/aida/aida_claim_01.trig
   np publish signed.aida_claim_01.trig
   ```

---

## Template URIs

Each nanopublication type references a Nanodash template:

| Type | Template URI |
|------|-------------|
| AIDA | `https://w3id.org/np/RALmXhDw3rHcMveTgbv8VtWxijUHwnSqhCmtJFIPKWVaA` |
| Software | `https://w3id.org/np/RABBzVTxosLGT4YBCfdfNd6LyuOOTe2EVOTtWJMyOoZHk` |
| CiTO | `https://w3id.org/np/RAX_4tWTyjFpO6nz63s14ucuejd64t2mK3IBlkwZ7jjLo` |
| Comment | `https://w3id.org/np/RA24onqmqTMsraJ7ypYFOuckmNWpo4Zv5gsLqhXt7xYPU` |
| Wikidata | `http://purl.org/np/RA95PFSIiN6-B5qh-a89s78Rmna22y2Yy7rGHEI9R6Vws` |

---

## Requirements

- Python 3.8+
- Jupyter Notebook/Lab
- For publishing: `pip install nanopub`

No additional Python packages required for generation - uses only standard library modules.

## License

MIT License - Free to use and modify.
