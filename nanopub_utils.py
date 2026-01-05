"""
Nanopublication Utilities
Common functions for generating nanopublications from JSON configurations.
"""

import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Standard prefixes used in nanopublications
PREFIXES = {
    "np": "http://www.nanopub.org/nschema#",
    "dct": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "prov": "http://www.w3.org/ns/prov#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "orcid": "https://orcid.org/",
    "npx": "http://purl.org/nanopub/x/",
    "nt": "https://w3id.org/np/o/ntemplate/",
    "cito": "http://purl.org/spar/cito/",
    "fabio": "http://purl.org/spar/fabio/",
    "schema": "https://schema.org/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "hycl": "http://purl.org/petapico/o/hycl#",
    "aida": "http://purl.org/aida/",
    "wd": "http://www.wikidata.org/entity/",
    "wdt": "http://www.wikidata.org/prop/direct/",
    "dcmitype": "http://purl.org/dc/dcmitype/",
    "fdof": "https://w3id.org/fdof/ontology#",
    "fair": "https://w3id.org/fair/fip/terms/",
    "dcat": "https://www.w3.org/ns/dcat#",
    "geo": "http://www.opengis.net/ont/geosparql#",
    "pico": "http://data.cochrane.org/ontologies/pico/",
}


def load_config(config_path: str) -> Dict[str, Any]:
    """Load JSON configuration file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_nanopub_uri() -> str:
    """Generate a placeholder nanopub URI (will be replaced on actual publishing)."""
    unique_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:43]
    return f"https://w3id.org/np/RA{unique_id}"


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def escape_literal(text: str) -> str:
    """Escape special characters in literals for TriG."""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')


def format_prefixes(prefixes: Dict[str, str]) -> str:
    """Format prefix declarations for TriG."""
    lines = []
    for prefix, uri in sorted(prefixes.items()):
        lines.append(f"@prefix {prefix}: <{uri}> .")
    return "\n".join(lines)


def make_uri(value: str, prefix: str = None) -> str:
    """Format a value as a URI reference."""
    if value.startswith("http://") or value.startswith("https://"):
        return f"<{value}>"
    elif prefix:
        return f"{prefix}:{value}"
    else:
        return f"<{value}>"


def make_literal(value: str, datatype: str = None, lang: str = None) -> str:
    """Format a value as an RDF literal."""
    escaped = escape_literal(str(value))
    if datatype:
        return f'"{escaped}"^^{datatype}'
    elif lang:
        return f'"{escaped}"@{lang}'
    else:
        return f'"{escaped}"'


def generate_pubinfo_graph(
    nanopub_uri: str,
    sub_prefix: str,
    creator_orcid: str,
    creator_name: str,
    label: str,
    template_uri: str = None,
    provenance_template_uri: str = None,
    pubinfo_template_uris: List[str] = None,
    nanopub_types: List[str] = None,
    introduces_uri: str = None,
    wikidata_labels: Dict[str, str] = None,
    supersedes: str = None,
    is_part_of: Dict[str, str] = None
) -> str:
    """Generate the publication info graph matching Nanodash format."""
    timestamp = get_timestamp()
    
    lines = [f"{sub_prefix}:pubinfo {{"]
    
    # Add Wikidata label lookups first (if any)
    if wikidata_labels:
        for wd_uri, wd_label in wikidata_labels.items():
            lines.append(f"  <{wd_uri}> nt:hasLabelFromApi {make_literal(wd_label)} .")
        lines.append("")
    
    # Add label for is_part_of URI (systematic review)
    if is_part_of and is_part_of.get('label'):
        lines.append(f"  <{is_part_of['uri']}> nt:hasLabelFromApi {make_literal(is_part_of['label'])} .")
        lines.append("")
    
    # Creator info
    lines.append(f"  orcid:{creator_orcid} foaf:name {make_literal(creator_name)} .")
    lines.append("")
    
    # Main nanopub metadata
    lines.append(f"  this: dct:created \"{timestamp}\"^^xsd:dateTime ;")
    lines.append(f"    dct:creator orcid:{creator_orcid} ;")
    lines.append(f"    dct:license <https://creativecommons.org/licenses/by/4.0/> ;")
    
    # Nanopub types
    if nanopub_types:
        types_str = ", ".join([f"<{t}>" for t in nanopub_types])
        lines.append(f"    npx:hasNanopubType {types_str} ;")
    
    # Introduces (the main subject)
    if introduces_uri:
        lines.append(f"    npx:introduces <{introduces_uri}> ;")
    
    # Supersedes
    if supersedes:
        lines.append(f"    npx:supersedes <{supersedes}> ;")
    
    # Is part of (link to systematic review or project)
    if is_part_of and is_part_of.get('uri'):
        lines.append(f"    <http://purl.org/dc/terms/isPartOf> <{is_part_of['uri']}> ;")
    
    lines.append(f"    npx:wasCreatedAt <https://nanodash.knowledgepixels.com/> ;")
    lines.append(f"    rdfs:label {make_literal(label)} ;")
    
    # Template references
    if provenance_template_uri:
        lines.append(f"    nt:wasCreatedFromProvenanceTemplate <{provenance_template_uri}> ;")
    
    if pubinfo_template_uris:
        templates_str = ",\n      ".join([f"<{t}>" for t in pubinfo_template_uris])
        lines.append(f"    nt:wasCreatedFromPubinfoTemplate {templates_str} ;")
    
    if template_uri:
        # Remove trailing semicolon from last line and add this as final
        lines[-1] = lines[-1].rstrip(" ;")
        if not lines[-1].endswith(" ."):
            lines[-1] += " ;"
        lines.append(f"    nt:wasCreatedFromTemplate <{template_uri}> .")
    else:
        # Convert last semicolon to period
        lines[-1] = lines[-1].rstrip(" ;") + " ."
    
    lines.append("}")
    
    return "\n".join(lines)


def generate_provenance_graph(sub_prefix: str, creator_orcid: str) -> str:
    """Generate the provenance graph."""
    return f"""{sub_prefix}:provenance {{
  {sub_prefix}:assertion prov:wasAttributedTo orcid:{creator_orcid} .
}}"""


def generate_head_graph(sub_prefix: str) -> str:
    """Generate the head graph."""
    return f"""{sub_prefix}:Head {{
  this: a np:Nanopublication ;
    np:hasAssertion {sub_prefix}:assertion ;
    np:hasProvenance {sub_prefix}:provenance ;
    np:hasPublicationInfo {sub_prefix}:pubinfo .
}}"""


def save_nanopub(content: str, output_path: str) -> str:
    """Save nanopublication to file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return output_path


