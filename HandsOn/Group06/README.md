## Group Members

- **Emanuele Emilio Alberti**  
  GitHub: [emaalberti](https://github.com/emaalberti)

- **Leandro Duarte**  
  GitHub: [Leandr0Duar7e](https://github.com/Leandr0Duar7e)

- **Kada Ivana Haala**  
  GitHub: [bombaHKI](https://github.com/bombaHKI)

- **Ottavia Biagi**  
  GitHub: [OttaviaBiagi](https://github.com/OttaviaBiagi)

---

## Generate Full Dataset Locally

**Note:** This repository contains only sample data. The full RDF datasets are ~5GB each and cannot be versioned in Git. To reproduce the complete datasets:

### 1. Download Raw Data
Download GTFS data from [Mobility Database](https://mobilitydatabase.org/feeds/gtfs/mdb-2820) and extract the `.txt` files into:
```
Group06/data/raw/
```

Create the output directory:
```bash
mkdir -p data/processed
```

### 2. Setup Python Environment
```bash
cd scripts
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Process Data
```bash
python preprocessing.py        # Converts GTFS files to CSV
python assignment3.py         # Cleans data, fixes dates
python linking.py            # Creates local areas with Wikidata links
```

**Note:** The `linking.py` script can take ~1 hour to complete as it queries Wikidata for all 7,852 bus stops to gather geographic area information and owl:sameAs links.

### 4. Generate RDF Data
**Base dataset (no external links):**
```bash
cd ../morph-kgc
# Use default configuration.ini (points to madrid-bus-rml.rml)
python3 -m morph_kgc configuration.ini
```
Output: `rdf/madrid-bus-data.nt` (~5GB)

**With Wikidata links:**
Edit `morph-kgc/configuration.ini`:
- Set `mappings=../mappings/madrid-bus-rml-with-links.rml`
- Set `output_file=../rdf/madrid-bus-data-with-links.nt`
```bash
python3 -m morph_kgc configuration.ini
```
Output: `rdf/madrid-bus-data-with-links.nt` (~5GB)

### 5. Validate with SPARQL Queries

For quick validation and testing, we provide a **curated 100k-triple sample** that includes all entity types (LocalAreas, BusStops, Routes, Trips, StopTimes) and Wikidata links. This sample is specifically designed to return meaningful results for all verification queries.

**Using the sample dataset (recommended for testing):**
```bash
cd scripts
source .venv/bin/activate

# Validate with Wikidata links (100k sample)
python query_runner.py \
  --rdf ../rdf/madrid-bus-data-with-links-sample-100k.ttl \
  --sparql ../rdf/queries-with-links.sparql
```

**Using the full dataset (if generated):**
```bash
# Base dataset validation (5GB)
python query_runner.py

# Wikidata links validation (5GB)
python query_runner.py --links
```

The query runner:
- Loads RDF data using `rdflib.Graph`
- Executes SPARQL queries to verify data integrity
- Validates entity counts and relationships
- Checks owl:sameAs links for Wikidata integration

---

## Application Capability 

The `app-capability.py` script demonstrates how the quiz application could leverage RDF/Linked Data to retrieve contextual information:

```bash
cd scripts
source .venv/bin/activate
python app-capability.py
```

It queries the local RDF graph to find a bus stop's area, extracts the Wikidata Q-identifier from `owl:sameAs`, queries Wikidata's SPARQL endpoint for structured data, and fetches Wikipedia article text for quiz generation. 

---

## Production Deployment with Full RDF Dataset

For production use with the full 5GB dataset, we could **deploy a triple store** (e.g., Apache Jena Fuseki, Virtuoso, or GraphDB) and load the RDF data into it. The application can then query the SPARQL endpoint via HTTP without loading the entire dataset into memory.