def validate_required_fields(config: Dict, required: List[str]) -> None:
    """Validate that required fields are present in config."""
    missing = [f for f in required if f not in config or not config[f]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


class NanopubGenerator:
    """Base class for nanopublication generators."""
    
    # Default template URIs used by Nanodash
    PROVENANCE_TEMPLATE = "https://w3id.org/np/RA7lSq6MuK_TIC6JMSHvLtee3lpLoZDOqLJCLXevnrPoU"
    PUBINFO_TEMPLATES = [
        "https://w3id.org/np/RA0J4vUn_dekg-U1kK3AOEt02p9mT2WO03uGxLDec1jLw",
        "https://w3id.org/np/RAukAcWHRDlkqxk7H2XNSegc1WnHI569INvNr-xdptDGI"
    ]
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.nanopub_uri = generate_nanopub_uri()
        self.sub_prefix = "sub"
        self.used_prefixes = set(["np", "dct", "rdf", "rdfs", "xsd", "prov", "foaf", "orcid", "npx", "nt"])
        # For collecting Wikidata labels to include in pubinfo
        self.wikidata_labels = {}
        # For tracking the main introduced URI
        self.introduces_uri = None
        # For tracking nanopub types
        self.nanopub_types = []
    
    def add_prefix(self, prefix: str):
        """Add a prefix to the used prefixes set."""
        self.used_prefixes.add(prefix)
    
    def add_wikidata_label(self, uri: str, label: str):
        """Add a Wikidata entity label for inclusion in pubinfo."""
        if uri.startswith("http://www.wikidata.org/entity/"):
            self.wikidata_labels[uri] = label
    
    def set_introduces(self, uri: str):
        """Set the main URI being introduced by this nanopub."""
        self.introduces_uri = uri
    
    def add_nanopub_type(self, type_uri: str):
        """Add a nanopub type."""
        if type_uri not in self.nanopub_types:
            self.nanopub_types.append(type_uri)
    
    def get_prefixes_block(self) -> str:
        """Get the prefixes block for the nanopublication."""
        prefix_lines = [f"@prefix this: <{self.nanopub_uri}> ."]
        prefix_lines.append(f"@prefix {self.sub_prefix}: <{self.nanopub_uri}/> .")
        
        for prefix in sorted(self.used_prefixes):
            if prefix in PREFIXES:
                prefix_lines.append(f"@prefix {prefix}: <{PREFIXES[prefix]}> .")
        
        return "\n".join(prefix_lines)
    
    def generate_assertion(self) -> str:
        """Generate the assertion graph. Override in subclasses."""
        raise NotImplementedError
    
    def generate(self) -> str:
        """Generate the complete nanopublication."""
        # Get creator info
        creator_orcid = self.config.get("creator_orcid", "0000-0000-0000-0000")
        creator_name = self.config.get("creator_name", "Unknown")
        template_uri = self.config.get("template_uri")
        supersedes = self.config.get("supersedes")
        is_part_of = self.config.get("is_part_of")  # Link to systematic review with label
        
        # Generate assertion first (may update label and other config)
        assertion = self.generate_assertion()
        
        # Get label AFTER assertion (subclasses may set it in generate_assertion)
        label = self.config.get("label", "Nanopublication")
        
        # Generate all other parts
        prefixes = self.get_prefixes_block()
        head = generate_head_graph(self.sub_prefix)
        provenance = generate_provenance_graph(self.sub_prefix, creator_orcid)
        pubinfo = generate_pubinfo_graph(
            self.nanopub_uri, 
            self.sub_prefix, 
            creator_orcid, 
            creator_name,
            label, 
            template_uri=template_uri,
            provenance_template_uri=self.PROVENANCE_TEMPLATE,
            pubinfo_template_uris=self.PUBINFO_TEMPLATES,
            nanopub_types=self.nanopub_types if self.nanopub_types else None,
            introduces_uri=self.introduces_uri,
            wikidata_labels=self.wikidata_labels if self.wikidata_labels else None,
            supersedes=supersedes,
            is_part_of=is_part_of
        )
        
        return f"{prefixes}\n\n{head}\n\n{assertion}\n\n{provenance}\n\n{pubinfo}\n"
